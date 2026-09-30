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
each other — seven dining halls, seven residence buildings and nine courses, all
written to the same template. Split plainly, the second chunk of the laundry
post reads "Best time to do laundry here is Tuesday or Wednesday morning" and
never says which building "here" is, so it could be retrieved for any of the
other six.

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
both be unusable without the line above them, because I have nine courses and
seven dining halls whose posts are otherwise worded almost identically. Chunk 2
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
which names no building, and I have six other dorms with near-identical
posts.

**3. Unit 2 — asking it to argue against my own verdicts.** The milestone
suggested pasting a criterion, its target, the runs and my verdict in and
asking Claude to argue the opposite as strongly as it could. I did that for all
five. Two of the attacks were on claims that were in my write-up without having
been checked: that the answer was in a retrieved *chunk* when my evidence file
only lists retrieved filenames, and that "names a source" couldn't be satisfied
by an invented filename. Both survived once actually measured — every `expects`
phrase is in a chunk that came back at rank 1, and none of the fifteen answers
cites a file that wasn't retrieved — so the verdicts stood but the evidence
behind them is real now rather than assumed. The third attack landed and became
my criterion 3 revision.

**4. Unit 2 — asking why my fix wouldn't work, before building it.** Before
writing any hybrid-search code I asked for the case against it. Five reasons
came back; I built anyway and two of them turned out to be right — my criteria
were already at ceiling so the run log couldn't record anything, and BM25 can't
help the dining-hall question because "shortest wait" shares no words with "no
queue". Knowing that in advance is why I measured entity coverage separately
instead of concluding from a flat run log that nothing happened.

**What I had to correct.** Claude wrote "eight dining halls, eight residence
buildings and ten courses" into my README, `criteria.md`, `chunker.py` and
`questions.py`. The real counts are seven, seven and nine. Nothing flagged it —
the number was wrong in confident prose across four files, and it only came out
by counting the files directly. Everything specific it wrote for me needed
checking against the corpus, and a few things I'd already committed didn't get
checked until later than they should have.

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

Evidence: `results/run_2026-09-23_2022_before.md`, produced by
`run_eval.py::main` — five questions, three runs each, cache off.

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. Retrieved chunk contains the answer | 4 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 2. Every answer names a source | 5 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 3. Gate stops out-of-corpus questions | 4 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 4. No chunk shorter than 50 characters | 0 chunks under 50 | 0 of 183 | 0 of 183 | 0 of 183 | MET |
| 5. Answer addresses what was asked | 4 of 5 | 5/5 | 5/5 | 5/5 | MET |

`scorer.py` doesn't exist, so the run columns came out blank and I judged all
fifteen answers by reading them.

Criteria 3 and 4 repeat across the three columns for the same reason: neither
depends on the model. The gate is a comparison against a fixed number, and the
chunks are built once at index time. Criteria 1, 2 and 5 could have moved
between runs and didn't.

The three runs were genuinely separate rather than one cached answer repeated —
the wording shifts even though the facts don't. Run 1 opens "The wait time at
Kestrel Commons…", run 3 opens "The wait at Kestrel Commons…".

### Criterion 1 — retrieved chunk contains the answer

From `run_eval.py::main`, retrieval by `store.py::search` over chunks from
`chunker.py::split_documents`. Kestrel Commons, run 1:

```
- Best distance: 0.1733 (passed the gate)
- Sources retrieved: dining_halden_hall_followup.txt, dining_kestrel_commons.txt, dining_kestrel_commons_followup.txt, dining_the_ridgeway_cafe_followup.txt

The wait time at Kestrel Commons between 12:15 and 1:00 is 20 to 25 minutes. 

Source: `dining_kestrel_commons.txt` and `dining_kestrel_commons_followup.txt`
```

Both Kestrel chunks are in the retrieved set, and the "20 to 25 minutes" I
wrote into `questions.py` as the expected answer is in them. Same for the other
four questions on all three runs.

