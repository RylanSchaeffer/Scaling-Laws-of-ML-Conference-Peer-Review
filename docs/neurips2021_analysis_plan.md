# Why two committees disagreed: the NeurIPS 2021 paired-review dataset and analysis

Status: plan for sign-off, 2026-10-14.

## 1. What we have

The NeurIPS 2021 consistency experiment reviewed 882 papers by two independent committees. For
301 of them both committees' records are public on OpenReview: 2,340 reviews (four reviewers per
copy as the norm, mean 3.9), every author response and discussion, each committee's meta-review
and own decision, and the final decision. Each copy's decision note names the other copy, so the
pairing is official. The counts match the report's Table 1 exactly, up to the 4 fatal-flaw
rejections it describes, which are private (`data/paired_reviews/neurips2021_reconciliation.md`).

Decision pairs among the 301: 99 agreed accepts, 199 accept/reject splits, 3 agreed rejects.
Award discrepancies: 6 oral/poster, 16 spotlight/poster, 25 spotlight/reject; 3 spotlight/spotlight.

## 2. The dataset on disk

```
data/raw/openreview/neurips2021/        raw API responses, never edited: notes.jsonl, references.jsonl, pull.json
data/paired_reviews/neurips2021/
  README.md                             provenance, schema, counts, licence, the reconciliation table
  pairs.csv                             one row per pair: ids, both decisions, final decision, review counts, mean ratings
  copies.csv                            one row per committee copy
  reviews.csv                           one row per review: ids, initial and final rating, confidence, time spent, text lengths
  pairs/n21-001/
    paper.json                          title, abstract, authors, keywords, PDF link, both forums
    a/  b/                              the two committees; a = lower paper number (the record does not say which was the original)
      decision.json                     own decision, the other committee's recommendation, final decision, meta-review text
      reviews.jsonl                     every review, every field, initial and final rating and text
      discussion.jsonl                  author responses and reviewer comments, threaded
      ethics.jsonl                      where an ethics review exists
    pair.md                             both committees side by side, readable
  analysis/                             everything the models write (Section 3)
```

Per copy the record holds: the reviewers' ratings (1 to 10), confidence (1 to 5), summary, main
review, limitations, ethics flags, time spent, and timestamps; the authors' responses and the
follow-up discussion; the AC's meta-review and the committee's own decision after SAC/PC
calibration; and the program chairs' final decision with the rule they applied. The initial
(pre-rebuttal) rating and text of each review come from the note's revision history, one API
call per copy. Not public, so absent: reviewer, AC and SAC identities, the reviewer–AC discussion,
the private pairs.

The CSVs and README go in git. The per-pair text (about 30 MB) is rebuilt from the raw dump by
one script and ships with the release as a zip.

## 3. The analysis, two stages, every step on disk

**Model:** `claude-opus-5-5`, temperature 0, through the API. Every call's prompt, response,
model id, prompt version and timestamp are saved. No step edits an earlier step's files.

**Stage 1: notes per pair.** For each of the 301 pairs the model reads both committees' full
records (reviews with initial and final ratings, rebuttals, discussion, meta-reviews, decisions)
and writes succinct notes on where the two committees diverged, and why. The notes are
structured: for each committee, the spread of ratings and whether one reviewer was an outlier
(a champion or a detractor); whether that reviewer's position rested on specific, checkable
argument or on enthusiasm; signs of inattention (a very high or low score with a thin review,
little time spent, no engagement in discussion); whether the rebuttal moved scores and on
which side; whether the AC's meta-review followed the reviews or overrode them; the substantive
issues one committee raised and the other did not; and a one-paragraph verdict on why one
committee recommended more than the other. Pairs that agreed get the same treatment, recording
what the committees agreed on and any score-level divergence, as a control. Output:
`analysis/stage1/<pair_id>.json` (structured fields) and `<pair_id>.md` (the notes), plus
`analysis/stage1/prompt.md`.

**Stage 2: the spreadsheet of reasons, grown one pair at a time.** One spreadsheet is the whole
state. Rows are the pairs processed so far; columns are reasons, each with a name, a one-sentence
definition and the pair that created it; cells are 0, 1 or blank, and every 1 carries a one-line
justification. At turn n the model reads pair n's stage 1 notes and the current columns, and
returns, for every existing column, 1 or 0 with a justification, and any new columns it needs,
defined, ticked for this row. The row is appended and the columns added. Every turn is saved,
`analysis/stage2/run_<k>/turn_<n>.json`: columns before, the row, columns after, the model's
reasoning. Order: the 47 award-discrepancy pairs first (oral/poster, spotlight/poster,
spotlight/reject), then the accept/reject splits, then the agreed pairs.

Two rules complete the matrix. *Back-fill:* a column created at turn n leaves rows 1 to n-1
blank; after the pass, each such column is judged for every earlier row in logged calls, so no
cell is an unjudged blank; back-fill creates no columns. *Merge:* one logged turn at the end in
which the model names columns that are one reason under two names; a merge ORs the ticks and
keeps both definitions in the log; nothing is deleted.

Outputs: `analysis/stage2/ticks.csv` (rows pairs, columns reasons, 0/1), `analysis/stage2/columns.json`
(names, definitions, creating pair, merge history), `analysis/stage2/justifications.jsonl` (one
line per 1), and `analysis/summary.csv`: for each reason, how many pairs it applies to, overall
and by kind of discrepancy (oral/poster, spotlight/poster, spotlight/reject, poster/reject,
agreed). The pass is repeated twice in other orders as a stability check: how many of run 1's
columns reappear, and how similar the matrices are.

**Audit trail.** `analysis/manifest.json` lists every input file with its SHA-256, every prompt
version, every model call's id, and the order of pairs in each run. Anyone can re-run any stage
from the saved inputs and compare.

## 4. Release

A standalone dataset: the raw OpenReview record, the per-pair folders, the three CSVs, the
stage 1 notes, the stage 2 turn logs, tick matrix and justifications,
the prompts, the scripts, and a README. Reviews and comments are CC BY 4.0 under OpenReview's
terms; our annotations the same.

## 5. Order of work

1. Pull the review revision histories; build the dataset folder; write the README.
2. Stage 1 on the 47 award-discrepancy pairs first; you read a few notes and the prompt is fixed
   or changed once; then all 301.
3. Stage 2: the pass, back-fill, merge; two more orders; summary table.
4. Release packaging.
