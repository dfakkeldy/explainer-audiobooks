---
name: classic-literature-adaptation
description: Translate or adapt classic literature into clear, beautiful modern English while preserving source meaning, with optional play, prose, and audiobook editions. Use for faithful Shakespeare modernization or original-language classics such as Homer; not for summaries or freely reinvented retellings.
---

# Classic literature adaptation

Make the work understandable without silently changing what happens, what is said,
or what remains uncertain. Aim for semantic fidelity and literary force; do not
promise an exact equivalent for every word or certainty about an author's intent.

## Establish the edition

Infer the requested scope from the conversation: complete work or excerpt, modern
English modernization or translation from another language, and requested formats.
Do not turn a manuscript request into an audiobook or start a mentioned future book.
Default to the original setting with accessible language. Relocating events to
modern society can change meaning and needs a different adaptation brief.

Obtain and record an identified source edition, editor, language, source URL,
retrieval date, and local checksum. Use stable book/line or act/scene/speech
references. Inspect the text itself, including speaker labels and stage directions;
web transcriptions can contain omissions, duplicated labels, and broken boundaries.
Record corrections with supporting edition evidence instead of silently repairing
by intuition. Public-domain works may have copyrighted modern translations or
editorial material: establish rights for the actual text used.

For a source in another language, read
[Original-language translation](references/original-languages.md). An English
translation used as the base makes the result an adaptation of that translation;
do not describe it as a translation directly from Greek or another original language.

## Preserve the source's decisions

Create a practical source-to-output ledger before long-form drafting. Give each
speech, verse passage, or other meaningful unit a stable ID. Map every unit to its
output span, allowing explicit splits. Track directions, songs, embedded quotations,
and asides separately where needed. Check for omitted, duplicated, misplaced, or
misattributed units. Coverage is necessary evidence, not proof of equivalent meaning.

Draft in coherent scenes or passages. Preserve who knows what, who speaks to whom,
argument and counterargument, negation, conditions, promises, threats, quantities,
and changes of mind. Keep an ambiguity ambiguous when resolving it would alter the
reading. Maintain a small ledger for names, relationships, key terms, and difficult
passages. Use it across chapters and across alternate editions.

Replace obsolete syntax and idioms with living English that performs the same
function. Preserve the force of jokes, insults, imagery, repetitions, and formal
speeches. Where a pun cannot survive, preserve the scene's action and explain the
loss in a note. Read passages aloud for rhythm and character voice. Do not flatten
verse into a plot report or add fashionable slang that changes status or tone.

Keep cultural realities and prejudices legible, including uncomfortable ones.
Explain institutions, money, religious references, and customs in separate reading
notes when a small in-text clarification would distort the speech. Distinguish
what the source states, a contextual explanation, and a contested interpretation.
Notes should help the reader understand; they should not prescribe a single moral
judgment or claim privileged access to the author's mind.

## Shape the requested editions

- **Play:** retain speaker identities, scene boundaries, directions needed for
  action, and the distinction between public speech and private asides.
- **Novel or prose edition:** preserve the complete dramatic or narrative content.
  Add only bridges needed to make visible action and speech attribution readable.
  Ground them in the source. Do not invent private motives, backstory, or outcomes
  unless the user has requested a freer retelling. Describe a dialogue-rich prose
  adaptation honestly rather than padding it to meet an arbitrary novel length.
- **Poetic source:** choose readable verse or rhythmic prose to suit the request.
  Preserve meaningful repetitions and shifts of register; they are not automatically
  prose defects. Keep source line references in the working ledger even when English
  lineation changes.

Reuse verified meaning across alternate editions, then inspect format-specific
bridges and omissions. Do not treat a matching word count as fidelity evidence.

## Review and deliver

Review the entire adaptation against the source in manageable batches, with a
second focused pass on difficult meanings, speaker attribution, and consequential
numbers or conditions. Check the ledger, chapter order, names, and unresolved
interpretations. Review literary quality separately so polishing does not silently
change meaning. Record the actual review performed and outstanding limitations.
Do not claim a scholar or human listener has reviewed material when they have not.

Credit the original author and identify the modern adapter/translator separately.
Include the source edition and a concise explanation of the adaptation method.
Keep private working packages outside Git. Publication requires the applicable
user authorization and rights check; an original-fiction publication shortcut does
not establish eligibility for an adaptation.

When audio is requested, use the available fiction-audiobook and Echo narration
workflow for packaging and verified rendering, retaining these fidelity constraints.
Do not apply original-story invention or length targets to an existing classic.
For a cast, freeze the EPUB first, export the actual renderer block inventory, and
map roles to those blocks. Preserve explicit speaker identities even when voices
are doubled. Check current voice preferences and supported limits; do not assume
one unique voice per character. Keep original-author metadata through the audio
export. Use original, coordinated portrait and square cover art if requested.

A requested renderer revision is an independent tooling requirement: inspect the
current install/verification contract and use its supported build workflow. Do not
rebuild Echo simply because a book uses this skill. Report manuscript completion,
package checks, render verification, delivery, and human listening as distinct states.