### Criterion 2 — every answer names a source

Same file. CS 210, run 2 — the model names the two files in prose rather than
on a Source line, which I counted as naming a source:

```
For CS 210, you should expect 8 to 10 hours a week outside of class. This is stated in *course_cs_210.txt* and *course_cs_210_workload.txt*.
```

All fifteen answers named at least one file. The format varied between runs —
a `Source:` line, a parenthesis, italics — but the filename was always there.

### Criterion 3 — the gate stops out-of-corpus questions

From `run_eval.py::check_out_of_scope`, decided by `gate.py::check` at a cutoff
of 0.5. One deterministic pass:

```
| Out-of-scope question                                       | Best distance | Gate    |
| What is the capital of Mongolia?                            | 0.787         | refused |
| How do I change the oil in a diesel engine?                 | 0.923         | refused |
| Who won the 1994 World Cup?                                 | 0.847         | refused |
| What is the recommended dosage of ibuprofen for a headache? | 0.849         | refused |
| How do I write a for loop in Rust?                          | 0.860         | refused |
```

Refused 5 of 5, and none of them came close to the cutoff — the nearest was
0.787 against a threshold of 0.5.

### Criterion 4 — no chunk shorter than 50 characters

From `chunker.py::describe`, on the chunks that `chunker.py::split_documents`
produced and that this whole run was served from:

```
183 chunks, 167 characters on average (shortest 63, longest 397), produced by chunker.py::split_documents
```

Shortest is 63, so nothing is under 50.

### Criterion 5 — the answer addresses what was asked

The Kestrel answer under criterion 1 is the evidence here too. Its
"Sources retrieved" line shows the model was handed chunks from Halden Hall and
The Ridgeway Café alongside the two Kestrel ones — different dining halls
written to the same template with different numbers. It used neither, and
answered about the hall I asked about. That was the failure this criterion
exists to catch.

## Verdicts

<!-- MET or MISSED for each of the five, against the target you wrote last
     unit — not a new one. Plus a sentence on how you decided. That sentence
     matters most where it was close.

     If your target said 4 of 5 and your runs came out 4, 3, 4, that's a MISS.
     The target has to hold, not show up occasionally.

     Milestone 2. -->

| # | Criterion | Verdict | How I decided |
|---|---|---|---|
| 1 | Retrieved chunks contain the answer, 4 of 5 | MET | Read all fifteen answers against the `expects` phrase I wrote in `questions.py` before I saw any results. The phrase was in the retrieved chunks every time — 5/5 on all three runs, so the target held rather than showing up occasionally. |
| 2 | Every answer names a source, 5 of 5 | MET | All fifteen named at least one file. The format moved between runs — a `Source:` line, italics, a parenthesis — and I counted all three, because my criterion asks the answer to name a document, not to format it a particular way. |
| 3 | Gate refuses out-of-corpus questions, 4 of 5 | MET, but revised | `gate.py::check` refused all five, and not narrowly: the closest was 0.787 against my 0.5 cutoff. One deterministic pass, so there is one number and it stands for all three runs. Met on the five it named — but I've revised it in `criteria.md`, because those five tested the wrong thing. See below. |
| 4 | No chunk shorter than 50 characters | MET | `chunker.py::describe` reports the shortest of my 183 chunks at 63 characters. Measured on the index this run was served from, not a separate one. |
| 5 | Answer addresses what was asked, 4 of 5 | MET | The closest call of the five, because it's a judgement rather than a count. I read each answer next to its question and asked whether it answered *that* question. The Kestrel one is the test case: the model was handed Halden Hall and Ridgeway Café chunks too and used neither. 5/5 on all three runs. |

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

I missed nothing. All five criteria came out MET on all three runs, and four of
them came out at 5/5 against targets of 4 of 5.

