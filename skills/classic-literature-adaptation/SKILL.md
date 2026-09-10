---
name: classic-literature-adaptation
description: Translate or adapt classic literature into clear, beautiful modern English while preserving source meaning, with optional play, prose, and audiobook editions. Use for faithful Shakespeare modernization or original-language classics such as Homer; not for summaries or freely reinvented retellings.
---

# Classic literature adaptation

Make the work understandable without silently changing what happens, what is said,
or what remains uncertain. Aim for semantic fidelity and literary force; do not
promise an exact equivalent for every word or certainty about an author's intent.

Prioritize understanding over brevity. Default to clear, adult everyday English
that gives a reader unfamiliar with the classic enough room to follow each thought.
Use more words when the original compresses several meanings; matching its brevity
or line length is not a fidelity goal. Preserve literary force without making the
reader decode archaic vocabulary, dense syntax, or unexplained euphemisms.

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

Unpack compressed sentences into a readable sequence of thoughts. Make referents
and connections explicit where the source supports them, so the reader can follow
what is said, how the argument develops, and what a joke or insult means. Preserve
effective imagery; explain an opaque image in a separate note when replacing it
would narrow its meaning. Expansion should clarify the passage, not repeat it,
pad its length, or turn the speaker's words into a running commentary.

Distinguish explanatory additions from explicit source statements. Record material
expansions in the working ledger and disclose an explanatory translation approach
in the edition's method note. Keep disputed implications and possible motives in
separate notes rather than inserting them as facts or invented speech. A simpler
sentence must not silently settle an ambiguity or claim access to private thoughts.

Keep obscenity, sexual acts, threats, and prejudices as explicit as the source.
Use understandable language without euphemistic censorship or added shock value.
When an insult has no close modern equivalent, preserve its function and explain
the cultural meaning separately rather than substituting a misleading modern label.

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

## Help the listener follow while driving

For audiobook editions, default to a little more explanation than the written
adaptation alone. Assume a first-time listener who cannot look at footnotes or
rewind every dense exchange. Shakespeare in particular can compress an argument,
an insult, and a change in the relationship into a few words. Give those thoughts
room to land while preserving the complete scene and its momentum. Follow an
explicit request for an unannotated performance instead when given.

Use Michael (`am_michael`) as the explanatory guide, subject to renderer support
and any later voice preference. Keep guide passages in separate, explicitly
identified manuscript paragraphs and renderer blocks, distinct from character
speech. Introduce the guide's function briefly in the opening method note. Make
transitions understandable by ear as well as by voice: use a short cue such as
“Notice what she is asking here” when needed. If Michael also narrates the story
or voices a character, the wording must still identify the commentary clearly.

At scene openings, briefly establish who is present, who is speaking to whom, and
the immediate situation when that would otherwise be hard to follow. After a
dense exchange or at a natural pause, let the guide unpack the useful missing
connection: what an image means here, how a joke or insult works, what is being
asked or risked, or how the response shifts the balance between the speakers.
Prefer one to three conversational sentences; use more when a difficult passage
needs it. Scale explanation to difficulty rather than adding a note after every
speech. A brief reminder of a name, relationship, or earlier promise can help a
listener rejoin the scene. Keep necessary explanation beside the relevant passage,
not solely in endnotes, and avoid spoilers beyond the listener's current position.

Let Michael read between the lines, grounded in the passage and context. Separate
literal meaning from inference with natural wording such as “The implication is”
or “One way to hear that is.” Present a consequential alternative when a reading
is disputed. Do not turn a possible motive into a fact, invent inner thoughts,
or attribute the guide's explanation to Shakespeare or a character. Explain the
specific exchange rather than delivering a general lecture or paraphrasing it twice.

Track guide additions separately in the source-to-output ledger, with the source
units and evidence they explain. Include them in the fidelity and comprehension
reviews. Finalize spoken guidance before freezing the EPUB and mapping the actual
renderer blocks to the guide role; it is part of the narrated text, not an audio-only
addition that would break text/audio synchronization. This preference governs new
audio adaptations, not permission to revise an already accepted manuscript or render.

## Pronunciation for listening editions

Follow `../echo-narration/references/epub-pronunciation.md` when preparing audio.
Review every occurrence of content, record, and read, including Michael's guide
passages, as well as names and archaic uses whose intended meaning affects sound.
Maintain the source-linked pronunciation plan; put IPA into the EPUB through the
verified Echo contract before freezing it. Keep disputed readings visible in the
plan and review choices against the source. For manuscript-only work, hand off
known decisions without starting packaging or narration.

## Review and deliver

Use independent adversarial AI review before accepting a translation or adaptation,
following [Adversarial review](references/adversarial-review.md). Prefer Cursor CLI
with an explicitly selected available Grok model. Review both source fidelity and
reader comprehension in fresh sessions; a model's approval is not scholarly proof.
Resolve findings against the source, recheck material revisions, and report actual
coverage and any unavailable review separately from manuscript completion.

Review the entire adaptation against the source in manageable batches, with a
second focused pass on difficult meanings, speaker attribution, and consequential
numbers or conditions. Check the ledger, chapter order, names, and unresolved
interpretations. Review literary quality separately so polishing does not silently
change meaning. Record the actual review performed and outstanding limitations.
Do not claim a scholar or human listener has reviewed material when they have not.

Also review for comprehension by a reader unfamiliar with the work: can they follow
each thought, identify its referents, and understand the stakes without decoding
the original idiom? Expand passages that remain needlessly compressed, then check
those expansions against the source for added claims or lost uncertainty.

Credit the original author and identify the modern adapter/translator separately.
Include the source edition and a concise explanation of the adaptation method.
Keep private working packages outside Git. Publication requires the applicable
user authorization and rights check; an original-fiction publication shortcut does
not establish eligibility for an adaptation.

When audio is requested, use the available fiction-audiobook and Echo narration
workflow for packaging and verified rendering, retaining these fidelity constraints.
Follow `../echo-narration/references/complete-delivery.md`: every audiobook
requires the M4B, matching alignment sidecar, EPUB, portrait and square covers,
and private iCloud delivery. Do not stop at an adapted manuscript or local EPUB.
Do not apply original-story invention or length targets to an existing classic.
For a cast, freeze the EPUB first, export the actual renderer block inventory, and
map roles to those blocks. Preserve explicit speaker identities even when voices
are doubled. Check current voice preferences and supported limits; do not assume
one unique voice per character. Keep original-author metadata through the audio
export. Create original, coordinated portrait and square cover art for every
audiobook edition; preserve accepted art on redos unless changes are authorized.

A requested renderer revision is an independent tooling requirement: inspect the
current install/verification contract and use its supported build workflow. Do not
rebuild Echo simply because a book uses this skill. Report manuscript completion,
package checks, render verification, delivery, and human listening as distinct states.
