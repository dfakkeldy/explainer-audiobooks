# Claims ledger plan

How each chapter rewrite produces `review/claims/chNN.md`, so that a later adversarial reviewer can
prove that every factual, legal, numeric and dated claim of the original survives in the textbook,
unchanged in meaning, and that the textbook adds no claim of its own.

The original is frozen: `books/beyond-the-tax-sale-packet/beyond-the-tax-sale-packet.md` (cited as
`md:LINE`; Markdown SHA-256 `6a636ec2…b670` per the book README). If that hash ever changes, stop:
every ledger's line numbers are void.

## 1. What counts as a claim

A claim is any statement a reader could check against a source or could act on. Each is one atomic
proposition: split a sentence that carries two facts; never merge two sentences into one claim.

| Type | Code | Examples from the original |
|---|---|---|
| Legal rule | L | "the treasurer may, with council's consent, call for tenders" (`md:87`); deed vests fee simple free of encumbrances (`md:953–955`) |
| Number or amount | N | 45 lien entries; 44 sheets (`md:37`); 4.53 median (`md:1069`); $608,693.21 (`md:1079`); 10% interest (`md:299`) |
| Date or period | D | June 30 (`md:65`); 14/60/30 days (`md:71–75`); September 11, 2025 (`md:773`); January 1, 2027 (`md:1143`) |
| Factual (non-legal) | F | the Inverness packet contains an aerial image with a property overlay (`md:23`); Touquoy later produced gold (`md:629`) |
| Source attribution | S | "Current CBRM guidance supplies…" (`md:993`); "the Province states" (`md:1139`); who said what |
| Limitation or boundary | Q | "A parcel shape is not a boundary survey" (`md:31`); "Neither result proves no flood hazard" (`md:601`) |
| Method or rule of practice | M | preserve both amounts and ask the municipality (`md:165`); the six-part note (`md:603–607`) |
| Composite-case fact | C | Harbour Road's recovery amount is $4,000 (`md:193`); Maple Ridge lies behind two roadside lots (`md:695`) |
| Privacy boundary | P | the brook is left unnamed (`md:623`); Harbour Road stays owner-free (`md:129`) |
| Figure content | G | every label, number and source string inside an original figure, and its alt text |

Qualifiers are part of the claim and are quoted with it: "may", "normally", "subject to", "about",
"roughly", "approximately", "currently", "in the checked build", "as of", "for this event".
Losing or strengthening a qualifier is a change, not a rewording (`cs/textbook-pdf/references/editions.md`:
"Small rewordings flip meaning").

Not claims (recorded only as a count, so the reviewer can see nothing was skipped): rhetorical
questions answered elsewhere, scene-setting without checkable content ("The auction room is still
waiting at the other end of that work"), transitions, and audio-only signposting ("road listener",
"Return to…", "Now imagine an interruption"). When in doubt, it is a claim.

## 2. Extraction (done before writing the chapter)

1. Copy the chapter's line range (front matter `md:1–9`; Ch1 `11–107`, Ch2 `109–247`, Ch3
   `249–343`, Ch4 `345–465`, Ch5 `467–689`, Ch6 `691–805`, Ch7 `807–943`, Ch8 `945–1049`,
   Ch9 `1051–1165`, Ch10 `1167–1275`, Ch11 `1277–1369`, Ch12 `1371–1495`, Ch13 `1497–1613`).
2. Split it into sentences (list items and block-quote lines count as sentences). Record the total.
3. Classify every sentence as claim-bearing or non-claim. Atomize claim-bearing sentences into
   numbered claims `chNN-001`, `chNN-002`, … in reading order. Each claim records its `md:` line and
   an exact quotation (the shortest span that carries the whole claim, qualifiers included).
4. Add the chapter's figures: for each original figure placed in the chapter, one G claim per label
   group (read the PNG at full size), one for the alt text, one for any source string in the image
   (e.g. "Sources: MGA ss. 134, 137-142, 150, 152, 155-156 • law checked 2026-07-19").
5. Attach the evidence ID where one exists (`docs/nova-scotia-tax-sale-book/research/evidence-notes.md`,
   `fact-pack.md`, and the `specificClaims` per section in `learning-outline.json`), else "—".
   Evidence IDs are for source notes; they are never a reason to change the original's wording.
6. Mark any claim that looks wrong, inconsistent or perishable with `⚑` and add it to
   `review/flagged-claims.md` (keep the claim; do not fix it).
7. Commit the extracted ledger *before* drafting, so the extraction cannot drift toward the draft.

## 3. Mapping (done while and after writing)

Each claim gets a destination and a status:

| Status | Meaning | Destination field |
|---|---|---|
| `kept` | Same proposition in the rewrite, same qualifiers, same numbers | file + heading path + exact rewrite quote |
| `kept-figure` | Carried by a figure or table in the same chapter | figure id or table caption + the label text |
| `kept-note` | Carried by a source note, glossary entry or caption | block + exact quote |
| `moved` | Appears in another chapter | `→ chMM` + heading + quote; the receiving ledger lists it under "Arrived" |
| `merged` | Stated once for two or more original claims that are identical in content | the surviving claim number, and the rewrite quote; both originals point to it |
| `flagged-kept` | Kept as printed, with a flag in `flagged-claims.md` | as `kept` + flag id |
| `non-claim` | Only for the sentence counts in §2 | — |

There is no status for "dropped". A claim that seems redundant is `merged`, never omitted. Repeated
statements of the same rule across chapters (the original recaps on purpose) may be merged only if
the receiving text is in the same chapter or a cross-reference ("see section 3.2") points to it; the
reviewer checks the cross-reference resolves.