**One criterion was broken rather than unmet, and I revised it.** Criterion 3
says the gate should stop "a question my documents clearly don't cover." I
measured that with Mongolia, diesel engines, the 1994 World Cup, ibuprofen and
Rust, which came back at 0.787 to 0.923 against a 0.5 cutoff. That tests whether
the gate can reject another universe. It does not test the case I care about — a
believable campus question I simply have no document for — and the gate fails
that one:

```
PASS   0.341  What are the operating hours of the campus bookstore?
          nearest: study_library_hours.txt
```

I have no bookstore document. The gate passes the question anyway and hands the
model library opening hours.

**Stage and mechanism:** embedding. "Operating hours of the campus bookstore"
and "Library hours during term" are the same *kind* of question — when is a
campus facility open — and cosine distance scores that resemblance, which is why
0.341 looks like a good match. Distance measures topical similarity, not whether
the chunk is about the thing I named. The gate inherits that limitation exactly:
`gate.py::check` compares one number against 0.5, so it can only ask "is the
nearest chunk on a similar topic", never "is the nearest chunk about a
bookstore". My Mongolia-and-Rust questions never exposed this because they
aren't similar to anything in the corpus on any axis.

The revision is in `criteria.md` underneath the
original line: *of five questions about my own campus that my documents happen
not to cover, the gate refuses at least 4.* That is harder than what I wrote
first, not easier — the original target was met on the five questions it named,
so this is a fix to the measurement rather than a retreat from a number I
missed.

I also argued the opposite verdict for the other four and couldn't make any of
them stick. Two are worth recording because I checked them rather than assumed:
every `expects` phrase was in a chunk that was actually retrieved, at rank 1 in
all five cases — not merely in a file that was retrieved, which is all my
evidence file lists. And none of the fifteen answers cited a document that
wasn't in its retrieved set, so criterion 2 isn't passing on invented filenames.

I don't think that means the system is good. I think my targets were set low,
and I can say exactly how. **The weakness isn't in the numbers I picked — it's
in the five questions I picked to measure them with.** Every one of my questions
names the thing it's asking about ("Kestrel Commons", "Morrow House", "CS 210"),
and every answer sits inside a single document. Those are the two easiest
properties a question can have, and I gave all five of them to myself.

Criterion 5 is the clearest case. I wrote it to catch answers about the wrong
dining hall, which my corpus invites because eight halls are written to the same
template with different numbers. It scored 5/5 — but it never got a real
chance to fail, because every question already said which hall I meant. When I
tried a question that doesn't:

```
How much is a wash and when should I go?
  gate: PASS  best 0.483
    0.483  housing_calder_annexe.txt
    0.483  housing_fenwick_court.txt
    0.497  housing_fenwick_court_laundry.txt
    0.506  housing_old_brewhouse_laundry.txt
    0.516  housing_aldridge_hall.txt
```

Three different buildings, all with different prices, handed to the model at
once, and nothing to tell it which one I live in.

**The pattern, and it's one problem rather than several: my system does lookups
well and comparisons badly.** Two examples, both of which pass the relevance
gate, so the system has no idea anything is wrong. They look like the same
failure and they are not — diagnosing them separately is what this section is
for:

```
Which dorm is the cheapest?
  gate: PASS  best 0.497
    0.497  housing_tamsin_court.txt
    0.503  housing_innisfree_hall.txt
    0.540  housing_old_brewhouse.txt
    0.546  housing_aldridge_hall.txt
    0.549  money_textbooks.txt
```

The right answer is Morrow House, the cheapest tier by about $900 a year. It is
not in the retrieved set. The system would answer this confidently, cite a real
file, and be wrong — the gate can't catch it, because the gate only asks "is the
nearest chunk close enough", never "is anything missing".

**Working backwards told me the stage, and it wasn't the one I assumed.** I
re-ran the search over all 183 chunks to find where the correct chunk actually
ranks:

