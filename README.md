# The Unofficial Guide

<!-- Raabiah - Corpus picked: campus_life -->



# Unit 1

## What This Does

This answers questions about student life at one university, using the
`campus_life` corpus — 88 short posts written by students about dining halls,
residence buildings, courses, and admin procedures like the pass/fail option and
the add/drop deadline. You ask it something specific, like how long the lunch
queue is at Kestrel Commons or how many hours a week CS 210 takes, and it finds
the posts that cover it and answers from those, naming the file it used.

It only knows what's in those 88 posts. If you ask it something they don't cover
it says "I don't have enough information about that" rather than guessing — it
checks how close the retrieved posts actually are before it lets the model see
them at all.

## Chunking Strategy

**Chunk size:** One paragraph, plus the document's title line. No fixed
character count — in practice this comes out at 63 to 397 characters, median
147.
**Overlap:** No character overlap. The title line is the only text repeated
between chunks from the same document.

Every post in `campus_life` has the same shape: a title line, a blank line,
then two or three paragraphs. Reading them in Milestone 1, the paragraphs turned
out to be answering *different questions*. `housing_aldridge_hall_laundry.txt`
gives machine prices in one paragraph and the best time to go in the next;
`dining_kestrel_commons.txt` gives wait times in one and opening hours in the
next. So the blank lines already mark where one thought ends, and I split on
those instead of on a character count.

I put the title back on every chunk because my documents are near-duplicates of
each other — eight dining halls, eight residence buildings and ten courses, all
written to the same template. Split plainly, the second chunk of the laundry
post reads "Best time to do laundry here is Tuesday or Wednesday morning" and
never says which building "here" is, so it could be retrieved for any of the
other seven.

I considered a fixed 400-character window first, on the reasoning that it was
near my average document length. I tried it and dropped it: only 12 of my 88
posts are longer than 400 characters, so it left 86% of the corpus untouched,
and where it did cut it landed mid-sentence and produced an 18-chunk tail of
fragments — the shortest was 2 characters. That would have broken my own fourth
acceptance criterion straight away.

This took the corpus from 88 chunks (the starter never split anything, because
nothing reaches 800 characters) to 183.

## Sample Chunks

Five chunks from `python app.py chunks -n 5`, spread across the corpus.

**Chunk 1** — source: `admin_add_drop_deadline.txt#0` — produced by: `chunker.py::split_documents`

```
On the add/drop deadline

You can add a course through the end of the second week. Dropping is a longer window — through the end of week six — but a drop after week two shows as a W on your transcript. Nothing anywhere on the registrar's site says this plainly, and students find out from each other.
```

**Chunk 2** — source: `course_cs_340_exams.txt#1` — produced by: `chunker.py::split_documents`

```
CS 340 Databases — assessment

Start the term project in week three, not week eight; everyone learns this the hard way.
```

**Chunk 3** — source: `course_phys_130_workload.txt#0` — produced by: `chunker.py::split_documents`

```
Workload for PHYS 130 Mechanics

People keep asking so: 7 hours a week, plus 3 on lab weeks. That's real time, not optimistic time.
```

**Chunk 4** — source: `dining_verrill_street_grill_followup.txt#1` — produced by: `chunker.py::split_documents`

```
Re: Verrill Street Grill

Also worth saying: one register, so the queue is a single line no matter how busy. Nobody tells you this at orientation.
```

**Chunk 5** — source: `housing_morrow_house.txt#1` — produced by: `chunker.py::split_documents`

```
Morrow House — what it's actually like

The good: cheapest housing tier by about $900 a year, and the singles are real singles.
```

**Reading them back:** all five answer a question on their own. Chunks 2, 4 and
5 are the ones that make the case for gluing the title on — "Start the term
project in week three" and "one register, so the queue is a single line" would
both be unusable without the line above them, because I have ten courses and
eight dining halls whose posts are otherwise worded almost identically. Chunk 2
is the shortest of the five at 119 characters and still answers "when should I
start the CS 340 project?" on its own. Across the whole corpus the shortest
chunk this produces is 63 characters, which clears the 50-character floor I set
in my fourth acceptance criterion.

## Sample Answer

**Question:** How long is the wait at Kestrel Commons between 12:15 and 1:00?

**Answer:**