Numbers may change form, not value: "forty-five" → "45", "ten percent" → "10 percent", "July
twentieth" → "July 20". Record the original and rewrite forms when they differ.

The destination quote must be at least six consecutive words copied from the chapter file (or the
whole label for a figure), so a script can find it.

## 4. The ledger file format: `review/claims/chNN.md`

```markdown
# Claims ledger — Chapter NN: <textbook title>

Original: md:<start>–<end> (<n> sentences; <c> claim-bearing; <x> non-claim).
Rewrite: src/chapters/NN-<slug>.md (draft <date>, SHA-256 <hash of the chapter file>).
Figures in this chapter: <ids>.

| # | md | Type | Original (exact) | Status | Destination | Rewrite (exact) | Evid. | Note |
|---|---|---|---|---|---|---|---|---|
| ch01-001 | 23 | F | "Its August 2026 packet is a substantial document." | kept | §1.1 The packet… | "Its August 2026 packet is substantial" | DATA-005 | |
| ch01-014 | 65 | D,L | "not before June thirtieth of the following year" | kept | §1.2 / fig-01-pre-sale-timeline | "not before June 30 of the following year" | LAW-002 | number form |
| … |

## Arrived from other chapters
| # | From | Destination | Rewrite (exact) |

## Apparatus added in this chapter (must introduce no new claims)
| Item | Text (exact) | Supporting claim numbers |
| Objective 2 | "Put the pre-sale steps in order…" | ch01-016, ch01-018, ch01-020 |
| Summary bullet 3 | … | … |
| Question 4 / Answer 4 | … | … |
| Caption fig-01-pre-sale-timeline | … | … |
| Glossary entry "tax lien" | … | ch01-011 |

## New statements not in the original
(Must be empty, or each row approved in review/open-questions.md with its source.)

## Counts
Sentences <n>; claims <c>; kept <k>; kept-figure <f>; kept-note <o>; moved out <m>; merged <g>;
flagged-kept <q>; arrived <a>. Check: k + f + o + m + g + q = c.
```

## 5. Apparatus rules (objectives, key terms, summaries, questions, answers, captions, glossary)

- Every factual sentence in apparatus cites at least one ledger claim from the same chapter (or a
  prior chapter for cumulative questions). Apparatus may select and restate; it may not generalize
  ("municipalities require photo ID" from CBRM's event rule is a new, false claim).
- Questions may test application to the composite cases only with facts the cases already have.
- Answers repeat the original's limits: an answer that says "the deed gives clean title" fails.
- Captions of REDRAW and NEW figures list their supporting claims in the ledger; every figure label
  must trace to a G claim (original figure) or to claims at the cited lines (NEW figure).
- Glossary definitions (`src/glossary-draft.yaml`) cite their claim numbers in the ledger of the
  chapter where the term is defined; abbreviation expansions that the original never spells out
  (e.g. HST) are listed in `review/open-questions.md`.

## 6. Source notes

Each `::: source` note lists the sources behind the section it closes: the publisher and title from
`research/sources.md` (with its retrieval or refresh date) and the evidence IDs. Section numbers come
only from `evidence-notes.md` and the original figures' source strings; a section number that
appears in neither is not printed. The ledger records each source note as apparatus with the claims
it supports, so the reviewer can check that every L, N and D claim in the section has a source.

## 7. Checks

Run at the end of each chapter and before review (scripts to be written in the build phase under
`review/tools/`; until then the reviewer runs them by hand):

1. **Coverage:** every claim number has a status; the counts balance; no status is "dropped".
2. **Original quotes exist:** every "Original (exact)" string is found at or near its `md:` line in
   the frozen file (whitespace-normalized).
3. **Rewrite quotes exist:** every destination quote is found in the named chapter file, figure spec
   or glossary (whitespace-normalized, Markdown marks stripped).
4. **Numbers:** every number, amount, percentage and date in the rewrite chapter appears in some
   claim's rewrite quote, apparatus row, or is a page/section/figure reference. Any other number is a
   new claim and fails.
5. **Qualifiers:** for each claim whose original contains a qualifier word (may, normally, subject
   to, about, roughly, approximately, currently, generally, can, appears, likely), the rewrite quote
   contains the same or an equivalent qualifier; the reviewer approves each equivalence.
6. **Privacy:** no eight-digit identifier other than the five the original prints; no owner,
   occupant, brook or extra address (mirrors the book.yaml forbid list).
7. **Moved claims:** every `moved` row has a matching "Arrived" row in the receiving ledger.

## 8. Adversarial review protocol

A reviewer (a second model, e.g. via the codex-debate skill, or a person) receives the frozen
original chapter, the rewrite chapter, its ledger, the figure PNGs and SVGs, and
`flagged-claims.md`. The brief:

1. Read the original chapter cold and list every claim you find, before opening the ledger. Compare
   your list with the ledger; any claim the ledger lacks is a finding.
2. For a random sample of at least 30% of claims (100% for L, N and D types), compare original and
   rewrite side by side, quoting both. Report any change of meaning, scope, qualifier, date, number,
   actor ("may" → "must"; "CBRM says" → "municipalities say"; "in the checked build" dropped).
3. Read the rewrite chapter cold and list every claim in it; any claim not mapped to the ledger is a
   new claim and a finding.
4. Check every figure label against its listed facts.
5. Verdict per finding: accepted (fix), partly, or rejected with evidence. Iterate on the same
   thread until "approve". Log rounds in `review/REVIEW-LOG.md`.

The reviewer does not check the original against the outside world; disagreements with sources go
to `flagged-claims.md` for Dan, never into the text.