```
Which dorm is the cheapest?
  correct chunk is RANK 11 of 183, distance 0.630  (housing_morrow_house.txt)
  rank 5 cutoff was distance 0.549
```

Not a near miss at rank 6 — rank 11, and at 0.630 it's beyond my 0.5 gate as
well, so it would be refused even if it came back alone. The reason shows up in
what *did* win:

```
 1. 0.497  housing_tamsin_court.txt    The good: the most independent housing on campus...
 2. 0.503  housing_innisfree_hall.txt  The good: the shared-bathroom arrangement is the best compromise...
 3. 0.540  housing_old_brewhouse.txt   The good: the most characterful building on campus...
 4. 0.546  housing_aldridge_hall.txt   The bad: the elevator is out roughly one week per semester.
...
11. 0.630  housing_morrow_house.txt    The good: cheapest housing tier by about $900 a year...
```

**The stage is embedding, and the mechanism is that my chunks are too alike in
form.** Every housing post has a "The good: the most X on campus" line, my
chunker made each of those its own chunk, and "Which dorm is the cheapest?" is
structurally a superlative claim about a dorm. So all seven buildings produce a
chunk matching the *shape* of the question almost equally well — the top four
sit inside 0.05 of each other — and the one that literally contains the word
"cheapest" loses. Cosine
distance is scoring sentence form over the specific attribute I asked about.

That matters because it rules out the obvious fix. Raising `TOP_K` to 11 would
retrieve this one chunk, but it doesn't make the ranking meaningful — it just
widens a net over seven near-ties.

The second example is a different story, and I had it wrong the first time:

```
Which dining hall has the shortest wait at lunch?
  correct chunk is RANK 2 of 183, distance 0.337  (dining_halden_hall_followup.txt)
  also RANK 5, distance 0.432  (dining_halden_hall.txt)
```

Halden Hall's "rarely more than 8 minutes" came back at rank 2. **Retrieval
succeeded here.** But the five chunks cover only four of my seven dining halls,
and two of the three it missed — The Atrium and North Kitchen — have no queue at
all, which makes them the real answer. So the system can produce a plausible
answer ("Halden Hall, rarely more than 8 minutes") from a genuinely retrieved,
correctly cited chunk, and still be wrong, because it never saw the halls it
needed to compare against. The stage here is retrieval, and the mechanism is
coverage rather than ranking: a top-5 over seven entities cannot answer a
question about all seven, no matter how good the ranking is.

**So the pattern is one symptom with two causes.** Comparison questions fail
either because the distinguishing chunk ranks low among near-identical siblings
(embedding), or because top-5 can't cover the full set being compared
(retrieval). Both are invisible to the gate, which measures the nearest chunk
and never asks what's missing.

**Which criterion I'd tighten, and to what.** Criterion 1. I'd keep the target
at 4 of 5 and constrain the test set instead:

> For at least 4 of my 5 test questions — **of which at least two require
> information from more than one document** — the retrieved chunks include one
> that contains the answer.

Same number, genuinely harder, and I already know it would have failed: "which
dorm is the cheapest?" needs all seven housing documents and gets four.

## The Improvement

**What I changed:** Hybrid search. `store.py::search` now runs a BM25 keyword
ranking over the same 183 chunks alongside the embedding ranking and fuses the
two with reciprocal rank fusion (`store.py::_fuse_with_keywords`). One change,
behind one flag — `config.HYBRID_SEARCH` — so I can run the identical test both
ways.

Each result keeps its true cosine distance, so `gate.py::check` still thresholds
on the quantity my 0.5 cutoff was calibrated against. Without that, fusing
scores would have left the gate comparing 0.5 to a number that no longer means
anything, and criterion 3's measurement would have broken as a side effect.

**Why I picked it:** My diagnosis found that for "which dorm is the cheapest?"
the chunk containing the literal word *cheapest* ranked 11th of 183 while seven
interchangeable "The good: the most X on campus" sibling chunks took the top
places — meaning alone could not separate near-duplicates, so I added the one
signal that can, the exact word.