```
  (best distance 0.173, cutoff 0.5)

The wait at Kestrel Commons between 12:15 and 1:00 is 20 to 25 minutes.

Source: `dining_kestrel_commons.txt` (and `dining_kestrel_commons_followup.txt`)

Sources retrieved: dining_halden_hall_followup.txt, dining_kestrel_commons.txt,
dining_kestrel_commons_followup.txt, dining_the_ridgeway_cafe_followup.txt
```

Worth noting what the "Sources retrieved" line shows: two of the five chunks
handed to the model were about *other* dining halls — Halden Hall and The
Ridgeway Café, whose posts use the same sentences with different numbers. The
model used neither. That's the failure my fifth criterion is watching for, and
on this question it didn't happen.

And the refusal path, same command:

```
$ python app.py ask "What is the capital of Mongolia?"
  (best distance 0.787, cutoff 0.5)

I don't have enough information about that.

0 model calls this session
```

**My relevance cutoff:** 0.5

I ran all ten questions through retrieval and took the best distance for each.
The two groups came out nowhere near each other — everything my corpus covers
landed between 0.117 and 0.235, and everything it doesn't landed between 0.787
and 0.923. That's a gap of more than half the scale with nothing in it, so the
exact number matters less than I expected it to. I put the cutoff at 0.5:
roughly double my worst real question, which leaves slack for one phrased more
vaguely than my five, and still 0.29 clear of my closest out-of-corpus question.
At this setting the gate passes all five real questions and refuses all five
others.

| Question | In corpus? | Best distance |
|---|---|---|
| When are the health centre's walk-in hours? | yes | 0.117 |
| How many hours a week outside class should I expect for CS 210? | yes | 0.162 |
| How long is the wait at Kestrel Commons between 12:15 and 1:00? | yes | 0.173 |
| How late in the term can I declare a course pass/fail? | yes | 0.215 |
| How much cheaper is Morrow House than the other housing tiers? | yes | 0.235 |
| What is the capital of Mongolia? | no | 0.787 |
| Who won the 1994 World Cup? | no | 0.847 |
| What is the recommended dosage of ibuprofen for a headache? | no | 0.849 |
| How do I write a for loop in Rust? | no | 0.860 |
| How do I change the oil in a diesel engine? | no | 0.923 |

I had predicted in criteria.md that the ibuprofen question would be the one to
slip through, because I do have a `health_center.txt` document. It came back at
0.849 — the third *furthest* of the ten — and its nearest chunk was
`money_textbooks.txt`, not the health centre at all. So the prediction was
wrong, and wrong in a useful way: the embedding model is matching on what a
question is *about*, not on shared vocabulary like "health". Asking for a drug
dosage isn't close to a document about walk-in hours just because both are
medical.

**Top-k:** left at 5. The correct chunk came back first for all three questions
I inspected, so there was nothing to fix by widening it, and on CS 210 the
second-nearest chunk was already the STAT 150 workload post — a different course
with the same sentence shape. Pulling back more would have added more of those.

**Grounding instruction:** left as the starter wrote it. I checked it with
`python app.py ask "..." --show-prompt`. It already says to use only the
supplied documents, to say so when they don't cover the question, and to name
the file — and my answers aren't drifting past the sources, so there was nothing
to tighten.

## How I Used AI

**1. Checking whether my acceptance criteria actually said anything.** I had
written criterion 4 as "the answer the system produces is one sentence long" and
criterion 5 as "the answer directly addresses what was asked," and I asked Claude
whether those were measurable. It said both were too vague to check twice and got
the same result, and that criterion 4 was about answers when the section asks for
something about chunks. What I was really worried about was a chunk being so
short it was just the title of the post, so I asked for a minimum length instead.
Rather than suggest a number, it measured my corpus: my title lines top out at 47
characters and my body paragraphs start at 36, so 50 separates them and only
costs me four real paragraphs out of 183. I went with 50. 

