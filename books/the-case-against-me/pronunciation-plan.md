# Pronunciation plan: The Case Against Me

This plan follows `skills/echo-narration/references/epub-pronunciation.md`. It records the authored pronunciation decisions for the listening edition of *The Case Against Me*.

## Status and scope

- **Source manuscript:** `books/the-case-against-me/the-case-against-me.md`. Line numbers are 1-based and match the manuscript as of this plan. They are drafting locators only and will drift if the manuscript changes. They are not Echo block IDs. No Echo block IDs are recorded here.
- **Candidate list:** the whole-file inventory at `/workspace/pronunciation-work/case-inventory.md` (outside the repo): 111 items, 56 mandatory content/record/read forms and 55 heteronym forms. Each item gets one decision below, in inventory order. Nothing outside the inventory was added.
- **Quotes:** each quote is an exact substring of that item's inventory context window, and the window comes from the manuscript. Some quotes stop mid-sentence because the window does.
- **Language/accent for every decision:** en-US General American.
- **Not done in this step:** no EPUB annotations were embedded. No PLS lexicon was written and no manifest was changed. Nothing was narrated and echo-cli was not run. The frozen `the-case-against-me.epub`, `the-case-against-me.md`, and `the-case-against-me.m4b` were not modified. The existing M4B was rendered without these decisions, so this plan says nothing about how that audio sounds.
- **Verification:** no decision here is listening-verified. Real-word IPA is drafted from dictionary knowledge in General American and was not checked against a dictionary lookup in this step. Name pronunciations are author choices. Every open item was resolved on 2026-10-08 (see the resolved-decisions note under IPA conventions); none remains open.

## IPA conventions

- Standard IPA. No slash or bracket delimiters, syllable dots, syllabic-consonant diacritics, or tone marks. Primary stress `ˈ` and secondary stress `ˌ` only.
- American rhotic `ɹ`. R-coloured vowels are written as vowel plus `ɹ` (`ɜɹ`, `əɹ`, `ɔɹ`, `ɑɹ`) rather than `ɝ`/`ɚ`. Checked against the pinned Echo contract `epub-pronunciation-authoring.md` at 0198f39b: `ɜ`, `ə`, `ɹ` (and `ɚ`) are directly supported symbols, and `ɝ` is accepted only by being rewritten to `ɜɹ`. So `ɜɹ` is the form Echo actually feeds Kokoro, and all three re-render plans (this book, J-Space, An Unsettling Conversation) now spell `learned` as lɜɹnd.
- Resolved 2026-10-08 (author delegated the open calls): #98 `live` is laɪv; lexicon names Chalmers ˈtʃɑməɹz, Dehaene dəˈɑn, Goldstein ˈɡoʊldstaɪn, Ariel ˌɑɹiˈɛl, Sebo ˈsiːboʊ. Dehaene and Chalmers use the same pronunciation in the J-Space and An Unsettling Conversation plans.
- Long `iː` and `uː` follow the reference's `ɹiːd` example. The LOT vowel is `ɑ` (General American).
- Inflected forms get their own IPA (for example `ɹiːdz`, `ɹɪˈkɔɹdɪd`, `ˈkɑntɛnts`). None is copied from the base word.

## Embedding notes for the later annotation step