I wrote down before building that this might not work, for three reasons: my
five criteria were already at 5/5 so the run log couldn't move; BM25 can't touch
the dining-hall case, where "shortest wait" shares no vocabulary with "rarely
more than 8 minutes" or "no queue"; and my corpus is templated, so every sibling
shares boilerplate and the distinguishing content is numbers. Two of those three
turned out to be right.

### Run Log — After

Evidence: `results/run_2026-09-29_2109_after.md`, produced by `run_eval.py::main`
with `config.HYBRID_SEARCH = True`.

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. Retrieved chunk contains the answer | 4 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 2. Every answer names a source | 5 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 3. Gate stops out-of-corpus questions | 4 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 4. No chunk shorter than 50 characters | 0 chunks under 50 | 0 of 183 | 0 of 183 | 0 of 183 | MET |
| 5. Answer addresses what was asked | 4 of 5 | 5/5 | 5/5 | 5/5 | MET |

Identical to the before table, cell for cell.

**Did it help?** Partly. It fixed the exact thing my diagnosis named and made
the other half of the same problem worse, and the run log shows none of it.

**On my five criteria: no change at all.** 5/5 on every criterion on all three
runs, before and after, with the same best distances to three decimal places
(0.173, 0.235, 0.162, 0.215, 0.117). I predicted this before running it — the
criteria were already at ceiling, so they had no room to record anything. That
is a fact about my test set, not about the change.

**On the failure it was built for: it worked.**

```
Which dorm is the cheapest?
  before: correct chunk retrieved: False   (Morrow $900 ranked 11 of 183)
  after : correct chunk retrieved: True
```

The word *cheapest* appears literally in that chunk, BM25 ranks it first on
keywords, and fusion pulls it into the top 5 past the ten chunks that outranked
it on cosine distance — nine of them from five sibling buildings. That is the mechanism I diagnosed, fixed by the signal I
chose for it.

**On the other cause, it backfired.** My diagnosis said comparison questions
fail two ways — bad ranking among siblings, and top-5 not covering the full set
being compared. Hybrid fixes the first by *spending* the second:

| Question | Entities covered before | after |
|---|---|---|
| Which dorm is the cheapest? | 4 of 7 housing buildings | **2 of 7** |
| Which dining hall has the shortest wait at lunch? | 4 of 7 dining halls | **2 of 7** |
| How much is a wash and when should I go? | 4 buildings | 4 buildings |

Five slots is five slots. Every chunk BM25 promotes displaces one the embedding
chose, so coverage halved. On the dorm question the two it displaced were
replaced partly by keyword noise — `money_textbooks.txt` and
`admin_printing_quota.txt` share vocabulary with a question about cost without
being about dorms at all. On the dining question the correct answer is a hall
with **no queue**, which shares no words with "shortest wait", so BM25 had
nothing to contribute and only cost coverage: it went from 4 halls to 2 and
still doesn't retrieve the right one.

**And it didn't touch my revised criterion 3.** "What are the operating hours of
the campus bookstore?" still passes the gate — 0.341 before, 0.411 after — and
still retrieves library hours. I expected that: the problem there is that cosine
distance scores topical resemblance rather than entity identity, and adding
keyword matching to the ranking doesn't change what the gate thresholds on.

**What I'd conclude.** The change was correctly aimed and too small to be worth
it on its own. Fusion re-ranks within a fixed budget of five chunks, and my real
problem with comparison questions is that the budget is smaller than the number
of things being compared. Hybrid search plus a larger `TOP_K` for questions that
name a category rather than an instance is the thing I'd try next, and I'd want
a criterion that measures entity coverage directly rather than inferring it from
whether an answer looks right.

