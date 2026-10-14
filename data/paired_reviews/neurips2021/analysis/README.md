# Analysis of the NeurIPS 2021 pairs: what the models wrote

Everything under this folder was written by language-model agents from the per-pair records in `../pairs/`
(not in git; rebuilt by `scripts/build_neurips2021_pairs.py`) or derived from those writings by script.
No file here was edited by hand. The design is in `docs/neurips2021_analysis_plan.md`.

## Order

`order.json`: the 301 pairs in the order both stages use. Kinds first: oral/poster (6), spotlight/poster (16),
spotlight/reject (25), spotlight/spotlight (3), then poster/reject (174), poster/poster (74), reject/reject (3);
by pair id within a kind. The first 50 are the pairs where at least one committee recommended an oral or a
spotlight.

## Stage 1: notes per pair

`stage1/prompt.md` (version 1) and, for every pair, `stage1/<pair_id>.json` (structured fields: per committee
the ratings, confidences, outlier reviewer, inattentive reviews, checkable claims verified against the
as-reviewed PDF, rebuttal effect, area chair's handling; issues only one side raised; shared issues; verdict;
candidate reasons) and `stage1/<pair_id>.md` (the notes, at most 600 words). One fresh agent per pair
(`scripts/workflows/stage1_notes.js`; `claude-opus-5-5`, effort `max`), eight pairs per workflow, two workflows at a
time. Each agent read both committees' reviews, discussion, meta-reviews and decisions and the PDF as reviewed.

## Stage 2: the set of reasons

`stage2/prompt.md` (version 2). A run processes the 50 award pairs one at a time in a fixed order. The state
is `stage2/run_<k>/reasons.json`, a list of reasons (id, name, one-sentence definition, creating pair and
turn, exemplar). Turn n reads pair n's stage 1 notes and the set, judges every reason in the set for that
pair (yes or no, one line of justification each), and adds the reasons the pair needs that none covers;
`turn_<nnn>.json` records the set before, the judgements, the additions, the reasoning and the set after.
After the pass, a back-fill judge per pair judges every reason its own turn did not see
(`backfill_<pair_id>.json`), and a merge judge names entries that are one mechanism under two names
(`merges.json`). `scripts/workflows/stage2_reasons.js` runs the four modes.

`scripts/build_stage2_matrix.py <run>` derives, under `run_<k>/derived/`: `ticks.csv` (rows pairs, columns
reasons after merge, 1 where any judgement said yes), `justifications.jsonl` (one line per yes with its
source: turn, created, or backfill), `reasons_final.json` (with the ids merged into each), `summary.csv`
(pairs per reason, overall and by kind) and `coverage.json` (every pair-reason with no judgement; must be
empty). `scripts/make_stage2_figure.py <run>` draws `figures/stage2_matrix_run<k>.pdf` (the binary chart) and
`figures/stage2_reasons_by_kind_run<k>.pdf`.

Run 1 (2026-10-13 to 14): 50 turns, 37 reasons, 4 merges, 33 reasons after merge, 466 ticks, full coverage.
Turns 1 to 6 ran at effort `max`, the rest at `high` (see `run_1/README.md`). Run 2 (reverse order, effort `high` throughout): 50 turns, 40 reasons, 2 merges, 38 after merge, 485 ticks.
Alignment of run 2's reasons to run 1's: `alignment_run1_run2.json`; stability numbers: `stability_run1_run2.json`
(26 of 33 run 1 reasons reappear, 83% cell agreement on aligned reasons). Summary for readers:
`docs/neurips2021_stage2_results.md`.