**2. Picking a chunk size, and being talked out of my first answer.** I was going
to set the chunk size to 400 characters, and my reason was that it was close to
my average document length. I asked Claude to sanity-check that before I coded
it. It ran the number against my actual files and the reason fell apart: only 12
of my 88 posts are longer than 400 characters, so the rule would have left 86% of
the corpus untouched, and where it did cut it landed mid-sentence and produced
fragments like "out from each other." The shortest chunk it made was 2
characters, which would have broken the criterion 4 I'd just written. The bigger
thing I took from it is that I was asking the wrong kind of question — my posts
already mark where one thought ends with a blank line, so I should split on that
rather than on any character count. What I changed here was my own plan rather
than the code: I dropped the 400-character idea completely. The suggestion that
came with it was to glue the title line onto every piece, and I checked that
against a real file before accepting it — `housing_aldridge_hall_laundry.txt`
splits into a paragraph that says "Best time to do laundry **here** is Tuesday,"
which names no building, and I have seven other dorms with near-identical
posts.

<!-- ── Stretch features ─────────────────────────────────────────────────────
     Doing one? Say so here BEFORE you start. A feature this README never
     claims earns nothing.
     ───────────────────────────────────────────────────────────────────────── -->

---

# Unit 2

<!-- These sections get ADDED to what's already above. Don't delete or rewrite
     unit 1 — the point is that someone can see what you said before you knew
     how it went. -->

## Run Log — Before

<!-- Your five criteria, three runs each. `python run_eval.py --label before`
     runs the questions, puts the OUT_OF_SCOPE ones through the gate, and
     writes it all into results/ for you. Targets come from criteria.md; the
     verdict column is your call.

     Criterion 3 is measured in one deterministic pass rather than three, so
     the same number goes in all three run columns. That's correct, not lazy.

     Milestone 1. -->

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. Retrieved chunk contains the answer | 4 of 5 |  |  |  |  |
| 2. Every answer names a source | 5 of 5 |  |  |  |  |
| 3. Gate stops out-of-corpus questions | 4 of 5 |  |  |  |  |
| 4. | | | | | |
| 5. | | | | | |

<!-- Underneath, paste the REAL output for each criterion from one of your
     runs — the actual text your system produced, not a description of it.
     Name the file and function that produced it. -->

## Verdicts

<!-- MET or MISSED for each of the five, against the target you wrote last
     unit — not a new one. Plus a sentence on how you decided. That sentence
     matters most where it was close.

     If your target said 4 of 5 and your runs came out 4, 3, 4, that's a MISS.
     The target has to hold, not show up occasionally.

     Milestone 2. -->

| # | Criterion | Verdict | How I decided |
|---|---|---|---|
| 1 |  |  |  |
| 2 |  |  |  |
| 3 |  |  |  |
| 4 |  |  |  |
| 5 |  |  |  |

## Diagnoses

<!-- For each miss: which stage caused it, and how. The stage alone isn't
     enough — you need the mechanism.

     Not a diagnosis: "Question 3 didn't work."
     A diagnosis:     "Question 3 asks about laundry costs. The answer is in
                       one sentence that got split across two chunks, so
                       neither chunk on its own contains it."

     The five stages: loading → chunking → embedding → retrieval → generation.

     Look for a pattern. If three misses all ask about numbers, that's one
     problem, not three.

     Missed nothing? Say so, then say honestly whether your targets were set
     low, and which one you'd tighten and to what.

     Milestone 3. -->

## The Improvement

**What I changed:**

**Why I picked it:**

<!-- Connect it to a specific diagnosis above in one sentence. If you can't,
     you picked a fix because it sounded impressive. -->

### Run Log — After

<!-- Same format, same five criteria, three runs each.
     `python run_eval.py --label after` -->

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. Retrieved chunk contains the answer | 4 of 5 |  |  |  |  |
| 2. Every answer names a source | 5 of 5 |  |  |  |  |
| 3. Gate stops out-of-corpus questions | 4 of 5 |  |  |  |  |
| 4. | | | | | |
| 5. | | | | | |

**Did it help?**

<!-- Say plainly whether it did, and how you know. If it made things worse,
     say that — a change that backfired, honestly reported, earns full credit
     and is more interesting than one that worked. What matters is that you can
     tell.

     Milestone 4. -->

## What's Still Broken

<!-- For each criterion still missed after your fix: what you'd do about it,
     and why you stopped where you did.

     "I ran out of time" is fine if it's true. Pretending nothing is left is
     not.

     Milestone 5. -->

## What I'd Do Differently

<!-- Knowing what you know now — which of your five criteria would you write
     differently, and why?

     Milestone 5. -->
