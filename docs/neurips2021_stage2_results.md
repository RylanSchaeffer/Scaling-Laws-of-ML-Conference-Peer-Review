# Why the two committees gave different awards: stage 2, run 1

Scope: the 50 NeurIPS 2021 pairs in which at least one committee recommended an oral or a spotlight (6 oral/poster,
16 spotlight/poster, 25 spotlight/reject, 3 spotlight/spotlight). One language-model judge per pair, in a fixed order,
growing one shared set of reasons; every judgement is on disk (`analysis/stage2/run_1/`). The chart:
`figures/stage2_matrix_run1.pdf` (pairs by reasons) and `figures/stage2_reasons_by_kind_run1.pdf`.

## What it changed in the model

The award tier was a chair's call in most pairs, so the model now cuts the award tiers on an award ordering,
the score plus a chair noise η ~ N(0, σ_η²) within the accepted set, redrawn by a second review. σ_η = 0.59 on
the 1-10 axis, fitted so that the model's awards fall inside each committee's score top-K as often as the real
ones did (26 of 53; `scripts/fit_award_noise.py`, `results/award_noise.json`, bootstrap 90% range 0.42 to 0.76).
Held out: the model then predicts 4.6 shared awards (observed 3, P = 0.32) and 33% of award papers rejected by
the other committee (observed 48%, P = 0.02; was 5.6 and 30% without the step). Paper: Section "The award step",
Appendix "The NeurIPS 2021 paired reviews".

## What the matrix says

Three mechanisms are present in almost every award split: the committees weighted the same evidence differently
(45 of 50), one committee's reviews were thin or inattentive (39), and a substantive concern was raised by one
committee only (39). The award tier itself was usually an area chair's call rather than an argument from the
reviews: in 30 of 50 pairs the higher tier was given with no stated grounds, in 33 the meta-review dropped
weaknesses its own reviewers had stated, and in 20 the area chair's own judgement drove the recommendation.
Score mechanics matter less: a factual misreading set a score in 24 pairs, the rebuttal moved one committee only
in 26, and reviewers who said they were not experts had their accept scores counted in full in 19.

Spotlight/reject splits (25 pairs) are where the area-chair mechanisms concentrate: the higher tier had no stated
grounds in 19 of 25 and the meta-review dropped stated weaknesses in 19 of 25, against 3 of 6 and 2 of 6 for the
oral/poster pairs. The oral/poster pairs are instead all cases of thin reviews on one side and different weighting
of the same evidence.

## The reasons, most frequent first

| Reason | Pairs | Oral/Poster (6) | Spotlight/Poster (16) | Spotlight/Reject (25) | Both spotlight (3) | Reappears in run 2 |
|---|---|---|---|---|---|---|
| Committees weighted the same evidence differently | 45 | 6 | 14 | 25 | 0 | yes |
| One committee's reviews were thin or inattentive | 39 | 6 | 15 | 16 | 2 | yes |
| Only one committee raised a substantive concern | 39 | 5 | 12 | 22 | 0 | yes |
| Meta-review dropped the reviewers' stated weaknesses | 33 | 2 | 10 | 19 | 2 | yes |
| Higher tier given with no stated grounds | 30 | 3 | 7 | 19 | 1 | yes |
| Rebuttal moved one committee but not the other | 26 | 3 | 5 | 15 | 3 | yes |
| Score rested on a factual misreading of the paper | 24 | 1 | 6 | 15 | 2 | yes |
| Area chair's own judgement drove the recommendation | 20 | 3 | 6 | 10 | 1 | yes |
| Rebuttal could answer one committee's concerns only | 19 | 3 | 4 | 12 | 0 | no |
| Non-expert reviewers' accept scores counted in full | 19 | 2 | 5 | 11 | 1 | yes |
| Damaging rebuttal admission did not lower scores | 18 | 1 | 5 | 11 | 1 | yes |
| Committees applied different standards for the contribution type | 15 | 1 | 4 | 10 | 0 | yes |
| Scores rose on unverified rebuttal evidence | 12 | 1 | 2 | 9 | 0 | yes |
| One committee's reviewers left the rebuttal unanswered | 12 | 1 | 4 | 7 | 0 | no |
| Novelty judged against wrong or ignored prior work | 12 | 1 | 1 | 9 | 1 | no |
| Authors told the two committees different things | 10 | 0 | 3 | 6 | 1 | yes |
| Reviewer's rating out of line with own text | 9 | 1 | 0 | 7 | 1 | yes |
| Unanimous scores read as grounds for higher tier | 9 | 0 | 4 | 4 | 1 | no |
| One outlying score set the tier | 9 | 3 | 5 | 1 | 0 | no |
| Only one committee had an engaged champion | 9 | 0 | 1 | 7 | 1 | yes |
| Promised fixes judged too large without re-review | 9 | 0 | 0 | 9 | 0 | yes |
| Area chair followed one outlying reviewer | 8 | 1 | 1 | 5 | 1 | yes |
| Recommendation rested on a forecast of broad impact | 7 | 1 | 4 | 2 | 0 | no |
| Reviewer discussion moved one committee's scores | 5 | 1 | 1 | 3 | 0 | yes |
| Late objection left the authors no reply | 5 | 0 | 1 | 4 | 0 | yes |
| Area chair settled an even split for one side | 5 | 0 | 0 | 5 | 0 | no |
| Reviewers placed similar verdicts at different scores | 4 | 1 | 2 | 1 | 0 | yes |
| Area chair relied on off-record reviewer input | 4 | 1 | 0 | 3 | 0 | yes |
| Low score held on a peripheral point | 3 | 0 | 0 | 3 | 0 | yes |
| Unsure reviewers defaulted to a borderline score | 2 | 1 | 1 | 0 | 0 | yes |
| Audience or venue-fit objection lowered one committee | 2 | 1 | 1 | 0 | 0 | yes |
| Neighbouring-field reviewers contested the paper's framing | 2 | 0 | 0 | 2 | 0 | yes |
| Discarded detractor framed decision as accept-or-reject | 1 | 0 | 1 | 0 | 0 | yes |

## Stability: run 2 in reverse order

Run 2 processed the same 50 pairs in reverse order from an empty set and produced 38 reasons after merge.
26 of run 1's 33 reasons reappear in run 2 under another name; 6 of run 2's reasons have no
run 1 counterpart. On the aligned reasons the two matrices agree on 83% of cells (mean per-pair
Jaccard 0.52). The three most frequent reasons and the two area-chair reasons are stable in count; the
largest disagreement is 'meta-review dropped the reviewers' stated weaknesses' (33 pairs in run 1, 7 in run 2),
which run 2 split across other area-chair reasons. Details: `analysis/stage2/stability_run1_run2.json`,
`analysis/stage2/alignment_run1_run2.json`.

## How it was run

Model `claude-opus-5-5`. Stage 1 (notes per pair, all 301 pairs) at effort `max`. Stage 2 run 1: turns 1 to 6 at
effort `max`, turns 7 to 50 and back-fill and merge at effort `high` (turn times at `max` grew to 10 minutes; the
change is recorded in `run_1/README.md`). Run 2 entirely at `high`. Prompts: `analysis/stage1/prompt.md` (v1),
`analysis/stage2/prompt.md` (v2). Derivation: `scripts/build_stage2_matrix.py`; charts: `scripts/make_stage2_figure.py`;
stability: `scripts/compare_stage2_runs.py`.
