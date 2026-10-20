# Extra vowel before IPA-tagged words

Scope: grok-bots #256, broadened to all IPA annotations, not only #252/#257's
GitHub report. No paid synthesis or re-narration was performed.

## Finding

No demonstrated cause was found. Repository serialization preserves both the
supplied IPA and the surrounding visible text. There is no local rule that
prefixes all annotated words with a vowel. No production fix is justified by
this evidence. The affected narration's exact input, selected renderer revision,
and token-level pronunciation audit are still needed to identify its cause.

The Echo source trace below was read from an available checkout at revision
`6ade93a3340db9b03d08c213d9c50d824c231171`; this does not establish that the
reported narration used that revision or that an installed renderer includes it.
Echo paths below are relative to that repository.

## Serialization and engine boundary

1. Here, `skill/scripts/build_book.py::build` escapes Markdown into XHTML and
   invokes `epub_pronunciation.py::apply_dictionary`. The latter calls `apply`.
   `apply` inserts the supplied, XML-escaped IPA in
   `<span ssml:ph="ˈɡɪtˌhʌb">GitHub</span>` (shared defaults additionally carry
   `data-pronunciation="shared"`). The display word and adjacent text are copied
   unchanged. `build_pls` serializes lexicon IPA as `<phoneme>…</phoneme>` inside
   a PLS lexeme. This is PLS XML, not an SSML synthesis `<phoneme>` request.
2. `skills/echo-narration/scripts/echo_pronunciation_narrate.sh` constructs
   `narrate_command` with `"$CLI" narrate --epub "$EPUB"` plus output, sidecar,
   voice and runtime arguments. It does not extract speech text, concatenate
   phonemes, or submit an HTTP TTS request. No alternative SSML or paid TTS
   request implementation was found in either scripts directory.
3. Echo's `Shared/EPUBPronunciation.swift`:
   `EPUBPronunciationIPA.normalize` converts supported IPA to Kokoro notation
   (for example eɪ → A), validates it, and does not prepend vowels.
   `EPUBInlinePronunciationTracker.end`/`flush` retain inline display offsets and
   IPA. `EPUBPLSParser` and `EPUBPronunciationImport.applyLexicons` produce the
   same span representation for lexicon matches, preserving inline priority.
4. `EchoCore/Services/Narration/EPUBPronunciationRewriter.swift::rewrite`
   replaces each addressed word with `[word](/ipa/)`. For this example the
   downstream G2P text is `Before [GitHub](/ˈɡɪtˌhʌb/), after.`. Both EPUB
   span sources converge here. `NarrationRenderPlan` invokes this rewriter
   before the other pronunciation resolvers and planning.
5. `ThirdParty/MisakiSwift/Sources/MisakiSwift/English/EnglishG2P.swift`:
   `preprocess` removes the link syntax from display text and records its IPA
   feature; it removes the closing slash. `tokenize` recognizes the opening
   slash and removes it, assigning the remaining phonemes once to the linked
   phrase. Correctly consumed delimiters do not become spoken tokens.
   `phonemizeWithMetadata` assembles token phonemes and whitespace.
6. `KokoroG2P.result` consumes that result.
   `PronunciationPlanner.plan` validates it through
   `KokoroPhonemeVocab.validatedIDs`, adding boundary IDs around the mapped
   phonemes. `OnnxKokoroEngine.plannedInputs` uses those immutable IDs;
   `runModel` submits ONNX tensors `input_ids`, `style`, and `speed`. The final
   engine receives IDs, not EPUB markup, an SSML document, or raw IPA prose.

## Relevant leads, not established causes

`EnglishFallbackNetwork.phonemes(for:)` returns `ə` when its assembled fallback
is empty. `EnglishG2P.voicedPhonemes` also rescues unvoiced letter-bearing tokens.
A stray unconsumed token could therefore generate additional speech. However,
`tokenize` supplies explicit phonemes for valid links, and `needsVoicedFallback`
does not trigger for such nonempty, valid phonemes. There is no evidence linking
an extra fallback token to the reported audio.

Local Git history lists `69b25ed`, “bind pronunciation spans after Unicode
preprocessing (#602)”. Current `preprocess` stores UTF-16 offsets and binds
indices only after constructing the final string; `tokenize` emits linked phrase
IPA once. This is relevant to annotation handling, but the historical patch could
not be fetched from the partial checkout while GitHub was unreachable. It is not
proof of either the symptom's cause or its repair in the installed renderer.

## Verification and limits

`tests/test_epub_pronunciation.py::test_exact_ipa_serialization_preserves_surrounding_text`
asserts the exact full paragraph around consonant-initial and vowel-initial IPA
words, including Unicode quotes and punctuation, the entire PLS document, and
unchanged display text. It passes. This is boundary coverage, not a fail-before
regression for a demonstrated vowel-insertion bug; no such fix is claimed.

The local Swift executable cannot start because `libncurses.so.6` is missing,
so the Echo G2P/token-ID path was inspected but not executed. No Echo files were
modified. A decisive reproduction needs the affected block, annotation spans,
resolved G2P input, per-token selected phonemes/IDs, and actual renderer identity;
compare whether an extra vowel ID exists before synthesis or appears only in
its acoustic output.
