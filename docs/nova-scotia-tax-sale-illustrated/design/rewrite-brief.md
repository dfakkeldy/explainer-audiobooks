# Rewrite brief: *Beyond the Tax-Sale Packet*, textbook edition

Dan's instruction (2026-10-23): "See how the writing is. I seem to remember it being annoyingly
over-qualifying of every paragraph. 'This doesn't mean that' and 'x doesn't mean y' and the like.
It's annoyingly too much." He also asked for a textbook-style PDF with lots of good infographics.

Measured before the rewrite: about one sentence in four (19–27% per chapter) carries a negative
construction, and most of them are the same move: say what a record is, then list three to six
things it is not.

## Who reads it

Nova Scotians meeting a municipal tax sale for the first time: curious residents, first-time
bidders, owners or families behind on taxes, journalists, students. They read on paper or a
screen. Afterwards they should be able to follow the whole process from unpaid tax to deed, read
a notice, build a dated research file, and know which authority or professional answers each
question.

## Voice

- Plain, direct, warm, confident. Second person ("you") where it helps. Canadian spelling
  (neighbour, colour, licence as a noun).
- Say what a thing **is**, what it **does**, and **where the next answer lives**.
  "The PID finds the mapped parcel. A surveyor answers where the boundary sits on the ground."
  not "The PID does not establish the boundary. It is not a survey. It does not prove access."
- Short paragraphs. Most sentences under 25 words. Active voice.
- Define each technical term once, in **bold**, at first use in the book's order. Later chapters
  may remind in a clause.
- Keep the stories: the Port Hood auction room, Harbour Road and the other composite cases. Say
  once, when each case first appears, that it is a fictional composite. Don't repeat that label.

## The core fix

1. **Each limit once, where it does work.** If a limit has legal or financial consequence, state
   it in one plain sentence, or put it in a `::: careful` panel (at most two per chapter). Then
   move on. Never restate it in the next paragraph, the chapter closer or a figure caption.
2. **Banned moves.** Rewrite every instance:
   - "X is not Y. It is Z." Write "X is Z."
   - "This/That does not mean…", "does not prove…", "does not establish…", "cannot tell you…"
     chains after a positive statement.
   - "Neither A nor B nor C can…" disclaimers.
   - Hedge words: *silently, quietly, merely, simply, impersonating, deliberately, actually,
     genuinely*, and "rather than" used as a second disclaimer.
   - Ritual closers that restate the boundary ("The packet still cannot…", "None of this proves…").
   - "Educational information only" and professional-advice disclaimers. The front matter and one
     boundary page carry those for the whole book.
3. **Budget.** At most **8% of sentences** may contain a negative word (not, cannot, can't,
   doesn't, don't, isn't, never, neither, nor, no longer). Check with
   `python3 design/hedge_count.py <file>`. A negative is fine where a reader would genuinely make
   the mistake and the mistake costs money or rights (for example: the six-month redemption right
   is lost when taxes were more than six years in arrears at the sale). Spend the budget there.
4. **Positive routing.** Replace "the map cannot tell you about access" with "access is a
   registry and legal question: the deed, the plans, and a lawyer's opinion answer it."

## What must survive exactly

- Every fact, number, date, count, statute rule, deadline, percentage, municipal example and
  dated source state in the original chapter. If you drop a fact, list it in your notes and why.
- Qualifiers that carry legal meaning: "may", "normally", "subject to", "at least", "about",
  "with council's consent", "as of <date>". A rewording that flips meaning is the worst failure.
  (A past project turned "limit work from May to October" into the permitted season.)
- Chapter 5's mineral-occurrence / gold-panning lesson: keep its substance and keep the brook and
  property location private.
- Privacy rules: no owner names; Property Online material stays out (one short sentence explaining
  why is enough); no live parcel is singled out as a recommendation.
- The educational purpose: the book explains a process and research method. It never ranks
  properties, predicts value or tells anyone to bid.

## Length

Aim for 60–75% of the original chapter's words. The cuts come from repetition: the original
restates the same boundary several times per chapter. Keep teaching content, examples, numbers
and the human frame.

## Format (textbook-pdf engine, Pandoc Markdown)

Write `src/chapters/NN-slug.md`:

```
---
label: "N"
intro: "One or two plain sentences: what this chapter teaches."
running_head: "Short title"
---

# Chapter title

Opening paragraphs…

## Section heading

…
```

- `##` for sections, `###` rarely. Sentence case. No numbered headings.
- `::: careful` … `:::` — at most two per chapter, for the limits that cost money or rights.
- `::: note` … `:::` — a worked example or case box (Harbour Road's file, a dated count).
- `::: {.rail label="Try it"}` … `:::` — one or two short retrieval questions per chapter, the
  question then the answer in the next paragraph starting "**Answer:**".
- `::: source` … `:::` — at the end of the chapter: the official sources this chapter relies on,
  as a short list (statute and section, municipal page or packet with its date). Draw them from
  `research/evidence-notes.md` (claim IDs in `research/fact-pack.md`). No claim IDs in the text.
- Figures: put a marker line `<!-- figure: ID -->` on its own line, after the paragraph that
  introduces the idea, for each figure ID listed for your chapter in `design/figures.yaml` (the `chapter:` field).
  Use every listed ID once, in a sensible order. Don't write captions; they live in the figure plan.
- No hard line wraps: one paragraph per line. No manual spacing. Lead-ins ("Before the sale:")
  as their own paragraph.
- Abbreviations: spell out at first use in each chapter ("Parcel Identification Number (PID)").
  Don't invent new abbreviations.

## Chapter titles

| # | Original | New |
|---|---|---|
| 1 | The Last Scene First | The Last Scene First |
| 2 | What the Notice Says—and Does Not Say | Reading the Notice |
| 3 | The Six-Month Door | The Six-Month Door |
| 4 | Give the Parcel a Biography | Give the Parcel a Biography |
| 5 | The Map Is a Question Machine | The Map Is a Question Machine |
| 6 | The Driveway That May Not Be a Right-of-Way | Access and Use |
| 7 | The Things a Map Cannot Smell | On, In and Under the Land |
| 8 | Title Is Not Possession | Title, Burdens and the People on the Land |
| 9 | The Number You Decide Before the Room | The Number You Decide Before the Room |
| 10 | When the Card Goes Up | When the Card Goes Up |
| 11 | The Certificate-Holder Months | The Certificate-Holder Months |
| 12 | The Deed Is a Beginning | The Deed Is a Beginning |
| 13 | A File That Knows Its Limits | A File That Knows Its Limits |

## Your notes (return these)

Write `design/rewrite-notes/NN.md` with:
- words and hedge count before and after (from `hedge_count.py`);
- every fact you dropped or merged, with the reason;
- every qualifier with legal weight that you reworded, quoting the old and new wording;
- anything in the original you think is wrong or unclear (don't silently fix facts; flag them).