<!-- Say plainly whether it did, and how you know. If it made things worse,
     say that — a change that backfired, honestly reported, earns full credit
     and is more interesting than one that worked. What matters is that you can
     tell.

     Milestone 4. -->

## What's Still Broken

All five of my original criteria are still MET after the change. That is not the
same as nothing being left, and three things are broken.

**1. My revised criterion 3 is failed, and the fix didn't touch it.** The
revision I added in `criteria.md` says the gate should refuse questions about my
own campus that my documents don't cover. It doesn't: "What are the operating
hours of the campus bookstore?" passed at 0.341 before hybrid search and 0.411
after, and retrieves `study_library_hours.txt` both times.

What I'd do: the gate currently asks one question — is the nearest chunk close
enough — and that can't distinguish "similar topic" from "about the thing you
named". I'd add a second check that compares the entity in the question against
the entities in the retrieved chunks, and refuse when the question names
something no chunk names. That's a different kind of code from a distance
comparison, closer to extraction than retrieval.

Why I stopped: the milestone asks for one change, and this is a second one. I'd
also want to think harder about whether it's really a gate problem rather than a
corpus problem — a system whose documents don't mention bookstores arguably
should say "I don't have a document about that" rather than guessing at the
threshold.

**2. Hybrid search halved my entity coverage, and I left that in.** Fusion
re-ranks inside a fixed budget of five chunks, so every keyword promotion
displaces an embedding hit: 4 of 7 buildings down to 2 of 7 on both comparison
questions.

What I'd do: raise `TOP_K` when fusion is on, so the keyword ranking adds chunks
rather than replacing them. That is one line, and I can guess the shape of the
tradeoff — more chunks means more near-identical siblings in the prompt, which
is exactly what my fifth criterion is afraid of.

Why I stopped: I didn't want to change two things and lose the ability to say
which one moved the numbers. Having measured the regression cleanly is worth
more to me than having half-fixed it.

**3. Comparison questions still don't work.** "Which dining hall has the
shortest wait at lunch?" retrieves 2 of my 7 halls and misses the two that have
no queue at all, which are the actual answer. Hybrid search couldn't help here —
"shortest wait" shares no vocabulary with "no queue" — and made the coverage
worse.

What I'd do: detect that a question is about a category rather than an instance,
and retrieve per entity so all seven halls are represented, then let the model
compare. That's a real feature, not a tuning change.

Why I stopped: out of time for this unit, and honestly I'm not certain the fix
belongs in retrieval. A question that needs all seven documents may just be a
question this architecture shouldn't answer, and refusing it might be better
than answering it from four.

## What I'd Do Differently

The single thing I'd change is that **I'd write criteria that constrain the test
set, not just the score.** All five of mine named a number and none of them
named what the questions had to be like, so I picked five questions that each
named their entity and had their answer in one document, and then measured 5/5
on everything. The numbers were honest. They just described an easy exam.

Concretely, three of the five:

**Criterion 1** — I'd keep 4 of 5 and add the clause: *of which at least two
require information from more than one document*. Same target, and I already
know it would have failed.

**Criterion 4** — "no chunk shorter than 50 characters" can no longer fail,
because my chunker glues a title onto every chunk by construction. It did its
job once, by ruling out the plain paragraph split that would have produced 88
title-only chunks, but it has been unfalsifiable ever since. I'd replace it with
something about whether a chunk is *usable* rather than long enough — for
instance, that a sampled chunk names the building or course it's about, which is
the property I actually care about.

**Criterion 5** — "as judged by reading the answer against the question" has no
procedure in it, and the person doing the reading wanted it to pass. I'd make it
checkable: *the answer contains the `expects` phrase and names a document that
phrase actually appears in.* That is stricter than what I wrote and can be run
without a human deciding.

The broader lesson is about where the difficulty in a criterion lives. I spent
my effort on choosing the number — 4 of 5 rather than 5 of 5, 50 characters
rather than 200 — when the number was never the part that made the test easy.
The test set was.