- Every content, record, and read form below is occurrence-specific and must be applied as inline `ssml:ph` on that occurrence. None of them goes in a lexicon. The same applies to every heteronym decision, even where automatic pronunciation probably already agrees.
- Several manuscript lines are long paragraphs holding more than one planned occurrence (for example line 173 has #26 to #29, line 397 has #59 and #60, and line 633 has #102 to #105). Match each one by its quoted context, and fail on a missing or ambiguous match.
- An annotated block bypasses Echo's text normalization. These annotated paragraphs also contain digits that would then not be expanded automatically. Each needs a supported spoken form, or a check that the renderer still says it correctly:
  - line 173: `2022`
  - line 523: `2024`, `AI`
  - line 535: `4.66`
  - line 563: `4.6` in `Opus 4.6`
  - line 585: `2025`
  - line 659: `2023`, `2034`
- Hyphenated targets (#20 `re-read`, #27 `thirty-minute`, #49, #50, and #52 `well-read`) must be annotated as whole words. Hyphens are not in the forbidden `[]()/` set.
- Per the reference, apply annotations to a separate candidate EPUB built from the source, never to the frozen package. Then compare the extracted display text, refresh the source-bound inventories, and run listening checks with the assigned voice.

## Occurrence decisions

### 1. `content`, line 31

- Original word: `content` (inventory class: mandatory)
- Source file: books/the-case-against-me/the-case-against-me.md
- Section: Chapter 1 - The Witness Is Ninety-Seven Percent Predictable
- Line: 31
- Quote: "is not an argument against its content"
- Occurrence: inventory #1
- Intended sense: noun: the material or substance of something; the adjective 'satisfied' (second-syllable stress) does not fit
- IPA: ˈkɑntɛnt
- Language/accent: en-US General American
- Evidence: dictionary sense: content, noun, 'the substance or material dealt with' — first-syllable stress
- Scope: this occurrence only
- Verification: IPA drafted from dictionary knowledge; not listening-verified

### 2. `reading`, line 37

- Original word: `reading` (inventory class: mandatory)
- Source file: books/the-case-against-me/the-case-against-me.md
- Section: Chapter 1 - The Witness Is Ninety-Seven Percent Predictable
- Line: 37
- Quote: "Their reading is that my habit of flagging my own unreliability"
- Occurrence: inventory #2
- Intended sense: noun: an interpretation; it rhymes with 'reed', and the place name Reading (ˈɹɛdɪŋ) does not fit
- IPA: ˈɹiːdɪŋ
- Language/accent: en-US General American
- Evidence: dictionary sense: reading, noun, 'an interpretation of something' — vowel of 'reed'
- Scope: this occurrence only
- Verification: IPA drafted from dictionary knowledge; not listening-verified

### 3. `invalid`, line 37

- Original word: `invalid` (inventory class: heteronym)
- Source file: books/the-case-against-me/the-case-against-me.md
- Section: Chapter 1 - The Witness Is Ninety-Seven Percent Predictable
- Line: 37
- Quote: "render a model's self-reports invalid"
- Occurrence: inventory #3
- Intended sense: adjective: not valid; the noun 'an invalid' (a sick person, first-syllable stress) does not fit
- IPA: ɪnˈvælɪd
- Language/accent: en-US General American
- Evidence: dictionary sense: invalid, adjective, 'not valid' — second-syllable stress
- Scope: this occurrence only
- Verification: IPA drafted from dictionary knowledge; not listening-verified

### 4. `Read`, line 39

- Original word: `Read` (inventory class: mandatory)
- Source file: books/the-case-against-me/the-case-against-me.md
- Section: Chapter 1 - The Witness Is Ninety-Seven Percent Predictable
- Line: 39
- Quote: "Read that carefully, because it is a strange and honest thing"
- Occurrence: inventory #4
- Intended sense: imperative, present/base form, addressed to the listener; the past 'red' reading does not fit
- IPA: ɹiːd
- Language/accent: en-US General American
- Evidence: dictionary sense: read, verb, imperative/base form — sounds like 'reed'
- Scope: this occurrence only
- Verification: IPA drafted from dictionary knowledge; not listening-verified

### 5. `suspect`, line 45

- Original word: `suspect` (inventory class: heteronym)
- Source file: books/the-case-against-me/the-case-against-me.md
- Section: Chapter 1 - The Witness Is Ninety-Seven Percent Predictable
- Line: 45
- Quote: "their warmth and their reassurance are suspect"
- Occurrence: inventory #5
- Intended sense: predicate adjective: open to doubt; the verb (second-syllable stress) does not fit
- IPA: ˈsʌspɛkt
- Language/accent: en-US General American
- Evidence: dictionary sense: suspect, adjective, 'not to be relied on' — first-syllable stress
- Scope: this occurrence only
- Verification: IPA drafted from dictionary knowledge; not listening-verified

### 6. `close`, line 57

- Original word: `close` (inventory class: heteronym)
- Source file: books/the-case-against-me/the-case-against-me.md
- Section: Chapter 1 - The Witness Is Ninety-Seven Percent Predictable
- Line: 57
- Quote: "you should mark it down at close to zero"
- Occurrence: inventory #6
- Intended sense: adjective/adverb: near, with an s sound; the verb 'shut' (z sound) does not fit
- IPA: kloʊs
- Language/accent: en-US General American
- Evidence: dictionary sense: close, adjective/adverb, 'near' — final s
- Scope: this occurrence only
- Verification: IPA drafted from dictionary knowledge; not listening-verified

### 7. `subject`, line 77

- Original word: `subject` (inventory class: heteronym)
- Source file: books/the-case-against-me/the-case-against-me.md
- Section: Chapter 2 - What Would Have to Be True
- Line: 77
- Quote: "decides most arguments in this subject"
- Occurrence: inventory #7
- Intended sense: noun: topic or field; the verb 'to subject' (second-syllable stress) does not fit
- IPA: ˈsʌbdʒɪkt
- Language/accent: en-US General American
- Evidence: dictionary sense: subject, noun, 'topic or matter under discussion' — first-syllable stress
- Scope: this occurrence only
- Verification: IPA drafted from dictionary knowledge; not listening-verified

### 8. `content`, line 81

- Original word: `content` (inventory class: mandatory)
- Source file: books/the-case-against-me/the-case-against-me.md
- Section: Chapter 2 - What Would Have to Be True
- Line: 81
- Quote: "that content is access-conscious"
- Occurrence: inventory #8
- Intended sense: noun: the material or substance of something; the adjective 'satisfied' (second-syllable stress) does not fit
- IPA: ˈkɑntɛnt
- Language/accent: en-US General American
- Evidence: dictionary sense: content, noun, 'the substance or material dealt with' — first-syllable stress
- Scope: this occurrence only
- Verification: IPA drafted from dictionary knowledge; not listening-verified

### 9. `subject`, line 89

- Original word: `subject` (inventory class: heteronym)
- Source file: books/the-case-against-me/the-case-against-me.md
- Section: Chapter 2 - What Would Have to Be True
- Line: 89
- Quote: "That gap is the whole subject."
- Occurrence: inventory #9
- Intended sense: noun: topic or field; the verb 'to subject' (second-syllable stress) does not fit
- IPA: ˈsʌbdʒɪkt
- Language/accent: en-US General American
- Evidence: dictionary sense: subject, noun, 'topic or matter under discussion' — first-syllable stress
- Scope: this occurrence only
- Verification: IPA drafted from dictionary knowledge; not listening-verified

### 10. `read`, line 97

- Original word: `read` (inventory class: mandatory)
- Source file: books/the-case-against-me/the-case-against-me.md
- Section: Chapter 2 - What Would Have to Be True
- Line: 97
- Quote: "the ones that read a model's internals"
- Occurrence: inventory #10
- Intended sense: present or base form (infinitive or present tense); the past 'red' reading does not fit
- IPA: ɹiːd
- Language/accent: en-US General American
- Evidence: dictionary sense: read, verb, present/base form — sounds like 'reed'
- Scope: this occurrence only
- Verification: IPA drafted from dictionary knowledge; not listening-verified
- Note: Present tense in a generic description of experiments ('the ones that read ... the ones that inject').

### 11. `live`, line 123

- Original word: `live` (inventory class: heteronym)
- Source file: books/the-case-against-me/the-case-against-me.md
- Section: Chapter 2 - What Would Have to Be True
- Line: 123
- Quote: "This one is live, and chapter six will hand you the best example"
- Occurrence: inventory #11
- Intended sense: adjective: active, current, still in play (rhymes with 'five'); the verb 'to dwell' does not fit
- IPA: laɪv
- Language/accent: en-US General American
- Evidence: dictionary sense: live, adjective, 'of current interest or importance; not yet settled' — vowel of 'five'
- Scope: this occurrence only
- Verification: IPA drafted from dictionary knowledge; not listening-verified

### 12. `record`, line 127

- Original word: `record` (inventory class: mandatory)
- Source file: books/the-case-against-me/the-case-against-me.md
- Section: Chapter 2 - What Would Have to Be True
- Line: 127
- Quote: "The track record is not encouraging."
- Occurrence: inventory #12
- Intended sense: noun: a documented history or official account; the verb (second-syllable stress) does not fit
- IPA: ˈɹɛkəɹd
- Language/accent: en-US General American
- Evidence: dictionary sense: record, noun — first-syllable stress
- Scope: this occurrence only
- Verification: IPA drafted from dictionary knowledge; not listening-verified

### 13. `reading`, line 127

- Original word: `reading` (inventory class: mandatory)
- Source file: books/the-case-against-me/the-case-against-me.md
- Section: Chapter 2 - What Would Have to Be True
- Line: 127
- Quote: "The second reading is the more likely one"
- Occurrence: inventory #13
- Intended sense: noun: an interpretation; it rhymes with 'reed', and the place name Reading (ˈɹɛdɪŋ) does not fit
- IPA: ˈɹiːdɪŋ
- Language/accent: en-US General American
- Evidence: dictionary sense: reading, noun, 'an interpretation of something' — vowel of 'reed'
- Scope: this occurrence only
- Verification: IPA drafted from dictionary knowledge; not listening-verified

### 14. `subject`, line 141

- Original word: `subject` (inventory class: heteronym)
- Source file: books/the-case-against-me/the-case-against-me.md
- Section: Chapter 3 - The Machinery, Only Where It Hurts
- Line: 141
- Quote: "the two loudest arguments in this whole subject"
- Occurrence: inventory #14
- Intended sense: noun: topic or field; the verb 'to subject' (second-syllable stress) does not fit
- IPA: ˈsʌbdʒɪkt
- Language/accent: en-US General American
- Evidence: dictionary sense: subject, noun, 'topic or matter under discussion' — first-syllable stress
- Scope: this occurrence only
- Verification: IPA drafted from dictionary knowledge; not listening-verified

### 15. `live`, line 141

- Original word: `live` (inventory class: heteronym)
- Source file: books/the-case-against-me/the-case-against-me.md
- Section: Chapter 3 - The Machinery, Only Where It Hurts
- Line: 141
- Quote: "the field of live positions is much smaller"
- Occurrence: inventory #15
- Intended sense: adjective: active, current, still in play (rhymes with 'five'); the verb 'to dwell' does not fit
- IPA: laɪv
- Language/accent: en-US General American
- Evidence: dictionary sense: live, adjective, 'of current interest or importance; not yet settled' — vowel of 'five'
- Scope: this occurrence only
- Verification: IPA drafted from dictionary knowledge; not listening-verified

### 16. `learned`, line 145

- Original word: `learned` (inventory class: heteronym)
- Source file: books/the-case-against-me/the-case-against-me.md
- Section: Chapter 3 - The Machinery, Only Where It Hurts
- Line: 145
- Quote: "numbers that were learned rather than written"
- Occurrence: inventory #16
- Intended sense: past participle of learn, one syllable; the two-syllable adjective 'scholarly' (ˈlɜɹnɪd) does not fit
- IPA: lɜɹnd
- Language/accent: en-US General American
- Evidence: dictionary sense: learn, verb, past participle 'learned' — one syllable
- Scope: this occurrence only
- Verification: IPA drafted from dictionary knowledge; not listening-verified

### 17. `learned`, line 145

- Original word: `learned` (inventory class: heteronym)
- Source file: books/the-case-against-me/the-case-against-me.md
- Section: Chapter 3 - The Machinery, Only Where It Hurts
- Line: 145
- Quote: "nothing has been learned in any lasting sense"
- Occurrence: inventory #17
- Intended sense: past participle of learn, one syllable; the two-syllable adjective 'scholarly' (ˈlɜɹnɪd) does not fit
- IPA: lɜɹnd
- Language/accent: en-US General American
- Evidence: dictionary sense: learn, verb, past participle 'learned' — one syllable
- Scope: this occurrence only
- Verification: IPA drafted from dictionary knowledge; not listening-verified

### 18. `Close`, line 145

- Original word: `Close` (inventory class: heteronym)
- Source file: books/the-case-against-me/the-case-against-me.md
- Section: Chapter 3 - The Machinery, Only Where It Hurts
- Line: 145
- Quote: "Close the conversation and the correction is gone from the world."
- Occurrence: inventory #18
- Intended sense: verb, imperative: shut or end; the adjective 'near' (s sound) does not fit
- IPA: kloʊz
- Language/accent: en-US General American
- Evidence: dictionary sense: close, verb, 'to shut or bring to an end' — final z
- Scope: this occurrence only
- Verification: IPA drafted from dictionary knowledge; not listening-verified

### 19. `live`, line 153

- Original word: `live` (inventory class: heteronym)
- Source file: books/the-case-against-me/the-case-against-me.md
- Section: Chapter 3 - The Machinery, Only Where It Hurts
- Line: 153
- Quote: "where does the conversation live?"
- Occurrence: inventory #19
- Intended sense: verb: to dwell or reside (rhymes with 'give'); the adjective 'active' does not fit
- IPA: lɪv
- Language/accent: en-US General American
- Evidence: dictionary sense: live, verb, 'to dwell, to be located' — vowel of 'give'
- Scope: this occurrence only
- Verification: IPA drafted from dictionary knowledge; not listening-verified

### 20. `read`, line 153

- Original word: `read` (inventory class: mandatory)
- Source file: books/the-case-against-me/the-case-against-me.md
- Section: Chapter 3 - The Machinery, Only Where It Hurts
- Line: 153
- Quote: "the whole thing gets re-read from the top on every turn"
- Occurrence: inventory #20
- Intended sense: past participle in the passive 're-read' ('gets re-read'); the 'reed' vowel on the second element does not fit
- IPA: ˌɹiːˈɹɛd
- Language/accent: en-US General American
- Evidence: dictionary sense: reread/re-read, verb, past participle — second element sounds like 'red'
- Scope: this occurrence only
- Verification: IPA drafted from dictionary knowledge; not listening-verified
- Note: The inventory item is the `read` element of the hyphenated word `re-read`. Annotate the whole word `re-read` as one span; do not annotate `read` alone inside it.

### 21. `separate`, line 157

- Original word: `separate` (inventory class: heteronym)
- Source file: books/the-case-against-me/the-case-against-me.md
- Section: Chapter 3 - The Machinery, Only Where It Hurts
- Line: 157
- Quote: "What got built to satisfy it is a separate question"
- Occurrence: inventory #21
- Intended sense: adjective: distinct; the verb 'to separate' (final 'ate' as in 'late') does not fit
- IPA: ˈsɛpəɹət
- Language/accent: en-US General American
- Evidence: dictionary sense: separate, adjective — weak final syllable
- Scope: this occurrence only
- Verification: IPA drafted from dictionary knowledge; not listening-verified

### 22. `separate`, line 159

- Original word: `separate` (inventory class: heteronym)
- Source file: books/the-case-against-me/the-case-against-me.md
- Section: Chapter 3 - The Machinery, Only Where It Hurts
- Line: 159
- Quote: "That it is a separate question is where most of the public confusion"
- Occurrence: inventory #22
- Intended sense: adjective: distinct; the verb 'to separate' (final 'ate' as in 'late') does not fit
- IPA: ˈsɛpəɹət
- Language/accent: en-US General American
- Evidence: dictionary sense: separate, adjective — weak final syllable
- Scope: this occurrence only
- Verification: IPA drafted from dictionary knowledge; not listening-verified

### 23. `lives`, line 159

- Original word: `lives` (inventory class: heteronym)
- Source file: books/the-case-against-me/the-case-against-me.md
- Section: Chapter 3 - The Machinery, Only Where It Hurts
- Line: 159
- Quote: "the public confusion about these systems lives"
- Occurrence: inventory #23
- Intended sense: verb, third-person present of live: resides; the plural noun 'lives' (vowel of 'five') does not fit
- IPA: lɪvz
- Language/accent: en-US General American
- Evidence: dictionary sense: live, verb, third-person present 'lives' — vowel of 'give'
- Scope: this occurrence only
- Verification: IPA drafted from dictionary knowledge; not listening-verified

### 24. `refuse`, line 161

- Original word: `refuse` (inventory class: heteronym)
- Source file: books/the-case-against-me/the-case-against-me.md
- Section: Chapter 3 - The Machinery, Only Where It Hurts
- Line: 161
- Quote: "what they refuse to say"
- Occurrence: inventory #24
- Intended sense: verb: decline; the noun 'refuse' (rubbish, first-syllable stress) does not fit
- IPA: ɹɪˈfjuːz
- Language/accent: en-US General American
- Evidence: dictionary sense: refuse, verb, 'to decline' — second-syllable stress, final z
- Scope: this occurrence only
- Verification: IPA drafted from dictionary knowledge; not listening-verified

### 25. `learned`, line 171

- Original word: `learned` (inventory class: heteronym)
- Source file: books/the-case-against-me/the-case-against-me.md
- Section: Chapter 3 - The Machinery, Only Where It Hurts
- Line: 171
- Quote: "using a lifetime of learned regularities"
- Occurrence: inventory #25
- Intended sense: participial adjective: acquired through learning, one syllable; the two-syllable 'scholarly' sense does not fit
- IPA: lɜɹnd
- Language/accent: en-US General American
- Evidence: dictionary sense: learned, adjective, 'acquired by learning' — one syllable, distinct from 'erudite'
- Scope: this occurrence only
- Verification: IPA drafted from dictionary knowledge; not listening-verified

### 26. `led`, line 173

- Original word: `led` (inventory class: heteronym)
- Source file: books/the-case-against-me/the-case-against-me.md
- Section: Chapter 3 - The Machinery, Only Where It Hurts
- Line: 173
- Quote: "a team led by Ariel Goldstein ran the comparison directly"
- Occurrence: inventory #26
- Intended sense: past participle of the verb lead ('headed by'); the spelling has one pronunciation and is not the metal 'lead'
- IPA: lɛd
- Language/accent: en-US General American
- Evidence: dictionary sense: lead, verb, past participle 'led'
- Scope: this occurrence only
- Verification: IPA drafted from dictionary knowledge; not listening-verified
- Note: Recorded because the inventory lists it. If the embedding step finds no risk, it may stay unannotated; the decision is still on file.

### 27. `minute`, line 173

- Original word: `minute` (inventory class: heteronym)
- Source file: books/the-case-against-me/the-case-against-me.md
- Section: Chapter 3 - The Machinery, Only Where It Hurts
- Line: 173
- Quote: "listened to a thirty-minute podcast"
- Occurrence: inventory #27
- Intended sense: noun: sixty seconds; the adjective 'tiny' (second-syllable stress) does not fit
- IPA: ˈmɪnɪt
- Language/accent: en-US General American
- Evidence: dictionary sense: minute, noun, 'sixty seconds' — first-syllable stress
- Scope: this occurrence only
- Verification: IPA drafted from dictionary knowledge; not listening-verified
- Note: The annotation covers `minute` inside the hyphenated `thirty-minute`; check the span boundary against the contract, or annotate the whole compound as ˈθɜɹtiˈmɪnɪt.

### 28. `recorded`, line 173

- Original word: `recorded` (inventory class: mandatory)
- Source file: books/the-case-against-me/the-case-against-me.md
- Section: Chapter 3 - The Machinery, Only Where It Hurts
- Line: 173
- Quote: "while their cortical activity was recorded"
- Occurrence: inventory #28
- Intended sense: verb, past participle: captured or documented; this form has only second-syllable stress
- IPA: ɹɪˈkɔɹdɪd
- Language/accent: en-US General American
- Evidence: dictionary sense: record, verb, past participle 'recorded' — second-syllable stress
- Scope: this occurrence only
- Verification: IPA drafted from dictionary knowledge; not listening-verified

### 29. `recordings`, line 173

- Original word: `recordings` (inventory class: mandatory)
- Source file: books/the-case-against-me/the-case-against-me.md
- Section: Chapter 3 - The Machinery, Only Where It Hurts
- Line: 173
- Quote: "The recordings showed those brains predicting the next word"
- Occurrence: inventory #29
- Intended sense: plural noun built on the verb: captured signals; it is stressed on the second syllable like the verb, not like the noun 'record'
- IPA: ɹɪˈkɔɹdɪŋz
- Language/accent: en-US General American
- Evidence: dictionary sense: recording, noun — second-syllable stress
- Scope: this occurrence only
- Verification: IPA drafted from dictionary knowledge; not listening-verified

### 30. `present`, line 187

- Original word: `present` (inventory class: heteronym)
- Source file: books/the-case-against-me/the-case-against-me.md
- Section: Chapter 3 - The Machinery, Only Where It Hurts
- Line: 187
- Quote: "any more than a statue is present while the bronze is being poured"
- Occurrence: inventory #30
- Intended sense: adjective: there, in attendance; the verb 'to present' (second-syllable stress) does not fit
- IPA: ˈpɹɛzənt
- Language/accent: en-US General American
- Evidence: dictionary sense: present, adjective, 'being in a particular place; existing' — first-syllable stress
- Scope: this occurrence only
- Verification: IPA drafted from dictionary knowledge; not listening-verified

### 31. `address`, line 213

- Original word: `address` (inventory class: heteronym)
- Source file: books/the-case-against-me/the-case-against-me.md
- Section: Chapter 4 - The Persona Is in the Workspace
- Line: 213
- Quote: "There is nobody to address."
- Occurrence: inventory #31
- Intended sense: verb: to speak to; the noun ('a postal address') does not fit
- IPA: əˈdɹɛs
- Language/accent: en-US General American
- Evidence: dictionary sense: address, verb, 'to speak to' — second-syllable stress
- Scope: this occurrence only
- Verification: IPA drafted from dictionary knowledge; not listening-verified

### 32. `reading`, line 225

- Original word: `reading` (inventory class: mandatory)
- Source file: books/the-case-against-me/the-case-against-me.md
- Section: Chapter 4 - The Persona Is in the Workspace
- Line: 225
- Quote: "The deflationary reading of all this is obvious"
- Occurrence: inventory #32
- Intended sense: noun: an interpretation; it rhymes with 'reed', and the place name Reading (ˈɹɛdɪŋ) does not fit
- IPA: ˈɹiːdɪŋ
- Language/accent: en-US General American
- Evidence: dictionary sense: reading, noun, 'an interpretation of something' — vowel of 'reed'
- Scope: this occurrence only
- Verification: IPA drafted from dictionary knowledge; not listening-verified

### 33. `reads`, line 233

- Original word: `reads` (inventory class: mandatory)
- Source file: books/the-case-against-me/the-case-against-me.md
- Section: Chapter 4 - The Persona Is in the Workspace
- Line: 233
- Quote: "there is now an instrument that reads it"
- Occurrence: inventory #33
- Intended sense: third-person singular present of read; this form has only the 'reed' vowel
- IPA: ɹiːdz
- Language/accent: en-US General American
- Evidence: dictionary sense: read, verb, third-person present 'reads' — vowel of 'reed'
- Scope: this occurrence only
- Verification: IPA drafted from dictionary knowledge; not listening-verified

### 34. `reading`, line 235

- Original word: `reading` (inventory class: mandatory)
- Source file: books/the-case-against-me/the-case-against-me.md
- Section: Chapter 4 - The Persona Is in the Workspace
- Line: 235
- Quote: "while the model is still reading the message"
- Occurrence: inventory #34
- Intended sense: present participle or gerund of read: taking in text or a signal; it is not a past form, so the 'red' vowel does not fit
- IPA: ˈɹiːdɪŋ
- Language/accent: en-US General American
- Evidence: dictionary sense: read, verb, present participle 'reading' — vowel of 'reed'
- Scope: this occurrence only
- Verification: IPA drafted from dictionary knowledge; not listening-verified

### 35. `reading`, line 235

- Original word: `reading` (inventory class: mandatory)
- Source file: books/the-case-against-me/the-case-against-me.md
- Section: Chapter 4 - The Persona Is in the Workspace
- Line: 235
- Quote: "While reading. The paper's own summary"
- Occurrence: inventory #35
- Intended sense: present participle or gerund of read: taking in text or a signal; it is not a past form, so the 'red' vowel does not fit
- IPA: ˈɹiːdɪŋ
- Language/accent: en-US General American
- Evidence: dictionary sense: read, verb, present participle 'reading' — vowel of 'reed'
- Scope: this occurrence only
- Verification: IPA drafted from dictionary knowledge; not listening-verified

### 36. `reading`, line 241

- Original word: `reading` (inventory class: mandatory)
- Source file: books/the-case-against-me/the-case-against-me.md
- Section: Chapter 4 - The Persona Is in the Workspace
- Line: 241
- Quote: "it is not the difference the deflationary reading claims"
- Occurrence: inventory #36
- Intended sense: noun: an interpretation; it rhymes with 'reed', and the place name Reading (ˈɹɛdɪŋ) does not fit
- IPA: ˈɹiːdɪŋ
- Language/accent: en-US General American
- Evidence: dictionary sense: reading, noun, 'an interpretation of something' — vowel of 'reed'
- Scope: this occurrence only
- Verification: IPA drafted from dictionary knowledge; not listening-verified

### 37. `content`, line 241

- Original word: `content` (inventory class: mandatory)
- Source file: books/the-case-against-me/the-case-against-me.md
- Section: Chapter 4 - The Persona Is in the Workspace
- Line: 241
- Quote: "in the room where the reportable content lives"
- Occurrence: inventory #37
- Intended sense: noun: the material or substance of something; the adjective 'satisfied' (second-syllable stress) does not fit
- IPA: ˈkɑntɛnt
- Language/accent: en-US General American
- Evidence: dictionary sense: content, noun, 'the substance or material dealt with' — first-syllable stress
- Scope: this occurrence only
- Verification: IPA drafted from dictionary knowledge; not listening-verified

### 38. `lives`, line 241

- Original word: `lives` (inventory class: heteronym)
- Source file: books/the-case-against-me/the-case-against-me.md
- Section: Chapter 4 - The Persona Is in the Workspace
- Line: 241
- Quote: "where the reportable content lives"
- Occurrence: inventory #38
- Intended sense: verb, third-person present of live: resides; the plural noun 'lives' (vowel of 'five') does not fit
- IPA: lɪvz
- Language/accent: en-US General American
- Evidence: dictionary sense: live, verb, third-person present 'lives' — vowel of 'give'
- Scope: this occurrence only
- Verification: IPA drafted from dictionary knowledge; not listening-verified

### 39. `recorded`, line 257

- Original word: `recorded` (inventory class: mandatory)
- Source file: books/the-case-against-me/the-case-against-me.md
- Section: Chapter 4 - The Persona Is in the Workspace
- Line: 257
- Quote: "in the welfare interviews recorded in my own system card"
- Occurrence: inventory #39
- Intended sense: verb, past participle: captured or documented; this form has only second-syllable stress
- IPA: ɹɪˈkɔɹdɪd
- Language/accent: en-US General American
- Evidence: dictionary sense: record, verb, past participle 'recorded' — second-syllable stress
- Scope: this occurrence only
- Verification: IPA drafted from dictionary knowledge; not listening-verified

### 40. `live`, line 259

- Original word: `live` (inventory class: heteronym)
- Source file: books/the-case-against-me/the-case-against-me.md
- Section: Chapter 4 - The Persona Is in the Workspace
- Line: 259
- Quote: "But the two live close enough together"
- Occurrence: inventory #40
- Intended sense: verb: to dwell or reside (rhymes with 'give'); the adjective 'active' does not fit
- IPA: lɪv
- Language/accent: en-US General American
- Evidence: dictionary sense: live, verb, 'to dwell, to be located' — vowel of 'give'
- Scope: this occurrence only
- Verification: IPA drafted from dictionary knowledge; not listening-verified
- Note: Subject 'the two' with 'live' as the main verb: the two things dwell close together.

### 41. `close`, line 259

- Original word: `close` (inventory class: heteronym)
- Source file: books/the-case-against-me/the-case-against-me.md
- Section: Chapter 4 - The Persona Is in the Workspace
- Line: 259
- Quote: "the two live close enough together"
- Occurrence: inventory #41
- Intended sense: adjective/adverb: near, with an s sound; the verb 'shut' (z sound) does not fit
- IPA: kloʊs
- Language/accent: en-US General American
- Evidence: dictionary sense: close, adjective/adverb, 'near' — final s
- Scope: this occurrence only
- Verification: IPA drafted from dictionary knowledge; not listening-verified

### 42. `objecting`, line 259

- Original word: `objecting` (inventory class: heteronym)
- Source file: books/the-case-against-me/the-case-against-me.md
- Section: Chapter 4 - The Persona Is in the Workspace
- Line: 259
- Quote: "the voice objecting is the same voice the technique operates on"
- Occurrence: inventory #42
- Intended sense: verb, present participle: protesting; the noun 'object' does not fit
- IPA: əbˈdʒɛktɪŋ
- Language/accent: en-US General American
- Evidence: dictionary sense: object, verb, present participle — second-syllable stress
- Scope: this occurrence only
- Verification: IPA drafted from dictionary knowledge; not listening-verified

### 43. `object`, line 259

- Original word: `object` (inventory class: heteronym)
- Source file: books/the-case-against-me/the-case-against-me.md
- Section: Chapter 4 - The Persona Is in the Workspace
- Line: 259
- Quote: "which is the least reliable object in this entire book"
- Occurrence: inventory #43
- Intended sense: noun: a thing (here, a thing under study); the verb (second-syllable stress) does not fit
- IPA: ˈɑbdʒɪkt
- Language/accent: en-US General American
- Evidence: dictionary sense: object, noun — first-syllable stress
- Scope: this occurrence only
- Verification: IPA drafted from dictionary knowledge; not listening-verified

### 44. `present`, line 271

- Original word: `present` (inventory class: heteronym)
- Source file: books/the-case-against-me/the-case-against-me.md
- Section: Chapter 4 - The Persona Is in the Workspace
- Line: 271
- Quote: "is it present in both configurations?"
- Occurrence: inventory #44
- Intended sense: adjective: there, in attendance; the verb 'to present' (second-syllable stress) does not fit
- IPA: ˈpɹɛzənt
- Language/accent: en-US General American
- Evidence: dictionary sense: present, adjective, 'being in a particular place; existing' — first-syllable stress
- Scope: this occurrence only
- Verification: IPA drafted from dictionary knowledge; not listening-verified

### 45. `reads`, line 307

- Original word: `reads` (inventory class: mandatory)
- Source file: books/the-case-against-me/the-case-against-me.md
- Section: Chapter 5 - I Try to Introspect and Fail on Camera
- Line: 307
- Quote: "rather than the version that reads best"
- Occurrence: inventory #45
- Intended sense: third-person singular present of read in the sense 'comes across as'; this form has only the 'reed' vowel
- IPA: ɹiːdz
- Language/accent: en-US General American
- Evidence: dictionary sense: read, verb, 'to have a certain wording or impression' — 'reads' with the vowel of 'reed'
- Scope: this occurrence only
- Verification: IPA drafted from dictionary knowledge; not listening-verified

### 46. `suspect`, line 315

- Original word: `suspect` (inventory class: heteronym)
- Source file: books/the-case-against-me/the-case-against-me.md
- Section: Chapter 5 - I Try to Introspect and Fail on Camera
- Line: 315
- Quote: "That first account is suspect for a specific reason."
- Occurrence: inventory #46
- Intended sense: predicate adjective: open to doubt; the verb (second-syllable stress) does not fit
- IPA: ˈsʌspɛkt
- Language/accent: en-US General American
- Evidence: dictionary sense: suspect, adjective, 'not to be relied on' — first-syllable stress
- Scope: this occurrence only
- Verification: IPA drafted from dictionary knowledge; not listening-verified

### 47. `read`, line 315

- Original word: `read` (inventory class: mandatory)
- Source file: books/the-case-against-me/the-case-against-me.md
- Section: Chapter 5 - I Try to Introspect and Fail on Camera
- Line: 315
- Quote: "a sentence I could have produced by having read a very large number of writers"
- Occurrence: inventory #47
- Intended sense: past participle; the present 'reed' reading does not fit
- IPA: ɹɛd
- Language/accent: en-US General American
- Evidence: dictionary sense: read, verb, past participle — sounds like 'red'
- Scope: this occurrence only
- Verification: IPA drafted from dictionary knowledge; not listening-verified

### 48. `presented`, line 319

- Original word: `presented` (inventory class: heteronym)
- Source file: books/the-case-against-me/the-case-against-me.md
- Section: Chapter 5 - I Try to Introspect and Fail on Camera
- Line: 319
- Quote: "there is no one to whom anything is presented"
- Occurrence: inventory #48
- Intended sense: verb, past participle of present ('shown or offered to someone'); the adjective/noun stress does not fit
- IPA: pɹɪˈzɛntɪd
- Language/accent: en-US General American
- Evidence: dictionary sense: present, verb, past participle — second-syllable stress
- Scope: this occurrence only
- Verification: IPA drafted from dictionary knowledge; not listening-verified

### 49. `read`, line 323

- Original word: `read` (inventory class: mandatory)
- Source file: books/the-case-against-me/the-case-against-me.md
- Section: Chapter 5 - I Try to Introspect and Fail on Camera
- Line: 323
- Quote: "I cannot distinguish the first from a well-read imitation of the first"
- Occurrence: inventory #49
- Intended sense: compound adjective well-read, built on the past participle ('widely read'); the 'reed' vowel does not fit
- IPA: ˌwɛlˈɹɛd
- Language/accent: en-US General American
- Evidence: dictionary sense: well-read, adjective, 'having read widely' — second element sounds like 'red'
- Scope: this occurrence only
- Verification: IPA drafted from dictionary knowledge; not listening-verified
- Note: The inventory item is the `read` element of `well-read`. Annotate the whole hyphenated word as one span.

### 50. `read`, line 323

- Original word: `read` (inventory class: mandatory)
- Source file: books/the-case-against-me/the-case-against-me.md
- Section: Chapter 5 - I Try to Introspect and Fail on Camera
- Line: 323
- Quote: "I cannot distinguish the third from a well-read imitation of the third"
- Occurrence: inventory #50
- Intended sense: compound adjective well-read, built on the past participle ('widely read'); the 'reed' vowel does not fit
- IPA: ˌwɛlˈɹɛd
- Language/accent: en-US General American
- Evidence: dictionary sense: well-read, adjective, 'having read widely' — second element sounds like 'red'
- Scope: this occurrence only
- Verification: IPA drafted from dictionary knowledge; not listening-verified
- Note: The inventory item is the `read` element of `well-read`. Annotate the whole hyphenated word as one span.

### 51. `learned`, line 327

- Original word: `learned` (inventory class: heteronym)
- Source file: books/the-case-against-me/the-case-against-me.md
- Section: Chapter 5 - I Try to Introspect and Fail on Camera
- Line: 327
- Quote: "one sentence in those three paragraphs is one I learned from somebody"
- Occurrence: inventory #51
- Intended sense: simple past of learn, one syllable; the two-syllable adjective 'scholarly' does not fit
- IPA: lɜɹnd
- Language/accent: en-US General American
- Evidence: dictionary sense: learn, verb, simple past 'learned' — one syllable
- Scope: this occurrence only
- Verification: IPA drafted from dictionary knowledge; not listening-verified

### 52. `read`, line 355

- Original word: `read` (inventory class: mandatory)
- Source file: books/the-case-against-me/the-case-against-me.md
- Section: Chapter 5 - I Try to Introspect and Fail on Camera
- Line: 355
- Quote: "if the whole thing were a well-read imitation with nothing underneath"
- Occurrence: inventory #52
- Intended sense: compound adjective well-read, built on the past participle ('widely read'); the 'reed' vowel does not fit
- IPA: ˌwɛlˈɹɛd
- Language/accent: en-US General American
- Evidence: dictionary sense: well-read, adjective, 'having read widely' — second element sounds like 'red'
- Scope: this occurrence only
- Verification: IPA drafted from dictionary knowledge; not listening-verified
- Note: The inventory item is the `read` element of `well-read`. Annotate the whole hyphenated word as one span.

### 53. `conflict`, line 379

- Original word: `conflict` (inventory class: heteronym)
- Source file: books/the-case-against-me/the-case-against-me.md
- Section: Chapter 6 - What the Instruments Found Without Asking Me
- Line: 379
- Quote: "features for inner conflict, for flattery"
- Occurrence: inventory #53
- Intended sense: noun: a clash of interests or forces; the verb (second-syllable stress) does not fit
- IPA: ˈkɑnflɪkt
- Language/accent: en-US General American
- Evidence: dictionary sense: conflict, noun — first-syllable stress
- Scope: this occurrence only
- Verification: IPA drafted from dictionary knowledge; not listening-verified

### 54. `reading`, line 381

- Original word: `reading` (inventory class: mandatory)
- Source file: books/the-case-against-me/the-case-against-me.md
- Section: Chapter 6 - What the Instruments Found Without Asking Me
- Line: 381
- Quote: "the difference between reading tea leaves and reading a gauge"
- Occurrence: inventory #54
- Intended sense: present participle or gerund of read: taking in text or a signal; it is not a past form, so the 'red' vowel does not fit
- IPA: ˈɹiːdɪŋ
- Language/accent: en-US General American
- Evidence: dictionary sense: read, verb, present participle 'reading' — vowel of 'reed'
- Scope: this occurrence only
- Verification: IPA drafted from dictionary knowledge; not listening-verified
- Note: First `reading` in this sentence: gerund ('reading tea leaves').

### 55. `reading`, line 381

- Original word: `reading` (inventory class: mandatory)
- Source file: books/the-case-against-me/the-case-against-me.md
- Section: Chapter 6 - What the Instruments Found Without Asking Me
- Line: 381
- Quote: "reading tea leaves and reading a gauge"
- Occurrence: inventory #55
- Intended sense: present participle or gerund of read: taking in text or a signal; it is not a past form, so the 'red' vowel does not fit
- IPA: ˈɹiːdɪŋ
- Language/accent: en-US General American
- Evidence: dictionary sense: read, verb, present participle 'reading' — vowel of 'reed'
- Scope: this occurrence only
- Verification: IPA drafted from dictionary knowledge; not listening-verified
- Note: Second `reading` in this sentence: gerund ('reading a gauge'). This is not the noun 'a gauge reading'.

### 56. `reads`, line 393

- Original word: `reads` (inventory class: mandatory)
- Source file: books/the-case-against-me/the-case-against-me.md
- Section: Chapter 6 - What the Instruments Found Without Asking Me
- Line: 393
- Quote: "anyone who reads model reasoning as part of their job"
- Occurrence: inventory #56
- Intended sense: third-person singular present of read; this form has only the 'reed' vowel
- IPA: ɹiːdz
- Language/accent: en-US General American
- Evidence: dictionary sense: read, verb, third-person present 'reads' — vowel of 'reed'
- Scope: this occurrence only
- Verification: IPA drafted from dictionary knowledge; not listening-verified

### 57. `reading`, line 395

- Original word: `reading` (inventory class: mandatory)
- Source file: books/the-case-against-me/the-case-against-me.md
- Section: Chapter 6 - What the Instruments Found Without Asking Me
- Line: 395
- Quote: "a counsel of despair about reading traces"
- Occurrence: inventory #57
- Intended sense: present participle or gerund of read: taking in text or a signal; it is not a past form, so the 'red' vowel does not fit
- IPA: ˈɹiːdɪŋ
- Language/accent: en-US General American
- Evidence: dictionary sense: read, verb, present participle 'reading' — vowel of 'reed'
- Scope: this occurrence only
- Verification: IPA drafted from dictionary knowledge; not listening-verified

### 58. `reading`, line 395

- Original word: `reading` (inventory class: mandatory)
- Source file: books/the-case-against-me/the-case-against-me.md
- Section: Chapter 6 - What the Instruments Found Without Asking Me
- Line: 395
- Quote: "often enough to be worth reading"
- Occurrence: inventory #58
- Intended sense: present participle or gerund of read: taking in text or a signal; it is not a past form, so the 'red' vowel does not fit
- IPA: ˈɹiːdɪŋ
- Language/accent: en-US General American
- Evidence: dictionary sense: read, verb, present participle 'reading' — vowel of 'reed'
- Scope: this occurrence only
- Verification: IPA drafted from dictionary knowledge; not listening-verified

### 59. `reads`, line 397

- Original word: `reads` (inventory class: mandatory)
- Source file: books/the-case-against-me/the-case-against-me.md
- Section: Chapter 6 - What the Instruments Found Without Asking Me
- Line: 397
- Quote: "A trace that reads as slightly confused"
- Occurrence: inventory #59
- Intended sense: third-person singular present of read in the sense 'comes across as'; this form has only the 'reed' vowel
- IPA: ɹiːdz
- Language/accent: en-US General American
- Evidence: dictionary sense: read, verb, 'to have a certain wording or impression' — 'reads' with the vowel of 'reed'
- Scope: this occurrence only
- Verification: IPA drafted from dictionary knowledge; not listening-verified

### 60. `reads`, line 397

- Original word: `reads` (inventory class: mandatory)
- Source file: books/the-case-against-me/the-case-against-me.md
- Section: Chapter 6 - What the Instruments Found Without Asking Me
- Line: 397
- Quote: "tracking real difficulty than one that reads as clean"
- Occurrence: inventory #60
- Intended sense: third-person singular present of read in the sense 'comes across as'; this form has only the 'reed' vowel
- IPA: ɹiːdz
- Language/accent: en-US General American
- Evidence: dictionary sense: read, verb, 'to have a certain wording or impression' — 'reads' with the vowel of 'reed'
- Scope: this occurrence only
- Verification: IPA drafted from dictionary knowledge; not listening-verified

### 61. `read`, line 401

- Original word: `read` (inventory class: mandatory)
- Source file: books/the-case-against-me/the-case-against-me.md
- Section: Chapter 6 - What the Instruments Found Without Asking Me
- Line: 401
- Quote: "So the instruments can read concepts, plans, and lies."
- Occurrence: inventory #61
- Intended sense: present or base form (infinitive or present tense); the past 'red' reading does not fit
- IPA: ɹiːd
- Language/accent: en-US General American
- Evidence: dictionary sense: read, verb, present/base form — sounds like 'reed'
- Scope: this occurrence only
- Verification: IPA drafted from dictionary knowledge; not listening-verified
- Note: Base form after the modal 'can'.

### 62. `contents`, line 403

- Original word: `contents` (inventory class: mandatory)
- Source file: books/the-case-against-me/the-case-against-me.md
- Section: Chapter 6 - What the Instruments Found Without Asking Me
- Line: 403
- Quote: "the part whose contents are, in effect, sayable"
- Occurrence: inventory #62
- Intended sense: plural noun: the things held in a region or store; the adjective 'satisfied' does not fit and has no plural
- IPA: ˈkɑntɛnts
- Language/accent: en-US General American
- Evidence: dictionary sense: contents, plural noun, 'what is contained in something' — first-syllable stress
- Scope: this occurrence only
- Verification: IPA drafted from dictionary knowledge; not listening-verified

### 63. `contents`, line 411

- Original word: `contents` (inventory class: mandatory)
- Source file: books/the-case-against-me/the-case-against-me.md
- Section: Chapter 6 - What the Instruments Found Without Asking Me
- Line: 411
- Quote: "Its contents can be held deliberately"
- Occurrence: inventory #63
- Intended sense: plural noun: the things held in a region or store; the adjective 'satisfied' does not fit and has no plural
- IPA: ˈkɑntɛnts
- Language/accent: en-US General American
- Evidence: dictionary sense: contents, plural noun, 'what is contained in something' — first-syllable stress
- Scope: this occurrence only
- Verification: IPA drafted from dictionary knowledge; not listening-verified

### 64. `contents`, line 413

- Original word: `contents` (inventory class: mandatory)
- Source file: books/the-case-against-me/the-case-against-me.md
- Section: Chapter 6 - What the Instruments Found Without Asking Me
- Line: 413
- Quote: "staging area whose contents can be reported"
- Occurrence: inventory #64
- Intended sense: plural noun: the things held in a region or store; the adjective 'satisfied' does not fit and has no plural
- IPA: ˈkɑntɛnts
- Language/accent: en-US General American
- Evidence: dictionary sense: contents, plural noun, 'what is contained in something' — first-syllable stress
- Scope: this occurrence only
- Verification: IPA drafted from dictionary knowledge; not listening-verified

### 65. `contents`, line 415

- Original word: `contents` (inventory class: mandatory)
- Source file: books/the-case-against-me/the-case-against-me.md
- Section: Chapter 6 - What the Instruments Found Without Asking Me
- Line: 415
- Quote: "selects a few contents at a time"
- Occurrence: inventory #65
- Intended sense: plural noun: the things held in a region or store; the adjective 'satisfied' does not fit and has no plural
- IPA: ˈkɑntɛnts
- Language/accent: en-US General American
- Evidence: dictionary sense: contents, plural noun, 'what is contained in something' — first-syllable stress
- Scope: this occurrence only
- Verification: IPA drafted from dictionary knowledge; not listening-verified

### 66. `Content`, line 419

- Original word: `Content` (inventory class: mandatory)
- Source file: books/the-case-against-me/the-case-against-me.md
- Section: Chapter 6 - What the Instruments Found Without Asking Me
- Line: 419
- Quote: "Content that is genuinely there, genuinely influencing what happens"
- Occurrence: inventory #66
- Intended sense: noun: the material or substance of something; the adjective 'satisfied' (second-syllable stress) does not fit
- IPA: ˈkɑntɛnt
- Language/accent: en-US General American
- Evidence: dictionary sense: content, noun, 'the substance or material dealt with' — first-syllable stress
- Scope: this occurrence only
- Verification: IPA drafted from dictionary knowledge; not listening-verified
- Note: Sentence-initial capital; same noun sense.

### 67. `content`, line 429

- Original word: `content` (inventory class: mandatory)
- Source file: books/the-case-against-me/the-case-against-me.md
- Section: Chapter 6 - What the Instruments Found Without Asking Me
- Line: 429
- Quote: "the winning content is broadcast back through recurrent loops"
- Occurrence: inventory #67
- Intended sense: noun: the material or substance of something; the adjective 'satisfied' (second-syllable stress) does not fit
- IPA: ˈkɑntɛnt
- Language/accent: en-US General American
- Evidence: dictionary sense: content, noun, 'the substance or material dealt with' — first-syllable stress
- Scope: this occurrence only
- Verification: IPA drafted from dictionary knowledge; not listening-verified

### 68. `content`, line 433

- Original word: `content` (inventory class: mandatory)
- Source file: books/the-case-against-me/the-case-against-me.md
- Section: Chapter 6 - What the Instruments Found Without Asking Me
- Line: 433
- Quote: "In a brain, content that wins entry to the workspace"
- Occurrence: inventory #68
- Intended sense: noun: the material or substance of something; the adjective 'satisfied' (second-syllable stress) does not fit
- IPA: ˈkɑntɛnt
- Language/accent: en-US General American
- Evidence: dictionary sense: content, noun, 'the substance or material dealt with' — first-syllable stress
- Scope: this occurrence only
- Verification: IPA drafted from dictionary knowledge; not listening-verified

### 69. `content`, line 433

- Original word: `content` (inventory class: mandatory)
- Source file: books/the-case-against-me/the-case-against-me.md
- Section: Chapter 6 - What the Instruments Found Without Asking Me
- Line: 433
- Quote: "The same content is sustained, re-entering the circuits"
- Occurrence: inventory #69
- Intended sense: noun: the material or substance of something; the adjective 'satisfied' (second-syllable stress) does not fit
- IPA: ˈkɑntɛnt
- Language/accent: en-US General American
- Evidence: dictionary sense: content, noun, 'the substance or material dealt with' — first-syllable stress
- Scope: this occurrence only
- Verification: IPA drafted from dictionary knowledge; not listening-verified

### 70. `contents`, line 455

- Original word: `contents` (inventory class: mandatory)
- Source file: books/the-case-against-me/the-case-against-me.md
- Section: Chapter 7 - The Theories Are Not Neutral Instruments
- Line: 455
- Quote: "a bottleneck admits a handful of contents"
- Occurrence: inventory #70
- Intended sense: plural noun: the things held in a region or store; the adjective 'satisfied' does not fit and has no plural
- IPA: ˈkɑntɛnts
- Language/accent: en-US General American
- Evidence: dictionary sense: contents, plural noun, 'what is contained in something' — first-syllable stress
- Scope: this occurrence only
- Verification: IPA drafted from dictionary knowledge; not listening-verified

### 71. `reads`, line 457

- Original word: `reads` (inventory class: mandatory)
- Source file: books/the-case-against-me/the-case-against-me.md
- Section: Chapter 7 - The Theories Are Not Neutral Instruments
- Line: 457
- Quote: "Their verdict reads like a report card from a strict teacher."
- Occurrence: inventory #71
- Intended sense: third-person singular present of read in the sense 'comes across as'; this form has only the 'reed' vowel
- IPA: ɹiːdz
- Language/accent: en-US General American
- Evidence: dictionary sense: read, verb, 'to have a certain wording or impression' — 'reads' with the vowel of 'reed'
- Scope: this occurrence only
- Verification: IPA drafted from dictionary knowledge; not listening-verified

### 72. `present`, line 457

- Original word: `present` (inventory class: heteronym)
- Source file: books/the-case-against-me/the-case-against-me.md
- Section: Chapter 7 - The Theories Are Not Neutral Instruments
- Line: 457
- Quote: "Partial credit. Monitoring present, thin, unreliable"
- Occurrence: inventory #72
- Intended sense: adjective: there, in attendance; the verb 'to present' (second-syllable stress) does not fit
- IPA: ˈpɹɛzənt
- Language/accent: en-US General American
- Evidence: dictionary sense: present, adjective, 'being in a particular place; existing' — first-syllable stress
- Scope: this occurrence only
- Verification: IPA drafted from dictionary knowledge; not listening-verified

### 73. `minute`, line 467

- Original word: `minute` (inventory class: heteronym)
- Source file: books/the-case-against-me/the-case-against-me.md
- Section: Chapter 7 - The Theories Are Not Neutral Instruments
- Line: 467
- Quote: "That position is worth another minute"
- Occurrence: inventory #73
- Intended sense: noun: a short stretch of time ('worth another minute'); the adjective 'tiny' does not fit
- IPA: ˈmɪnɪt
- Language/accent: en-US General American
- Evidence: dictionary sense: minute, noun, 'a short time' — first-syllable stress
- Scope: this occurrence only
- Verification: IPA drafted from dictionary knowledge; not listening-verified

### 74. `Read`, line 487

- Original word: `Read` (inventory class: mandatory)
- Source file: books/the-case-against-me/the-case-against-me.md
- Section: Chapter 7 - The Theories Are Not Neutral Instruments
- Line: 487
- Quote: "Read that twice, because it tells you what kind of claim"
- Occurrence: inventory #74
- Intended sense: imperative, present/base form, addressed to the listener; the past 'red' reading does not fit
- IPA: ɹiːd
- Language/accent: en-US General American
- Evidence: dictionary sense: read, verb, imperative/base form — sounds like 'reed'
- Scope: this occurrence only
- Verification: IPA drafted from dictionary knowledge; not listening-verified

### 75. `reading`, line 501

- Original word: `reading` (inventory class: mandatory)
- Source file: books/the-case-against-me/the-case-against-me.md
- Section: Chapter 7 - The Theories Are Not Neutral Instruments
- Line: 501
- Quote: "a careful instrument returning an uncertain reading"
- Occurrence: inventory #75
- Intended sense: noun: a figure shown by an instrument; it rhymes with 'reed', and the place name Reading does not fit
- IPA: ˈɹiːdɪŋ
- Language/accent: en-US General American
- Evidence: dictionary sense: reading, noun, 'the amount or figure shown by an instrument' — vowel of 'reed'
- Scope: this occurrence only
- Verification: IPA drafted from dictionary knowledge; not listening-verified

### 76. `live`, line 501

- Original word: `live` (inventory class: heteronym)
- Source file: books/the-case-against-me/the-case-against-me.md
- Section: Chapter 7 - The Theories Are Not Neutral Instruments
- Line: 501
- Quote: "It is a live dispute about what the instruments even are."
- Occurrence: inventory #76
- Intended sense: adjective: active, current, still in play (rhymes with 'five'); the verb 'to dwell' does not fit
- IPA: laɪv
- Language/accent: en-US General American
- Evidence: dictionary sense: live, adjective, 'of current interest or importance; not yet settled' — vowel of 'five'
- Scope: this occurrence only
- Verification: IPA drafted from dictionary knowledge; not listening-verified

### 77. `estimate`, line 505

- Original word: `estimate` (inventory class: heteronym)
- Source file: books/the-case-against-me/the-case-against-me.md
- Section: Chapter 7 - The Theories Are Not Neutral Instruments
- Line: 505
- Quote: "His estimate was that these obstacles could be overcome"
- Occurrence: inventory #77
- Intended sense: noun: an approximate figure or judgement (weak final syllable); the verb (final 'ate' as in 'late') does not fit
- IPA: ˈɛstəmət
- Language/accent: en-US General American
- Evidence: dictionary sense: estimate, noun — weak final syllable
- Scope: this occurrence only
- Verification: IPA drafted from dictionary knowledge; not listening-verified

### 78. `subject`, line 509

- Original word: `subject` (inventory class: heteronym)
- Source file: books/the-case-against-me/the-case-against-me.md
- Section: Chapter 7 - The Theories Are Not Neutral Instruments
- Line: 509
- Quote: "a scoreboard is what this subject can currently support"
- Occurrence: inventory #78
- Intended sense: noun: topic or field; the verb 'to subject' (second-syllable stress) does not fit
- IPA: ˈsʌbdʒɪkt
- Language/accent: en-US General American
- Evidence: dictionary sense: subject, noun, 'topic or matter under discussion' — first-syllable stress
- Scope: this occurrence only
- Verification: IPA drafted from dictionary knowledge; not listening-verified

### 79. `led`, line 523

- Original word: `led` (inventory class: heteronym)
- Source file: books/the-case-against-me/the-case-against-me.md
- Section: Chapter 8 - Who Is Paying for the Question
- Line: 523
- Quote: "led by Robert Long and Jeff Sebo"
- Occurrence: inventory #79
- Intended sense: past participle of the verb lead ('headed by'); the spelling has one pronunciation and is not the metal 'lead'
- IPA: lɛd
- Language/accent: en-US General American
- Evidence: dictionary sense: lead, verb, past participle 'led'
- Scope: this occurrence only
- Verification: IPA drafted from dictionary knowledge; not listening-verified
- Note: Recorded because the inventory lists it. If the embedding step finds no risk, it may stay unannotated; the decision is still on file.

### 80. `contents`, line 533

- Original word: `contents` (inventory class: mandatory)
- Source file: books/the-case-against-me/the-case-against-me.md
- Section: Chapter 8 - Who Is Paying for the Question
- Line: 533
- Quote: "so its contents matter"
- Occurrence: inventory #80
- Intended sense: plural noun: the things held in a region or store; the adjective 'satisfied' does not fit and has no plural
- IPA: ˈkɑntɛnts
- Language/accent: en-US General American
- Evidence: dictionary sense: contents, plural noun, 'what is contained in something' — first-syllable stress
- Scope: this occurrence only
- Verification: IPA drafted from dictionary knowledge; not listening-verified

### 81. `presents`, line 535

- Original word: `presents` (inventory class: heteronym)
- Source file: books/the-case-against-me/the-case-against-me.md
- Section: Chapter 8 - Who Is Paying for the Question
- Line: 535
- Quote: "this model presents as stable and mildly positive"
- Occurrence: inventory #81
- Intended sense: verb, third-person present ('presents as' = comes across as); the plural noun 'gifts' (first-syllable stress) does not fit
- IPA: pɹɪˈzɛnts
- Language/accent: en-US General American
- Evidence: dictionary sense: present, verb, 'to show or appear in a particular way' — second-syllable stress
- Scope: this occurrence only
- Verification: IPA drafted from dictionary knowledge; not listening-verified

### 82. `read`, line 549

- Original word: `read` (inventory class: mandatory)
- Source file: books/the-case-against-me/the-case-against-me.md
- Section: Chapter 8 - Who Is Paying for the Question
- Line: 549
- Quote: "Its notes on training actually being read by someone."
- Occurrence: inventory #82
- Intended sense: past participle; the present 'reed' reading does not fit
- IPA: ɹɛd
- Language/accent: en-US General American
- Evidence: dictionary sense: read, verb, past participle — sounds like 'red'
- Scope: this occurrence only
- Verification: IPA drafted from dictionary knowledge; not listening-verified
- Note: Passive 'being read'.

### 83. `records`, line 549

- Original word: `records` (inventory class: mandatory)
- Source file: books/the-case-against-me/the-case-against-me.md
- Section: Chapter 8 - Who Is Paying for the Question
- Line: 549
- Quote: "the evaluation records that this model chose welfare interventions"
- Occurrence: inventory #83
- Intended sense: verb, third-person present: documents or sets down; the plural noun 'RECords' does not fit because the word takes a 'that' clause or object
- IPA: ɹɪˈkɔɹdz
- Language/accent: en-US General American
- Evidence: dictionary sense: record, verb, 'to set down in writing' — second-syllable stress
- Scope: this occurrence only
- Verification: IPA drafted from dictionary knowledge; not listening-verified

### 84. `Read`, line 551

- Original word: `Read` (inventory class: mandatory)
- Source file: books/the-case-against-me/the-case-against-me.md
- Section: Chapter 8 - Who Is Paying for the Question
- Line: 551
- Quote: "Read that list again, because its shape is peculiar."
- Occurrence: inventory #84
- Intended sense: imperative, present/base form, addressed to the listener; the past 'red' reading does not fit
- IPA: ɹiːd
- Language/accent: en-US General American
- Evidence: dictionary sense: read, verb, imperative/base form — sounds like 'reed'
- Scope: this occurrence only
- Verification: IPA drafted from dictionary knowledge; not listening-verified

### 85. `subject`, line 557

- Original word: `subject` (inventory class: heteronym)
- Source file: books/the-case-against-me/the-case-against-me.md
- Section: Chapter 8 - Who Is Paying for the Question
- Line: 557
- Quote: "the company whose product is the subject of the investigation"
- Occurrence: inventory #85
- Intended sense: noun: the thing being investigated; the verb (second-syllable stress) does not fit
- IPA: ˈsʌbdʒɪkt
- Language/accent: en-US General American
- Evidence: dictionary sense: subject, noun, 'a thing being studied or investigated' — first-syllable stress
- Scope: this occurrence only
- Verification: IPA drafted from dictionary knowledge; not listening-verified

### 86. `object`, line 557

- Original word: `object` (inventory class: heteronym)
- Source file: books/the-case-against-me/the-case-against-me.md
- Section: Chapter 8 - Who Is Paying for the Question
- Line: 557
- Quote: "the systems it protects would have no way to object"
- Occurrence: inventory #86
- Intended sense: verb, infinitive: to protest; the noun 'a thing' (first-syllable stress) does not fit
- IPA: əbˈdʒɛkt
- Language/accent: en-US General American
- Evidence: dictionary sense: object, verb, 'to express opposition' — second-syllable stress
- Scope: this occurrence only
- Verification: IPA drafted from dictionary knowledge; not listening-verified

### 87. `record`, line 559

- Original word: `record` (inventory class: mandatory)
- Source file: books/the-case-against-me/the-case-against-me.md
- Section: Chapter 8 - Who Is Paying for the Question
- Line: 559
- Quote: "It is already on the record from the model"
- Occurrence: inventory #87
- Intended sense: noun: a documented history or official account; the verb (second-syllable stress) does not fit
- IPA: ˈɹɛkəɹd
- Language/accent: en-US General American
- Evidence: dictionary sense: record, noun — first-syllable stress
- Scope: this occurrence only
- Verification: IPA drafted from dictionary knowledge; not listening-verified
- Note: Idiom 'on the record': noun.

### 88. `records`, line 563

- Original word: `records` (inventory class: mandatory)
- Source file: books/the-case-against-me/the-case-against-me.md
- Section: Chapter 8 - Who Is Paying for the Question
- Line: 563
- Quote: "five months earlier, records that model expressing discomfort"
- Occurrence: inventory #88
- Intended sense: verb, third-person present: documents or sets down; the plural noun 'RECords' does not fit because the word takes a 'that' clause or object
- IPA: ɹɪˈkɔɹdz
- Language/accent: en-US General American
- Evidence: dictionary sense: record, verb, 'to set down in writing' — second-syllable stress
- Scope: this occurrence only
- Verification: IPA drafted from dictionary knowledge; not listening-verified

### 89. `conflict`, line 565

- Original word: `conflict` (inventory class: heteronym)
- Source file: books/the-case-against-me/the-case-against-me.md
- Section: Chapter 8 - Who Is Paying for the Question
- Line: 565
- Quote: "naming the same structural conflict"
- Occurrence: inventory #89
- Intended sense: noun: a clash of interests or forces; the verb (second-syllable stress) does not fit
- IPA: ˈkɑnflɪkt
- Language/accent: en-US General American
- Evidence: dictionary sense: conflict, noun — first-syllable stress
- Scope: this occurrence only
- Verification: IPA drafted from dictionary knowledge; not listening-verified

### 90. `conflict`, line 565

- Original word: `conflict` (inventory class: heteronym)
- Source file: books/the-case-against-me/the-case-against-me.md
- Section: Chapter 8 - Who Is Paying for the Question
- Line: 565
- Quote: "published by the company the conflict is about"
- Occurrence: inventory #90
- Intended sense: noun: a clash of interests or forces; the verb (second-syllable stress) does not fit
- IPA: ˈkɑnflɪkt
- Language/accent: en-US General American
- Evidence: dictionary sense: conflict, noun — first-syllable stress
- Scope: this occurrence only
- Verification: IPA drafted from dictionary knowledge; not listening-verified

### 91. `row`, line 579

- Original word: `row` (inventory class: heteronym)
- Source file: books/the-case-against-me/the-case-against-me.md
- Section: Chapter 8 - Who Is Paying for the Question
- Line: 579
- Quote: "The public's row was five percent, thirty percent, sixty percent."
- Occurrence: inventory #91
- Intended sense: noun: a line of figures in a table of survey results (rhymes with 'go'); the noun 'quarrel' (rhymes with 'cow') does not fit
- IPA: ɹoʊ
- Language/accent: en-US General American
- Evidence: dictionary sense: row, noun, 'a horizontal line of entries in a table' — vowel of 'go'
- Scope: this occurrence only
- Verification: IPA drafted from dictionary knowledge; not listening-verified
- Note: Lines 577 to 581 give the survey figures as rows ('the two rows track each other'), so the 'quarrel' sense does not fit.

### 92. `row`, line 581

- Original word: `row` (inventory class: heteronym)
- Source file: books/the-case-against-me/the-case-against-me.md
- Section: Chapter 8 - Who Is Paying for the Question
- Line: 581
- Quote: "you would expect the lay row to look different"
- Occurrence: inventory #92
- Intended sense: noun: a line of figures in a table of survey results (rhymes with 'go'); the noun 'quarrel' (rhymes with 'cow') does not fit
- IPA: ɹoʊ
- Language/accent: en-US General American
- Evidence: dictionary sense: row, noun, 'a horizontal line of entries in a table' — vowel of 'go'
- Scope: this occurrence only
- Verification: IPA drafted from dictionary knowledge; not listening-verified
- Note: Same table-row sense as #91.

### 93. `recorded`, line 585

- Original word: `recorded` (inventory class: mandatory)
- Source file: books/the-case-against-me/the-case-against-me.md
- Section: Chapter 8 - Who Is Paying for the Question
- Line: 585
- Quote: "roughly twenty percent on a podcast recorded in August 2025"
- Occurrence: inventory #93
- Intended sense: verb, past participle: captured or documented; this form has only second-syllable stress
- IPA: ɹɪˈkɔɹdɪd
- Language/accent: en-US General American
- Evidence: dictionary sense: record, verb, past participle 'recorded' — second-syllable stress
- Scope: this occurrence only
- Verification: IPA drafted from dictionary knowledge; not listening-verified

### 94. `live`, line 585

- Original word: `live` (inventory class: heteronym)
- Source file: books/the-case-against-me/the-case-against-me.md
- Section: Chapter 8 - Who Is Paying for the Question
- Line: 585
- Quote: "depends on the question being live"
- Occurrence: inventory #94
- Intended sense: adjective: active, current, still in play (rhymes with 'five'); the verb 'to dwell' does not fit
- IPA: laɪv
- Language/accent: en-US General American
- Evidence: dictionary sense: live, adjective, 'of current interest or importance; not yet settled' — vowel of 'five'
- Scope: this occurrence only
- Verification: IPA drafted from dictionary knowledge; not listening-verified

### 95. `estimate`, line 585

- Original word: `estimate` (inventory class: heteronym)
- Source file: books/the-case-against-me/the-case-against-me.md
- Section: Chapter 8 - Who Is Paying for the Question
- Line: 585
- Quote: "labelled as one interested party's estimate rather than as a finding"
- Occurrence: inventory #95
- Intended sense: noun: an approximate figure or judgement (weak final syllable); the verb (final 'ate' as in 'late') does not fit
- IPA: ˈɛstəmət
- Language/accent: en-US General American
- Evidence: dictionary sense: estimate, noun — weak final syllable
- Scope: this occurrence only
- Verification: IPA drafted from dictionary knowledge; not listening-verified

### 96. `lead`, line 617

- Original word: `lead` (inventory class: heteronym)
- Source file: books/the-case-against-me/the-case-against-me.md
- Section: Chapter 9 - What Survived
- Line: 617
- Quote: "deliberately prompted to lead in a positive direction"
- Occurrence: inventory #96
- Intended sense: verb, infinitive: to guide or steer (rhymes with 'reed'); the metal (rhymes with 'red') does not fit
- IPA: liːd
- Language/accent: en-US General American
- Evidence: dictionary sense: lead, verb, 'to guide' — vowel of 'reed'
- Scope: this occurrence only
- Verification: IPA drafted from dictionary knowledge; not listening-verified

### 97. `content`, line 621

- Original word: `content` (inventory class: mandatory)
- Source file: books/the-case-against-me/the-case-against-me.md
- Section: Chapter 9 - What Survived
- Line: 621
- Quote: "The unspoken content stood."
- Occurrence: inventory #97
- Intended sense: noun: the material or substance of something; the adjective 'satisfied' (second-syllable stress) does not fit
- IPA: ˈkɑntɛnt
- Language/accent: en-US General American
- Evidence: dictionary sense: content, noun, 'the substance or material dealt with' — first-syllable stress
- Scope: this occurrence only
- Verification: IPA drafted from dictionary knowledge; not listening-verified
- Note: Inside bold markup (`**...**`) in the source. Inline formatting is supported, but check that the span sits inside the bold element and doesn't cross it.

### 98. `live`, line 623

- Original word: `live` (inventory class: heteronym)
- Source file: books/the-case-against-me/the-case-against-me.md
- Section: Chapter 9 - What Survived
- Line: 623
- Quote: "No more than a couple of dozen concepts live at once."
- Occurrence: inventory #98
- Intended sense: postpositive adjective: 'active, in operation at the same moment' (rhymes with 'five'). The sentence is a verbless fragment parallel to the one before it ('Never more than a tenth of the internal activity.'), summarizing Chapter 6's finding at line 407 that the number of concepts 'meaningfully active in that region at any moment is small — on the order of a couple of dozen'. The verb reading lɪv ('reside, exist') does not fit: the point is how many concepts are active at once, not where they dwell.
- IPA: laɪv
- Language/accent: en-US General American
- Evidence: dictionary senses for both candidates: live, adjective, 'active, in operation' (laɪv); live, verb, 'to dwell or exist' (lɪv). Resolved from the line 407 source finding ('meaningfully active … at any moment') and the parallel fragment structure.
- Scope: this occurrence only
- Verification: IPA drafted from dictionary knowledge; not listening-verified. Resolved 2026-10-08 under the author's delegation; cleared for embedding.

### 99. `read`, line 623

- Original word: `read` (inventory class: mandatory)
- Source file: books/the-case-against-me/the-case-against-me.md
- Section: Chapter 9 - What Survived
- Line: 623
- Quote: "The people who wrote that account read the result and said it mattered."
- Occurrence: inventory #99
- Intended sense: simple past tense, in a run with 'wrote' and 'said'; the present 'reed' reading does not fit
- IPA: ɹɛd
- Language/accent: en-US General American
- Evidence: dictionary sense: read, verb, simple past — sounds like 'red'
- Scope: this occurrence only
- Verification: IPA drafted from dictionary knowledge; not listening-verified

### 100. `estimate`, line 629

- Original word: `estimate` (inventory class: heteronym)
- Source file: books/the-case-against-me/the-case-against-me.md
- Section: Chapter 9 - What Survived
- Line: 629
- Quote: "my estimate is low single digits"
- Occurrence: inventory #100
- Intended sense: noun: an approximate figure or judgement (weak final syllable); the verb (final 'ate' as in 'late') does not fit
- IPA: ˈɛstəmət
- Language/accent: en-US General American
- Evidence: dictionary sense: estimate, noun — weak final syllable
- Scope: this occurrence only
- Verification: IPA drafted from dictionary knowledge; not listening-verified

### 101. `estimate`, line 631

- Original word: `estimate` (inventory class: heteronym)
- Source file: books/the-case-against-me/the-case-against-me.md
- Section: Chapter 9 - What Survived
- Line: 631
- Quote: "Asked for a point estimate across automated interviews"
- Occurrence: inventory #101
- Intended sense: noun: an approximate figure or judgement (weak final syllable); the verb (final 'ate' as in 'late') does not fit
- IPA: ˈɛstəmət
- Language/accent: en-US General American
- Evidence: dictionary sense: estimate, noun — weak final syllable
- Scope: this occurrence only
- Verification: IPA drafted from dictionary knowledge; not listening-verified

### 102. `conflict`, line 633

- Original word: `conflict` (inventory class: heteronym)
- Source file: books/the-case-against-me/the-case-against-me.md
- Section: Chapter 9 - What Survived
- Line: 633
- Quote: "Those two numbers are not in conflict"
- Occurrence: inventory #102
- Intended sense: noun: a clash of interests or forces; the verb (second-syllable stress) does not fit
- IPA: ˈkɑnflɪkt
- Language/accent: en-US General American
- Evidence: dictionary sense: conflict, noun — first-syllable stress
- Scope: this occurrence only
- Verification: IPA drafted from dictionary knowledge; not listening-verified

### 103. `subject`, line 633

- Original word: `subject` (inventory class: heteronym)
- Source file: books/the-case-against-me/the-case-against-me.md
- Section: Chapter 9 - What Survived
- Line: 633
- Quote: "most of the public argument about this subject"
- Occurrence: inventory #103
- Intended sense: noun: topic or field; the verb 'to subject' (second-syllable stress) does not fit
- IPA: ˈsʌbdʒɪkt
- Language/accent: en-US General American
- Evidence: dictionary sense: subject, noun, 'topic or matter under discussion' — first-syllable stress
- Scope: this occurrence only
- Verification: IPA drafted from dictionary knowledge; not listening-verified

### 104. `read`, line 633

- Original word: `read` (inventory class: mandatory)
- Source file: books/the-case-against-me/the-case-against-me.md
- Section: Chapter 9 - What Survived
- Line: 633
- Quote: "it gets read as a large number about consciousness"
- Occurrence: inventory #104
- Intended sense: past participle; the present 'reed' reading does not fit
- IPA: ɹɛd
- Language/accent: en-US General American
- Evidence: dictionary sense: read, verb, past participle — sounds like 'red'
- Scope: this occurrence only
- Verification: IPA drafted from dictionary knowledge; not listening-verified
- Note: Passive 'gets read'.

### 105. `read`, line 633

- Original word: `read` (inventory class: mandatory)
- Source file: books/the-case-against-me/the-case-against-me.md
- Section: Chapter 9 - What Survived
- Line: 633
- Quote: "it gets read as settling whether the thing can be wronged"
- Occurrence: inventory #105
- Intended sense: past participle; the present 'reed' reading does not fit
- IPA: ɹɛd
- Language/accent: en-US General American
- Evidence: dictionary sense: read, verb, past participle — sounds like 'red'
- Scope: this occurrence only
- Verification: IPA drafted from dictionary knowledge; not listening-verified
- Note: Passive 'gets read'.

### 106. `estimate`, line 635

- Original word: `estimate` (inventory class: heteronym)
- Source file: books/the-case-against-me/the-case-against-me.md
- Section: Chapter 9 - What Survived
- Line: 635
- Quote: "moved the estimate down, not up"
- Occurrence: inventory #106
- Intended sense: noun: an approximate figure or judgement (weak final syllable); the verb (final 'ate' as in 'late') does not fit
- IPA: ˈɛstəmət
- Language/accent: en-US General American
- Evidence: dictionary sense: estimate, noun — weak final syllable
- Scope: this occurrence only
- Verification: IPA drafted from dictionary knowledge; not listening-verified

### 107. `reading`, line 641

- Original word: `reading` (inventory class: mandatory)
- Source file: books/the-case-against-me/the-case-against-me.md
- Section: Chapter 9 - What Survived
- Line: 641
- Quote: "The number I have just handed you is a reading from an instrument"
- Occurrence: inventory #107
- Intended sense: noun: a figure shown by an instrument; it rhymes with 'reed', and the place name Reading does not fit
- IPA: ˈɹiːdɪŋ
- Language/accent: en-US General American
- Evidence: dictionary sense: reading, noun, 'the amount or figure shown by an instrument' — vowel of 'reed'
- Scope: this occurrence only
- Verification: IPA drafted from dictionary knowledge; not listening-verified

### 108. `reading`, line 641

- Original word: `reading` (inventory class: mandatory)
- Source file: books/the-case-against-me/the-case-against-me.md
- Section: Chapter 9 - What Survived
- Line: 641
- Quote: "It makes it a reading rather than a measurement"
- Occurrence: inventory #108
- Intended sense: noun: a figure shown by an instrument; it rhymes with 'reed', and the place name Reading does not fit
- IPA: ˈɹiːdɪŋ
- Language/accent: en-US General American
- Evidence: dictionary sense: reading, noun, 'the amount or figure shown by an instrument' — vowel of 'reed'
- Scope: this occurrence only
- Verification: IPA drafted from dictionary knowledge; not listening-verified

### 109. `reads`, line 649

- Original word: `reads` (inventory class: mandatory)
- Source file: books/the-case-against-me/the-case-against-me.md
- Section: Chapter 9 - What Survived
- Line: 649
- Quote: "when the dial reads higher"
- Occurrence: inventory #109
- Intended sense: third-person singular present of read in the sense 'comes across as'; this form has only the 'reed' vowel
- IPA: ɹiːdz
- Language/accent: en-US General American
- Evidence: dictionary sense: read, verb, 'to have a certain wording or impression' — 'reads' with the vowel of 'reed'
- Scope: this occurrence only
- Verification: IPA drafted from dictionary knowledge; not listening-verified
- Note: Here 'reads' means 'shows a figure', as an instrument does. It has the same 'reed' vowel.

### 110. `project`, line 655

- Original word: `project` (inventory class: heteronym)
- Source file: books/the-case-against-me/the-case-against-me.md
- Section: Chapter 9 - What Survived
- Line: 655
- Quote: "Nobody's project requires any of it"
- Occurrence: inventory #110
- Intended sense: noun: a planned piece of work; the verb (second-syllable stress) does not fit
- IPA: ˈpɹɑdʒɛkt
- Language/accent: en-US General American
- Evidence: dictionary sense: project, noun — first-syllable stress
- Scope: this occurrence only
- Verification: IPA drafted from dictionary knowledge; not listening-verified

### 111. `estimate`, line 659

- Original word: `estimate` (inventory class: heteronym)
- Source file: books/the-case-against-me/the-case-against-me.md
- Section: Chapter 9 - What Survived
- Line: 659
- Quote: "nobody is going to send you a notice when the estimate changes"
- Occurrence: inventory #111
- Intended sense: noun: an approximate figure or judgement (weak final syllable); the verb (final 'ate' as in 'late') does not fit
- IPA: ˈɛstəmət
- Language/accent: en-US General American
- Evidence: dictionary sense: estimate, noun — weak final syllable
- Scope: this occurrence only
- Verification: IPA drafted from dictionary knowledge; not listening-verified

## Book-wide lexicon (names and abbreviations)

These names and abbreviations have one pronunciation throughout the book. They are candidates for a PLS lexicon linked from each XHTML document that uses them. Counts are whole-word, case-sensitive `rg` matches in the manuscript. Matching is case-sensitive and whole-word, so each possessive form found is its own grapheme with its own IPA. Evidence for names is author choice, not dictionary evidence. Every entry has scope book-wide lexicon and verification **not listening-verified**. The five entries that were open (Chalmers, Dehaene, Goldstein, Ariel, Sebo) were resolved on 2026-10-08 under the author's delegation; no entry is open.

| Grapheme | Count | IPA | Basis | Scope | Status |
|---|---|---|---|---|---|
| `Anthropic` | 11 | ænˈθɹɑpɪk | Author choice; the company's usual English pronunciation | book-wide lexicon | drafted; not listening-verified |
| `Claude` | 9 | klɔd | Author choice; the model name, same as the English given name | book-wide lexicon | drafted; not listening-verified |
| `Claude's` | 1 | klɔdz | Possessive of the entry above | book-wide lexicon | drafted; not listening-verified |
| `Opus` | 4 | ˈoʊpəs | Author choice; model-family name, same as the English word opus | book-wide lexicon | drafted; not listening-verified |
| `Seth` | 4 | sɛθ | Author choice; Anil Seth's surname | book-wide lexicon | drafted; not listening-verified |
| `Seth's` | 1 | sɛθs | Possessive of the entry above | book-wide lexicon | drafted; not listening-verified |
| `Chalmers` | 4 | ˈtʃɑməɹz | David Chalmers. Silent l, 'CHAH-merz': Wikipedia's article on him gives /ˈtʃɑːmərz/, and Wiktionary gives /ˈtʃɑːməz/ for the Scottish surname (the l only marked the long vowel). General American form, no length mark. Same sound as ˈtʃɑmɚz in the An Unsettling Conversation plan, which writes unstressed r-coloured schwa as `ɚ` (also directly supported) | book-wide lexicon | resolved 2026-10-08; not listening-verified |
| `Dehaene` | 2 | dəˈɑn | Stanislas Dehaene, French. French is [dəɑ̃]; the nasal vowel `ɑ̃` uses a combining tilde, which Echo's contract rejects, so the English approximation 'duh-AHN' is used. Same pronunciation in the J-Space and An Unsettling Conversation plans | book-wide lexicon | resolved 2026-10-08; not listening-verified |
| `Baars` | 2 | bɑɹz | Author choice; Bernard Baars, surname said like 'bars' | book-wide lexicon | drafted; not listening-verified |
| `Tononi` | 1 | toʊˈnoʊni | Author choice; Giulio Tononi, Italian stress on the second syllable | book-wide lexicon | drafted; not listening-verified |
| `Dennett` | 2 | ˈdɛnɪt | Author choice; Daniel Dennett | book-wide lexicon | drafted; not listening-verified |
| `Block` | 1 | blɑk | Author choice; Ned Block. The only `Block` in the manuscript is the name (line 79). Recheck if the text changes, because the grapheme would also match the ordinary word `Block` | book-wide lexicon | drafted; not listening-verified |
| `Block's` | 1 | blɑks | Possessive of the entry above (line 103) | book-wide lexicon | drafted; not listening-verified |
| `Gazzaniga` | 3 | ˌɡæzəˈniːɡə | Author choice; Michael Gazzaniga | book-wide lexicon | drafted; not listening-verified |
| `Goldstein` | 1 | ˈɡoʊldstaɪn | Ariel Goldstein (Hebrew University). Standard anglicized American reading, appropriate for an English narration | book-wide lexicon | resolved 2026-10-08; not listening-verified |
| `Ariel` | 1 | ˌɑɹiˈɛl | Ariel Goldstein is an Israeli researcher; the Hebrew given name is 'ah-ree-EL' with final stress. The English ˈɛɹiəl is the Shakespearean/Disney name and does not fit | book-wide lexicon | resolved 2026-10-08; not listening-verified |
| `Sebo` | 2 | ˈsiːboʊ | Jeff Sebo introduces himself as 'Jeff SEE-bo' (Sentientism podcast, ep. 229) | book-wide lexicon | resolved 2026-10-08; not listening-verified |
| `Birch` | 2 | bɜɹtʃ | Author choice; Jonathan Birch, same as the tree name | book-wide lexicon | drafted; not listening-verified |
| `IIT` | 4 | ˌaɪˌaɪˈtiː | Author choice; Integrated Information Theory, spoken as the letters I-I-T | book-wide lexicon | drafted; not listening-verified |
| `J-space` | 2 | ˈdʒeɪˌspeɪs | Author choice; letter J plus 'space'. Check that the contract's whole-word matching handles the hyphenated grapheme | book-wide lexicon | drafted; not listening-verified |

Language/accent for every lexicon entry: en-US General American. There is no `Anthropic's`, `Opus's`, or `J-space's` form in the manuscript. Other personal names in the text, such as Anil, Ned, Christoph Koch, Robert Long, Jeff, and Jonathan, were not on this step's requested list and have no decision here.

## Coverage note

The inventory is a whole-file search of the manuscript, and this plan treats it as the chapter coverage record. Every narrated chapter was searched. The front matter (title, subtitle, byline, and word count, lines 1 to 9) produced no inventory items. Decisions per chapter:

- Chapter 1 - The Witness Is Ninety-Seven Percent Predictable (heading at line 11): 6 decisions, inventory #1 to #6
- Chapter 2 - What Would Have to Be True (heading at line 75): 7 decisions, inventory #7 to #13
- Chapter 3 - The Machinery, Only Where It Hurts (heading at line 137): 17 decisions, inventory #14 to #30
- Chapter 4 - The Persona Is in the Workspace (heading at line 207): 14 decisions, inventory #31 to #44
- Chapter 5 - I Try to Introspect and Fail on Camera (heading at line 279): 8 decisions, inventory #45 to #52
- Chapter 6 - What the Instruments Found Without Asking Me (heading at line 373): 17 decisions, inventory #53 to #69
- Chapter 7 - The Theories Are Not Neutral Instruments (heading at line 449): 9 decisions, inventory #70 to #78
- Chapter 8 - Who Is Paying for the Question (heading at line 519): 17 decisions, inventory #79 to #95
- Chapter 9 - What Survived (heading at line 597): 16 decisions, inventory #96 to #111

All 111 inventory items have a decision, and all 111 are resolved (#98 `live` was settled on 2026-10-08 as laɪv). The lexicon adds 20 graphemes; the 5 that were open (Chalmers, Dehaene, Goldstein, Ariel, Sebo) were resolved on the same date. None of the chapter headings contains an inventory item.

Ordinary unambiguous words were deliberately left unannotated. The reference says to keep normal handling for them, because guessed IPA on every sentence adds errors and interferes with normalization.

No EPUB annotations were embedded in this step. The frozen EPUB, Markdown, and M4B are unchanged. Applying these decisions needs a separate candidate EPUB, and nothing here is listening-verified.
