# Empirical claims used by the study

This file is deliverable 6 of the handoff (§2): the list of empirical claims, with sources.
It covers handoff §10.1 to §10.5 and the score scales of §3.2. The groups follow §10.

Each claim shows its value, its source, its handoff status, and the outcome of the check
made on 2026-10-02. Three verifiers made that check. Their notes are in
`docs/verification/neurips.md`, `docs/verification/icml.md` and `docs/verification/iclr.md`.

Machine-readable copies:

- `data/venues.csv`: one row per venue-year of §10.4. Load it with
  `peerreview.venues.load_venues()`.
- `data/experiments.json`: the NeurIPS 2014 and 2021 experiments and the ICLR
  inter-review agreement, with derived values computed from the raw counts.

The data files keep the handoff value wherever a source disagrees. The source value is in
`check_value` (CSV) or `check` (JSON). The values the study uses are in the `N_used`, `acc_rate_used` and `orals_used` columns of `data/venues.csv`, written by `scripts/build_venues_used.py`: the primary value where a primary source contradicts the handoff, and main-track oral counts.

**Handoff status key.** V = verified by the author against the primary source on 2 Oct 2026.
P = read from a primary source, not re-verified. S = secondary source. U = unverified or
conflicting.

**Check outcome key.**

- confirmed.
- partly confirmed: part of the claim holds, or it holds only under a stated definition.
- contradicted.
- not found: no primary source was located.
- not checked.

"Primary" means an official conference page, fact sheet, press release, PC post or
virtual-site data, PMLR, or the paper itself. Paper Copilot, csconfstats, Synced and the
`paperlists` dumps are secondary.

## Contradictions and open items

### Contradictions

A source disagrees with the handoff value. The data files keep the handoff value.

| # | Item | Handoff | Source value | Source | Effect on the study |
|---|---|---|---|---|---|
| 1 | NeurIPS 2021 committee mean-score correlation (§10.1, §10.7) | "not reported" (V absence) | 0.575 (initial scores), 0.586 (final scores) | [arXiv:2306.03262](https://arxiv.org/pdf/2306.03262), Fig. 1 caption | A direct calibration target (r12 = rho^2). `calibrate.py` already uses it. §10.7 must change. |
| 2 | NeurIPS 2025 orals | 87 | 77 main track (87 = 77 main + 7 D&B + 3 Position) | [virtual-site data](https://neurips.cc/static/virtual/data/neurips-2025-orals-posters.json) | §8.4 precision at the oral count. N is main track, so the matching K is 77. The §10.7 note "77 was wrong" is itself wrong. |
| 3 | NeurIPS 2025 awards | 4 | 3 main track (1 of the 4 is D&B) | [2025 fact sheet](https://media.neurips.cc/Conferences/NeurIPS2025/press/NeurIPS2025-Fact_Sheet.pdf) | Context only. |
| 4 | NeurIPS 2020 N | 9,454 | 9,467 | [press release](https://neurips.cc/media/Press/2020_NeurIPS_Press_Release.pdf) and three other primary sources | Small. The rate is 20.1% with either N. |
| 5 | NeurIPS 2021 rate | 25.7% | 25.6% (2,334 / 9,122) | [2021 fact sheet](https://neurips.cc/media/Press/NeurIPS_2021-Fact_Sheet.pdf) | Small. |
| 6 | NeurIPS 2022 N and rate, "P (fact sheet)" | 10,411; 25.6% | Fact sheet: 9,634 full submissions, 2,905 accepted (all tracks), "20%". 10,411 and 2,671 (25.66%) are Paper Copilot values. | [2022 fact sheet](https://media.neurips.cc/Conferences/NeurIPS2022/NeurIPS_2022_Fact_Sheet.pdf) | The status must be S. The study uses 9,634 (primary, full submissions), with 2,671 accepted and 184 orals (`N_used`, `acc_rate_used`, `orals_used` in `data/venues.csv`). |
| 7 | NeurIPS 2025: "volume forced SAC-level ranking that rejected some AC-recommended papers" (§10.5) | P | The PC post says space played a negligible role for the main track. The "about 400" figure is in news reports only. | [2025 PC post](https://blog.neurips.cc/2025/09/30/reflections-on-the-2025-review-process-from-the-program-committee-chairs/) | Process motivation only. Drop the "volume forced" wording. |
| 8 | ICML 2023 orals | 158 | 155 | [virtual-site data](https://icml.cc/static/virtual/data/icml-2023-orals-posters.json) | §8.4 precision at the oral count. |
| 9 | ICML 2026 realised reviews per paper (§10.3) | about 3.3 (S) | 3.80 (90,822 main-track reviews / 23,918 papers); 80.9% of analysed papers had exactly four | [arXiv:2609.19420](https://arxiv.org/pdf/2609.19420) | Supports R = 4 as current practice. |
| 10 | ICLR 2018 rate | 32.0% | 34.3% (336 accepted / 981). 32.0% = 314 / 981 counts posters only. | [official schedule](https://iclr.cc/Conferences/2018/Schedule?type=Poster) | §8.4 for 2018. |
| 11 | ICLR 2020 awards | 2 | 0: the PCs decided against a best-paper award (secondary source) | [Synced](https://syncedreview.com/2020/05/04/iclr-2020-virtual-conference-openly-available-online-no-best-paper-awards-this-year/) | Context only. |
| 12 | ICLR 2021 N and rate | 2,997; 28.7% | 3,014; 28.5% (860 accepted). 2,997 = 3,014 minus 17 desk rejects. | [2021 fact sheet](https://iclr.cc/media/Press/ICLR_2021_Fact_Sheet.pdf) | Small. |
| 13 | ICLR 2022 N, rate, orals | 3,328; 32.9%; 54 | 3,391; 32.26%; 55 (1,095 accepted) | [2022 fact sheet](https://iclr.cc/media/Press/ICLR_2022_Fact_Sheet.pdf) | Small. |
| 14 | ICLR acceptance threshold in mean score (§10.2) | near 5.11 (2024), 5.12 (2025) | 5.83 (2024), 5.81 (2025): the 50% point of a logistic fit on decided papers. 5.11 and 5.12 are the all-paper means. | own computation on [`paperlists`](https://github.com/papercopilot/paperlists); `results/iclr_variance.csv` agrees (5.835, 5.810) | §8.3 threshold check. The handoff values are means, not thresholds. |
| 15 | ICLR 2024 desk rejections (§10.5) | 53 | 54 (secondary only) | [Paper Copilot](https://papercopilot.com/statistics/iclr-statistics/) | Context only. |

### Open items

**Unverified row.** NeurIPS 2026 (30,709; 25.7%; 112 orals) has status V in the handoff. No
fact sheet, PC post or public virtual site exists. The official JSON export is duplicated, so
it cannot give counts. Treat the row as U.

**Main track or all tracks.** §10.4 says "main-track figures", but some values count other
tracks too. ICML 2024: 144 orals = 129 main + 15 position; 10 awards = 8 main + 2 position.
ICML 2025: 120 orals = 108 main + 12 position. NeurIPS 2025: see contradictions 2 and 3.
NeurIPS 2023 already uses the main-track count (67). The study counts main-track orals only (`orals_used`: ICML 2024 129, ICML 2025 108, NeurIPS 2025 77).

**N from secondary sources only.** NeurIPS 2018; ICML 2014, 2019, 2020, 2021, 2022, 2024,
2025; ICLR 2017, 2018, 2019, 2020. For most of these years a primary accepted count fits the
handoff rate. The exceptions are ICLR 2018 (see contradiction 10), ICML 2020 (PMLR has 1,084
papers, 21.7%) and ICML 2024 (the fact sheet gives the rate, not an exact count). ICLR 2017 has 490 or 507 by source. ICLR 2018
has 935, 981 or 1,013 by source.

**Rounding slips.** NeurIPS 2017: 679 / 3,240 = 20.96% (21.0%, not 20.9%). ICML 2023:
1,828 / 6,538 = 27.96% (28.0%; 1,827 gives 27.9%). ICLR 2023: 1,574 / 4,938 = 31.87%
(31.9%, not 31.8%). NeurIPS 2019: 21.2% uses 6,743; the PCs give 21.6% on 6,614.

**Blanks that a primary source can fill.** NeurIPS 2014 awards 2. NeurIPS 2015 orals 15,
awards 2. NeurIPS 2016 orals 45. NeurIPS 2022 orals 184 (fact sheet; the virtual site lists
no oral events). The CSV keeps these blank.

**Smaller corrections (partly confirmed).**

- NeurIPS 2014: 50% and 49% of one committee's accepts were rejected by the other, not 50%
  and 51%. 51% is the share that the other committee accepted.
- NeurIPS 2014: the notebook value 0.544 is the raw-score correlation. The calibrated value
  is 0.5456, which rounds to the published 0.55.
- NeurIPS 2014 "57%": 22.5% was the target rate the committees were given. The realised
  conference rate was 24.7%.
- ICLR 2026: 779 + 5,042 + 13,763 = 19,584, which is 59 more than 19,525. The source's own
  counts do not add up. The fact sheet gives 5,357 accepted; the retrospective gives 5,355.
- ICLR 2026 reviews per paper: about 3.9, not 4.1. The 18,746 denominator is not in the
  source. The dump has 75,859 reviews on 19,474 reviewed papers.
- ICLR 2026 scale: 4 and 6 are "marginally below/above the acceptance threshold". So the
  scale has borderline points but no neutral midpoint.
- ICLR 2023 "91 orals" is the notable-top-5% tier. The conference ran 248 oral talks.
- NeurIPS score labels: the handoff's ten labels hold for 2022 to 2024. 2021 used 1 to 10
  with percentile anchors. The 2025 page has no "top 2 to 3 percent" anchor.
- NeurIPS "ACs aim for four reviewers" is in the 2024 SAC page only, not the AC page, and
  not in 2025.
- ICLR 2025 desk rejections (148) and ICLR 2024 and 2025 withdrawal rates have no primary
  source. No ICLR 2024 or 2025 retrospective exists.

**§8.1 pairing of tier sizes and counts.** For the oral+spotlight tier (29 and 25 papers) the
other committee rejected 13 of 29 and 13 of 25. For spotlights only (25 and 23) it rejected
13 of 25 and 13 of 23. The handoff's §8.1 reconstruction mixes the two.
`scripts/run_validation_neurips2021.py` uses the correct pairing.

**NeurIPS 2021 base.** The quoted "23.0% at 22.7%" uses all 882 papers. It counts the 118
papers withdrawn in both copies as consistent rejects. On the 764 decided papers the values
are 26.6% at 26.2%. `calibrate.py` uses the 764 basis for the central level and keeps the
882 basis as a separate target. Both are in `data/experiments.json`.

**Wrong source links in the handoff.** ICML 2025 reviewer counts are on the AC instructions
page, not the reviewer instructions. The ICML 2026 scale is on the reviewer instructions page,
not the FAQ. The ICLR 2024 and 2025 rating labels are on the OpenReview review form, not the
reviewer guide. The ICML 2026 counts are in the ICML post on X and the PC paper, not the
awards post. The NeurIPS 2025 oral count must come from the virtual-site data, not the fact
sheet.

**Not checked.** The Cole/Bornmann row of §10.1. The claim that no published reviewer-leniency
estimate exists for ICLR or ICML. The Krippendorff-alpha values of §10.7.

**§10.7 gaps after this check.** The NeurIPS 2021 committee correlation exists (item 1). The
NeurIPS 2024 orals (61), the ICLR 2026 orals (224) and the ICLR 2026 scale now have primary
sources. New gaps: NeurIPS 2026 (no source), the secondary-only N values above, ICLR 2018
awards, and ICLR 2024 and 2025 desk-reject and withdrawal counts.

## §3.2 Score scales

| Scale (latent points) | Used by (handoff) | Check | Source |
|---|---|---|---|
| integer 1 to 10 | NeurIPS through 2024 | confirmed. The 2022 to 2024 pages have the handoff's labels. 2014 and 2021 also used 1 to 10, with other labels. | [NeurIPS 2024 reviewer guidelines](https://neurips.cc/Conferences/2024/ReviewerGuidelines); arXiv:2306.03262 App. B |
| integer 1 to 10 | ICML 2023 to 2024 | confirmed | [arXiv:2408.13430](https://arxiv.org/pdf/2408.13430) p. 5; [ICML 2024 reviewer instructions](https://icml.cc/Conferences/2024/ReviewerInstructions) |
| integer 1 to 10 | ICLR 2017 to 2019 and 2021 | confirmed (all ten values occur in each dump; secondary) | [`paperlists`](https://github.com/papercopilot/paperlists) |
| six-point (6 points from 1 to 10) | NeurIPS 2025 to 2026 | 2025 confirmed (6 Strong Accept to 1 Strong Reject). 2026 not checked. | [NeurIPS 2025 reviewer guidelines](https://neurips.cc/Conferences/2025/ReviewerGuidelines) |
| six-point | ICML 2026 | confirmed (6 strong accept to 1 strong reject; confidence 1 to 5) | [ICML 2026 reviewer instructions](https://icml.cc/Conferences/2026/ReviewerInstructions) |
| ICLR six-point 1, 3, 5, 6, 8, 10 | ICLR 2022 to 2025 | confirmed (dumps for 2022 and 2023; review forms for 2024 and 2025) | [ICLR 2025 review form](https://api2.openreview.net/invitations?id=ICLR.cc/2025/Conference/Submission5825/-/Official_Review&expired=true) |
| five-point (5 points from 1 to 10) | ICML 2025 | confirmed for the main track (5 strong accept, 4 accept, 3 weak accept, 2 weak reject, 1 reject; no confidence) | [ICML 2025 reviewer instructions](https://icml.cc/Conferences/2025/ReviewerInstructions) |
| not in the §3.2 table | ICLR 2020: 1, 3, 6, 8 | confirmed (secondary) | dump; [Synced](https://syncedreview.com/2019/12/20/iclr-2020-accepted-papers-announced/) |
| not in the §3.2 table | ICLR 2026: 0, 2, 4, 6, 8, 10 | confirmed | [ICLR 2026 review form](https://api2.openreview.net/invitations?id=ICLR.cc/2026/Conference/Submission18691/-/Official_Review&expired=true) |

## §10.1 Two-committee consistency experiments

Full counts and derived values: `data/experiments.json`.

| Claim | Value | Handoff status | Check | Source |
|---|---|---|---|---|
| NeurIPS 2014 design | 166 papers (about 10% of 1,678) had two independent decisions. 170 were chosen; 4 were withdrawn or rejected without review. | V | confirmed | [arXiv:2109.09774](https://arxiv.org/pdf/2109.09774) §2, Table 1 |
| NeurIPS 2014 2x2 table | 22 both accept; 22 committee 2 only; 21 committee 1 only; 101 both reject. Committee 1 accepted 43, committee 2 accepted 44. | V | confirmed. The handoff's "A only" (22) is committee 2. | [arXiv:2109.09774](https://arxiv.org/pdf/2109.09774) Table 1 |
| NeurIPS 2014 inconsistency | 43 / 166 = 25.9%. Acceptance 26.5% and 25.9%. | V | confirmed. Paper §2.2 has the typo 25.0%. | [Lawrence 2014 blog](https://inverseprobability.com/2014/12/16/the-nips-experiment); arXiv:2109.09774 App. C |
| NeurIPS 2014 share of accepts rejected by the other | 22 / 44 = 50% and 21 / 43 = 49% (handoff: 50% and 51%) | V | partly confirmed | [arXiv:2109.09774](https://arxiv.org/pdf/2109.09774) §2.2, App. C |
| Origin of the "57%" | 25.9% inconsistency applied to a 22.5% rate: 21/37 or 22/38. 22.5% was the target rate; the realised rate was 24.7%. | V | confirmed | [E. Price, 2014](http://blog.mrtz.org/2014/12/15/the-nips-experiment.html); arXiv:2109.09774 App. C.1 |
| NeurIPS 2014 committee mean-score correlation | 0.55 +/- 0.065 (calibrated scores). Notebook: 0.5440 raw, 0.5456 calibrated. | V | partly confirmed (0.544 is the raw value) | [arXiv:2109.09774](https://arxiv.org/pdf/2109.09774) Fig. 2; [notebook](https://raw.githubusercontent.com/lawrennd/neurips2014/master/notebooks/Reviewer%20Calibration.ipynb) |
| NeurIPS 2014 variance components | paper 1.28, reviewer offset 0.24, subjective 1.27. Offset share 0.24 / 2.79 = 8.6%. Subjective share after offsets 1.27 / 2.55 = 49.8%. | V | confirmed | [arXiv:2109.09774](https://arxiv.org/pdf/2109.09774) Table 2 |
| NeurIPS 2014 score-citation correlation | accepted 0.051 +/- 0.049 (n = 414, not significant); rejected 0.22 +/- 0.038 | V | confirmed | [arXiv:2109.09774](https://arxiv.org/pdf/2109.09774) Figs. 4 and 8 |
| NeurIPS 2021 accept-level inconsistency | 882 papers; 206 and 195 accepts, 99 in both; 203 (23.0%) inconsistent at 22.7% mean acceptance; random 35.1%. On the 764 decided papers: 26.6% at 26.2%. | V | confirmed | [arXiv:2306.03262](https://arxiv.org/pdf/2306.03262) §4.1, Table 1; [NeurIPS blog](https://blog.neurips.cc/2021/12/08/the-neurips-2021-consistency-experiment/) |
| NeurIPS 2021 spotlights rejected by the other committee | 13 of 25 and 13 of 23 (spotlights only) | V | confirmed | [NeurIPS blog](https://blog.neurips.cc/2021/12/08/the-neurips-2021-consistency-experiment/); Table 1 |
| NeurIPS 2021 oral+spotlight tier | 29 and 25 papers, 3 in both (all spotlight in both). The other committee rejected 13 of 29 and 13 of 25. No oral was rejected by the other committee. | V | confirmed | [arXiv:2306.03262](https://arxiv.org/pdf/2306.03262) Table 1, §4.1 |
| NeurIPS 2021 disagreement if only orals and spotlights were accepted | 48 / 882 = 5.4% at 3.1%; random 5.9%. The paper text says 5.8%. | not in handoff | confirmed from Table 1 | [arXiv:2306.03262](https://arxiv.org/pdf/2306.03262) |
| NeurIPS 2021 committee mean-score correlation | 0.575 (initial), 0.586 (final). Handoff: not reported. | V (absence) | **contradicted** | [arXiv:2306.03262](https://arxiv.org/pdf/2306.03262) Fig. 1 |
| NeurIPS 2021 disagreement by score band | No table. Figs. 2 and 3 plot disagreement against the acceptance rate for top-x% by mean score. | V (absence) | partly confirmed | [arXiv:2306.03262](https://arxiv.org/pdf/2306.03262) Figs. 2, 3 |
| NeurIPS 2021 recommendation process | The AC form had Accept (Oral) / (Spotlight) / (Poster) / Reject plus a qualifier. SACs and PCs set orals and spotlights jointly. Table 1 shows recommendations after calibration. | not in handoff | confirmed | [arXiv:2306.03262](https://arxiv.org/pdf/2306.03262) §2, §4.2, §5.1, App. B |
| NeurIPS 2021 main track | 9,122 submissions; 2,334 accepted (25.6%, handoff 25.7%) | P | partly confirmed | [2021 fact sheet](https://neurips.cc/media/Press/NeurIPS_2021-Fact_Sheet.pdf) |
| Low inter-reviewer agreement is general across fields | Cole, Cole & Simon 1981; Bornmann, Mutz & Daniel 2010 | S | not checked | the two papers |

## §10.2 Inter-review agreement and score dispersion

| Claim | Value | Handoff status | Check | Source |
|---|---|---|---|---|
| berenslab ICLR dataset, 2017 to 2024 | r = 0.40 over 244,226 review pairs (ordered, so each pair counts twice); 3.7 reviews per paper; 24,445 papers; 93% with 3 or 4 reviews | V | confirmed. Recompute: r = 0.399, 244,234 ordered pairs, 3.66 reviews, 92.8%. `results/iclr_pooled_pairs.csv` agrees. The value pools three scales. | [arXiv:2404.08403](https://arxiv.org/abs/2404.08403); [README](https://github.com/berenslab/iclr-dataset) |
| Paper Copilot mean paper-average rating | 5.18 (2022); 5.13, SD 1.33 (2023); about 5.11 (2024); 5.12, SD 1.25 (2025) | S | confirmed | [Paper Copilot](https://papercopilot.com/statistics/iclr-statistics/) |
| ICLR 2025 accepted and rejected means | accepted 6.43 (SD 0.68; poster 6.23, spotlight 7.35, oral 7.79); rejected 4.77 (SD 0.92) | S | confirmed | [Paper Copilot](https://papercopilot.com/statistics/iclr-statistics/) |
| Acceptance threshold in mean score | handoff: near 5.11 (2024) and 5.12 (2025) | S | **contradicted**: 5.83 and 5.81 (logistic 50% point) | own computation on [`paperlists`](https://github.com/papercopilot/paperlists) |
| ICLR 2025 mean score before and after discussion | 4.78 to 5.14 | S | confirmed; the ICLR fact sheet is a primary source | [ICLR 2025 fact sheet](https://media.iclr.cc/Conferences/ICLR2025/ICLR2025_Fact_Sheet.pdf) |
| Own ICC(1) decomposition, 2017 to 2020 | ICC(1) 0.58 / 0.41 / 0.46 / 0.39; within SD 1.03 to 1.19; between SD 1.00 to 1.20 | own computation | partly confirmed. ICC(1) 0.576 / 0.413 / 0.464 / 0.392. The SD ranges hold for 2017 to 2019 only; 2020 has within SD 1.72, between SD 1.38. ICC(1) is 0.36 to 0.42 for 2021 to 2025 and 0.18 for 2026. | [`paperlists`](https://github.com/papercopilot/paperlists); `results/iclr_variance.csv` |
| Rebuttal effects, ICLR 2024 and 2025 | 81% / 75% unchanged; 17% / 23% up; 1% / 1% down; modal change 5 to 6; accepted 57.6% / 55.7% (improved) vs 12.4% / 7.8% (unchanged) | V / S | confirmed; one primary source covers every part | [Kargaran et al., arXiv:2511.15462](https://arxiv.org/abs/2511.15462) |
| OpenReview reviewer IDs are per paper | 99.5% or more of the 4-character IDs occur once in 2024 to 2026; repeats fit random collisions | P (absence) | confirmed (ID part); "no published leniency estimate" not checked | [`paperlists`](https://github.com/papercopilot/paperlists) |

## §10.3 Reviews per paper and score scales

| Claim | Value | Handoff status | Check | Source |
|---|---|---|---|---|
| NeurIPS 2024 and 2025: at least three quality reviews before the author response | at least 3 | V | confirmed | [2025 SAC guidelines](https://neurips.cc/Conferences/2025/SAC-Guidelines); [2024 SAC guidelines](https://neurips.cc/Conferences/2024/SAC-Guidelines) |
| NeurIPS ACs aim for four reviewers | four qualified reviewers per paper | U | partly confirmed: 2024 SAC page only | [2024 SAC guidelines](https://neurips.cc/Conferences/2024/SAC-Guidelines) |
| ICML 2025 reviewers per paper | 4 assigned, at least 3 required | P | confirmed (AC page, not the cited reviewer page) | [ICML 2025 AC instructions](https://icml.cc/Conferences/2025/AreaChairInstructions) |
| ICML 2026 reviewers per paper | 4 assigned, at least 3 required; over 99% had 3 or more at rebuttal start | P | confirmed | [ICML 2026 AC instructions](https://icml.cc/Conferences/2026/AreaChairInstructions); [FAQ](https://icml.cc/Conferences/2026/PeerReviewFAQ) |
| ICML 2024 reviewer assignment | 3 auto-assigned plus 1 chosen by the AC; some papers end with 3 | P | confirmed | [ICML 2024 PC blog](https://medium.com/@icml2024pc/reviewing-at-icml-2024-a7aa81169d8c) (read through the RSS feed) |
| ICLR 2026 realised reviews per paper | handoff: about 4.1 (76,139 / 18,746) | V (counts) | partly confirmed: 76,139 holds; about 3.9 per reviewed paper | [ICLR 2026 retrospective](https://blog.iclr.cc/2026/03/31/a-retrospective-on-the-iclr-2026-review-process/) |
| ICML 2026 realised reviews per paper | handoff: about 3.3 | S | **contradicted**: 3.80 | [arXiv:2609.19420](https://arxiv.org/pdf/2609.19420) |
| NeurIPS overall score through 2024 | 1 to 10 (10 award quality ... 1 very strong reject); sub-scores 1 to 4; confidence 1 to 5 | V | partly confirmed: labels hold for 2022 to 2024 | [NeurIPS 2024 reviewer guidelines](https://neurips.cc/Conferences/2024/ReviewerGuidelines) |
| NeurIPS overall score from 2025 | 1 to 6 (6 strong accept ... 1 strong reject); sub-scores 1 to 4; confidence 1 to 5 | V | partly confirmed: no "top 2 to 3 percent" anchor | [NeurIPS 2025 reviewer guidelines](https://neurips.cc/Conferences/2025/ReviewerGuidelines) |
| ICML overall score | 1 to 10 (2023, 2024); 1 to 5, no confidence (2025 main track); 1 to 6 with confidence 1 to 5 (2026) | V (2025, 2026) / P (2023, 2024) | confirmed | [2024](https://icml.cc/Conferences/2024/ReviewerInstructions), [2025](https://icml.cc/Conferences/2025/ReviewerInstructions), [2026](https://icml.cc/Conferences/2026/ReviewerInstructions) reviewer instructions |
| ICLR rating 1 to 10 (2017 to 2019, 2021) and 2021 value counts | 14/167/905/2,289/2,685/2,832/1,999/495/112/10 | V | confirmed (secondary) | [`paperlists`](https://github.com/papercopilot/paperlists) |
| ICLR 2020 four-point scale | 1/3/6/8 | V | confirmed (secondary) | [`paperlists`](https://github.com/papercopilot/paperlists); [Synced](https://syncedreview.com/2019/12/20/iclr-2020-accepted-papers-announced/) |
| ICLR 2022 and 2023 value counts | 2022 310/3,223/3,771/3,714/2,089/54; 2023 465/4,711/5,126/5,326/2,846/101 | V | confirmed (secondary) | [`paperlists`](https://github.com/papercopilot/paperlists) |
| ICLR 2024 and 2025 rating labels | 1 strong reject, 3 reject, 5 marginally below, 6 marginally above, 8 accept, 10 strong accept | V | confirmed on the review form; the reviewer guide shows no scale | [ICLR 2025 review form](https://api2.openreview.net/invitations?id=ICLR.cc/2025/Conference/Submission5825/-/Official_Review&expired=true) |
| ICLR 2026 rating scale | {0, 2, 4, 6, 8, 10}; handoff: "no borderline point" | U | partly confirmed: the points hold; 4 and 6 are borderline labels | [ICLR 2026 review form](https://api2.openreview.net/invitations?id=ICLR.cc/2026/Conference/Submission18691/-/Official_Review&expired=true) |

## §10.4 Submissions, acceptance rates, orals and awards by venue-year

The columns N, Rate, Orals and Awards show the handoff values. "Accepted" is a source count
that agrees with N x rate to rounding. It is blank where no such count exists; then the
accepted count is round(rate x N). "Check" is the worst outcome over the row's claims. Bold text
marks a contradiction. Every source link is in `data/venues.csv` (`check_url`).

<!-- BEGIN 10.4 TABLES -->
### NeurIPS

| Year | N | Rate | Accepted | Orals | Awards | Status | Check | Finding | Source |
|---|---|---|---|---|---|---|---|---|---|
| 2014 | 1,678 | 24.7% | 414 | 20 |  | V | confirmed | All values hold; 414 accepted. A primary source gives 2 awards (handoff blank). | [link](https://media.nips.cc/Conferences/2014/NIPS-2014-Conference-Book.pdf) |
| 2015 | 1,838 | 21.9% | 403 |  |  | S | confirmed | N and rate hold; 403 accepted. Primary sources give 15 orals and 2 awards (handoff blank). | [link](https://media.nips.cc/Conferences/2015/NIPS-2015-Conference-Book.pdf) |
| 2016 | 2,403 | 23.6% | 568 |  | 1 | S | partly confirmed | N and rate hold; 568 accepted (2,403 is the reviewed count). Awards: 1 best paper plus 1 best student paper. A primary source gives 45 orals (handoff blank). | [link](https://media.nips.cc/Conferences/2016/NIPS-2016-Conference-Book.pdf) |
| 2017 | 3,240 | 20.9% | 679 | 40 | 3 | S | partly confirmed | 679 accepted, so the rate is 20.96% (21.0%), not 20.9%. Orals and awards hold. | [link](https://media.nips.cc/Conferences/NIPS2017/Eventmedia/opening_remarks.pdf) |
| 2018 | 4,856 | 20.8% | 1,009 | 30 | 4 | S | not found | No primary source gives N. The proceedings list 1,009 papers, which fits the rate. Orals and awards hold. | [link](https://papercopilot.com/statistics/neurips-statistics/) |
| 2019 | 6,743 | 21.2% | 1,428 | 36 | 2 | S | partly confirmed | N holds (after filtering). The PCs give 21.6% on the 6,614 papers at notification. Orals and awards hold. | [link](https://web.archive.org/web/20200624120539/https://medium.com/@NeurIPSConf/what-we-learned-from-neurips-2019-data-111ab996462c) |
| 2020 | 9,454 | 20.1% | 1,900 | 105 | 3 | S | contradicted | **N is 9,467** in four primary sources. The rate is 20.1% with either N. Orals and awards hold. | [link](https://neurips.cc/media/Press/2020_NeurIPS_Press_Release.pdf) |
| 2021 | 9,122 | 25.7% |  | 55 | 6 | P | contradicted | **The rate is 25.6%** (2,334 / 9,122). N, orals and awards hold. | [link](https://neurips.cc/media/Press/NeurIPS_2021-Fact_Sheet.pdf) |
| 2022 | 10,411 | 25.6% |  |  | 13 | P | contradicted | **The fact sheet does not give 10,411 or 25.6%**; Paper Copilot does. The fact sheet gives 9,634 full submissions and 184 main-track orals. Awards hold. | [link](https://media.neurips.cc/Conferences/NeurIPS2022/NeurIPS_2022_Fact_Sheet.pdf) |
| 2023 | 12,343 | 26.1% | 3,218 | 67 | 2 | P/S | confirmed | All values hold. The 67 orals are main track (the fact sheet's 77 include 10 D&B orals). | [link](https://media.neurips.cc/Conferences/NeurIPS2023/NeurIPS2023-Fact_Sheet.pdf) |
| 2024 | 15,671 | 25.8% | 4,037 | 61 | 2 | P/U | confirmed | All values hold. The virtual-site data confirm the 61 main-track orals. | [link](https://media.neurips.cc/Conferences/NeurIPS2024/NeurIPS2024-Fact_Sheet.pdf) |
| 2025 | 21,575 | 24.5% | 5,290 | 87 | 4 | V | contradicted | N and rate hold. **Main-track orals are 77** (the 87 include 7 D&B and 3 Position orals). **Main-track awards are 3** (one of the 4 is D&B). | [link](https://neurips.cc/static/virtual/data/neurips-2025-orals-posters.json) |
| 2026 | 30,709 | 25.7% | 7,900 | 112 |  | V | not found | No primary source exists yet. The row is unverified (status U, not V). | [link](https://neurips.cc/static/virtual/data/neurips-2026-orals-posters.json) |

### ICML

| Year | N | Rate | Accepted | Orals | Awards | Status | Check | Finding | Source |
|---|---|---|---|---|---|---|---|---|---|
| 2014 | 1,238 | 25.0% | 310 |  |  | S | not found | No primary source gives N. PMLR v32 has 310 papers, which fits the rate. | [link](https://proceedings.mlr.press/v32/) |
| 2015 | 1,037 | 26.0% | 270 |  |  | S | confirmed | The PC letter gives 270 of 1,037 (26.0%). | [link](https://icml.cc/2015/booklet-icml2015.online.pdf) |
| 2016 | 1,320 | 24.4% | 322 |  |  | S | confirmed | The PC letter gives 322 of 1,320 (24.4%). Every paper had a talk, so an oral count has no meaning. | [link](https://web.archive.org/web/20160615062007id_/http://icml.cc:80/2016/wp-content/uploads/ICML-Book-Web-Version.pdf) |
| 2017 | 1,676 | 25.9% | 434 |  |  | S | confirmed | The PC letter gives 434 of 1,676 (25.9%). | [link](https://media.nips.cc/Conferences/ICML2017/ICML-2017-Conference-Book.pdf) |
| 2018 | 2,473 | 25.1% | 621 |  |  | S | confirmed | The PC letter gives 621 of 2,473 (25.1%). | [link](https://media.nips.cc/Conferences/ICML2018/ICML-2018-Conference-Book.pdf) |
| 2019 | 3,424 | 22.6% | 773 |  |  | S | not found | No primary source gives N. PMLR v97 has 773 papers, which fits the rate. | [link](https://proceedings.mlr.press/v97/) |
| 2020 | 4,990 | 21.8% | 1,088 |  | 2 | S | not found | No primary source gives N. PMLR v119 has 1,084 papers (21.7%); 1,088 were announced (21.8%). Awards hold. | [link](https://proceedings.mlr.press/v119/) |
| 2021 | 5,513 | 21.5% | 1,183 | 166 | 1 | S | not found | No primary source gives N. PMLR v139 has 1,183 papers, which fits the rate. Orals and awards hold. | [link](https://proceedings.mlr.press/v139/) |
| 2022 | 5,630 | 21.9% | 1,233 | 118 | 10 | S | not found | No primary source gives N. PMLR v162 has 1,233 papers, which fits the rate. Orals and awards hold. | [link](https://proceedings.mlr.press/v162/) |
| 2023 | 6,538 | 27.9% | 1,828 | 158 | 6 | S | contradicted | N and rate hold (1,828 accepted). **The virtual site lists 155 orals**, not 158. | [link](https://icml.cc/static/virtual/data/icml-2023-orals-posters.json) |
| 2024 | 9,473 | 27.5% |  | 144 | 10 | P | partly confirmed | The fact sheet gives the rate but not N; 9,473 is secondary (Paper Copilot: 9,653). The 144 orals and 10 awards include position papers; the main track has 129 and 8. | [link](https://media.icml.cc/Conferences/ICML2024/ICML2024_Fact_Sheet.pdf) |
| 2025 | 12,107 | 26.9% | 3,260 | 120 | 6 | V | partly confirmed | N is secondary only. The 120 orals include 12 position-track orals; the main track has 108. Accepted count and awards hold. | [link](https://media.icml.cc/Conferences/ICML2025/ICML2025_Fact_Sheet.pdf) |
| 2026 | 23,918 | 26.6% | 6,352 | 159 | 2 | V | confirmed | All values hold (ICML post; PC paper). The fact sheet's 24,661 and 6,552 include the position track. | [link](https://x.com/icmlconf/status/2049919242862985559) |

### ICLR

| Year | N | Rate | Accepted | Orals | Awards | Status | Check | Finding | Source |
|---|---|---|---|---|---|---|---|---|---|
| 2017 | 507 | 39.1% | 198 | 15 | 3 | S | not found | No primary source gives N (secondary lists give 490 or 507). The official list has 198 accepted papers. Orals and awards hold. | [link](https://iclr.cc/archive/www/doku.php%3Fid=iclr2017:conference_posters.html) |
| 2018 | 981 | 32.0% |  | 23 | 3 | S | contradicted | No primary source gives N. **The official schedule lists 336 accepted papers**, so the rate is 34.3% on 981; the 32.0% counts posters only. Orals hold; awards have a secondary source only. | [link](https://iclr.cc/Conferences/2018/Schedule?type=Poster) |
| 2019 | 1,591 | 31.4% | 500 | 24 | 2 | S | confirmed | All values hold. N has a secondary source only. | [link](https://iclr.cc/Conferences/2019/Schedule?type=Poster) |
| 2020 | 2,594 | 26.5% | 687 | 48 | 2 | S | contradicted | N, rate and orals hold. **Synced reports no best-paper award** in 2020 (secondary source). | [link](https://syncedreview.com/2020/05/04/iclr-2020-virtual-conference-openly-available-online-no-best-paper-awards-this-year/) |
| 2021 | 2,997 | 28.7% | 860 | 53 | 8 | S | contradicted | **The fact sheet gives 3,014 submitted** and 860 accepted (28.5%). 2,997 excludes 17 desk rejects. Orals and awards hold. | [link](https://iclr.cc/media/Press/ICLR_2021_Fact_Sheet.pdf) |
| 2022 | 3,328 | 32.9% | 1,095 | 54 | 7 | S | contradicted | **The fact sheet gives 3,391 submissions, 32.26% and 55 orals.** 1,095 accepted. Awards hold. | [link](https://iclr.cc/media/Press/ICLR_2022_Fact_Sheet.pdf) |
| 2023 | 4,938 | 31.8% | 1,574 | 91 | 4 | S | partly confirmed | N holds. 1,574 / 4,938 = 31.87%, which rounds to 31.9%. The 91 is the top-5% tier; the conference ran 248 oral talks. | [link](https://iclr.cc/media/Press/ICLR_2023_Press_Release.pdf) |
| 2024 | 7,262 | 31.1% | 2,260 | 86 | 5 | P | confirmed | All values hold. | [link](https://media.iclr.cc/Conferences/ICLR2024/ICLR2024_Press_Release.pdf) |
| 2025 | 11,603 | 31.9% | 3,704 | 213 | 3 | V | partly confirmed | All values hold. The 380 spotlights come from the virtual site; the fact sheet says 85 spotlight posters. | [link](https://media.iclr.cc/Conferences/ICLR2025/ICLR2025_Fact_Sheet.pdf) |
| 2026 (valid) | 19,525 | 27.4% | 5,355 | 224 | 2 | V/U | partly confirmed | N, accepted (5,355), orals (224) and awards hold. The three sub-counts add to 19,584, not 19,525. The fact sheet gives 5,357 accepted. | [link](https://blog.iclr.cc/2026/03/31/a-retrospective-on-the-iclr-2026-review-process/) |
| 2026 (decided) | 13,763 | 38.9% | 5,355 | 224 | 2 | V/U | partly confirmed | 5,355 / 13,763 = 38.9%. See the row above. | [link](https://blog.iclr.cc/2026/03/31/a-retrospective-on-the-iclr-2026-review-process/) |
<!-- END 10.4 TABLES -->

## §10.4a Main-track spotlights by venue-year

Added on 2026-10-04 for Fig. 1b. A spotlight is the main-track tier between oral and poster
("spotlight", "spotlight poster", or ICLR 2023's "notable-top-25%"). Counts exclude orals,
Datasets & Benchmarks and position papers. A blank count means the venue had no such tier
that year. ICML 2021 and 2022 labelled every non-oral paper a spotlight, so the label marks no
selective tier there. One agent per venue found the counts and a second agent re-checked
each one at its source. Machine-readable copy: `data/spotlights.csv`.

| Venue | Year | Spotlights | Tier | Source | Finding |
|---|---|---|---|---|---|
| NeurIPS | 2014 | 62 | spotlight | [primary](https://neurips.cc/Conferences/2014/Schedule?type=Spotlight) | Schedule lists 62 spotlight papers; Lawrence's slides give 20 orals, 62 spotlights, 331 posters. |
| NeurIPS | 2015 | 67 | spotlight | [primary](https://neurips.cc/Conferences/2015/Schedule?type=Spotlight) | Schedule lists 67; 15 orals + 67 + 321 posters = 403. |
| NeurIPS | 2016 | – | no spotlight tier | [primary](https://neurips.cc/Conferences/2016/Schedule?type=Oral) | Schedule and conference book have orals and posters only. |
| NeurIPS | 2017 | 112 | spotlight | [primary](https://neurips.cc/Conferences/2017/Schedule?type=Spotlight) | Schedule lists 112; PC opening remarks give 40/112/527 = 679. |
| NeurIPS | 2018 | 167 | spotlight | [primary](https://neurips.cc/Conferences/2018/Schedule?type=Spotlight) | Schedule and virtual site list 167; secondary sources give 168. |
| NeurIPS | 2019 | 164 | spotlight | [primary](https://neurips.cc/Conferences/2019/Schedule?type=Spotlight) | Schedule and virtual site list 164; 36 + 164 + 1,228 = 1,428. |
| NeurIPS | 2020 | 280 | spotlight | [primary](https://neurips.cc/Conferences/2020/Schedule?type=Spotlight) | Schedule and virtual site list 280; PC post gives 105 orals and 280 spotlights. |
| NeurIPS | 2021 | 260 | spotlight | [primary](https://arxiv.org/abs/2306.03262) | PC paper section 2: 55 orals, 260 spotlights, 2,019 posters; schedule lists 260. |
| NeurIPS | 2022 | – | no spotlight tier | [primary](https://media.neurips.cc/Conferences/NeurIPS2022/NeurIPS_2022_Fact_Sheet.pdf) | Fact sheet and PC blog give orals and posters only; no source names a spotlight tier (inference). |
| NeurIPS | 2023 | 378 | spotlight poster | [primary](https://neurips.cc/static/virtual/data/neurips-2023-orals-posters.json) | Unique main-track papers in virtual-site data; all-track page shows 400 = 378 + 22 D&B. |
| NeurIPS | 2024 | 326 | spotlight poster | [primary](https://neurips.cc/static/virtual/data/neurips-2024-orals-posters.json) | Unique main-track papers in virtual-site data; a secondary source gives 327. |
| NeurIPS | 2025 | 687 | spotlight poster | [primary](https://neurips.cc/static/virtual/data/neurips-2025-orals-posters.json) | Unique main-track papers in virtual-site data; secondary sources quoting the notification give 688. |
| NeurIPS | 2026 | 292 | spotlight | [secondary](https://agihunt.info/en/p/1a0d4e8d89e797c4ba011942d61) | Unverified: secondary article quoting the notification (112 orals + 292 spotlights); the official JSON is duplicated (302 records). |
| ICML | 2014 | – | no spotlight tier | primary | Every accepted paper had the same talk or poster format; no spotlight tier. |
| ICML | 2015 | – | no spotlight tier | primary | Every accepted paper had the same talk or poster format; no spotlight tier. |
| ICML | 2016 | – | no spotlight tier | primary | Every accepted paper had the same talk or poster format; no spotlight tier. |
| ICML | 2017 | – | no spotlight tier | primary | Every accepted paper had the same talk or poster format; no spotlight tier. |
| ICML | 2018 | – | no spotlight tier | primary | Every accepted paper had the same talk or poster format; no spotlight tier. |
| ICML | 2019 | – | no spotlight tier | primary | Every accepted paper had the same talk or poster format; no spotlight tier. |
| ICML | 2020 | – | no spotlight tier | primary | Every accepted paper had the same talk or poster format; no spotlight tier. |
| ICML | 2021 | – | no spotlight tier | [primary](https://icml.cc/Conferences/2021/Schedule?type=Spotlight) | Every non-oral paper was labelled spotlight (1,017 of 1,183), so the label marks no selective tier. |
| ICML | 2022 | – | no spotlight tier | [primary](https://icml.cc/Conferences/2022/Schedule?type=Spotlight) | Every non-oral paper was labelled spotlight (1,115 of 1,233), so the label marks no selective tier. |
| ICML | 2023 | – | no spotlight tier | [primary](https://icml.cc/Conferences/2023/Schedule?type=Oral) | Schedule has orals and posters only. |
| ICML | 2024 | 180 | spotlight poster | [primary](https://icml.cc/virtual/2024/events/2024SpotlightPosters) | Virtual site lists 191 across tracks; 11 are position papers. |
| ICML | 2025 | 213 | spotlight poster | [secondary](https://papers.cool/venue/ICML.2025?group=Spotlight) | OpenReview labels: 225 non-oral spotlights, 12 position papers. Virtual site lists 224 (all tracks). A decision-time count gives 313 including 108 orals, i.e. 205. |
| ICML | 2026 | 377 | spotlight poster | [primary](https://x.com/icmlconf/status/2049919242862985559) | ICML: 536 main-track spotlight papers (2.2%), orals chosen from them; 536 - 159 main orals = 377. |
| ICLR | 2017 | – | no spotlight tier | [primary](https://iclr.cc/archive/www/doku.php%3Fid=iclr2017:schedule.html) | Contributed talks and posters only. |
| ICLR | 2018 | – | no spotlight tier | [primary](https://iclr.cc/Conferences/2018/Schedule) | Orals and posters only. |
| ICLR | 2019 | – | no spotlight tier | [primary](https://iclr.cc/Conferences/2019/Schedule) | Orals and posters only. |
| ICLR | 2020 | 108 | spotlight | [secondary](https://syncedreview.com/2019/12/20/iclr-2020-accepted-papers-announced/) | Quotes the PC post: 108 spotlights and 48 talks of 687 accepted; paperlists agrees. |
| ICLR | 2021 | 114 | spotlight | [primary](https://iclr.cc/virtual/2021/events/spotlight) | Virtual site lists 114; paperlists agrees. |
| ICLR | 2022 | 175 | spotlight | [primary](https://iclr.cc/media/Press/ICLR_2022_Fact_Sheet.pdf) | Fact sheet and virtual site give 175; paperlists gives 174. |
| ICLR | 2023 | 280 | notable-top-25% | [secondary](https://papercopilot.com/venue-overview/iclr-2023-venue-overview/) | Author Guide: notable-top-25% was traditionally Accept (spotlight). Paper Copilot and paperlists give 280. |
| ICLR | 2024 | 367 | spotlight poster | [primary](https://iclr.cc/virtual/2024/events/spotlight-posters) | Virtual site lists 367; paperlists agrees. |
| ICLR | 2025 | 380 | spotlight poster | [primary](https://iclr.cc/virtual/2025/events/spotlight-posters) | Virtual site lists 380; the fact sheet's 85 conflicts with every other source and the accepted total. |
| ICLR | 2026 | – | no spotlight tier | [primary](https://iclr.cc/virtual/2026/events/spotlight-posters) | Virtual site lists 0 spotlights; fact sheet and paperlists have orals and posters only. |

## §10.5 How decisions are made

| Claim | Value | Handoff status | Check | Source |
|---|---|---|---|---|
| No venue decides by mean score alone (NeurIPS) | AC meta-review and recommendation; SAC calibration across ACs; PCs finalise; orals and spotlights decided jointly by SACs and PCs | P | partly confirmed: the oral/spotlight process is sourced for 2021 only | [NeurIPS 2025 SAC guidelines](https://neurips.cc/Conferences/2025/SAC-Guidelines); arXiv:2306.03262 §2 |
| No venue decides by mean score alone (ICML) | ACs recommend from review content, not average scores; SACs calibrate; the average score is not a direct indication of the decision | not in handoff | confirmed | [ICML 2026 AC instructions](https://icml.cc/Conferences/2026/AreaChairInstructions); [FAQ](https://icml.cc/Conferences/2026/PeerReviewFAQ) |
| No venue decides by mean score alone (ICLR) | AC/SAC/PC calibration separate from the accept recommendation | P | not checked | ICLR reviewer and AC guides |
| NeurIPS 2025 AC overrides | ACs moved papers in both directions | P | confirmed | [2025 PC post](https://blog.neurips.cc/2025/09/30/reflections-on-the-2025-review-process-from-the-program-committee-chairs/) |
| NeurIPS 2025 SAC ranking | volume forced SAC-level ranking that rejected some AC-recommended papers (about 400) | P / S | **contradicted** by the PC post (space played a negligible role for the main track); 400 is in news reports only | [2025 PC post](https://blog.neurips.cc/2025/09/30/reflections-on-the-2025-review-process-from-the-program-committee-chairs/); [36kr](https://www.36kr.com/p/3447809868404355) (secondary) |
| NeurIPS 2025 committee | 20,518 reviewers, 1,663 ACs, 199 SACs (main track); 21,575 / 1,663 = 13.0 papers per AC | P | confirmed. All tracks: 21,921, 1,985, 240. | [2025 PC post](https://blog.neurips.cc/2025/09/30/reflections-on-the-2025-review-process-from-the-program-committee-chairs/) |
| ICLR desk rejections | 53 (2024), 148 (2025), 779 (2026) | P / S | 2024 contradicted (54, secondary); 2025 partly confirmed (148, secondary; 70 in the dump); 2026 confirmed | [Paper Copilot](https://papercopilot.com/statistics/iclr-statistics/); [ICLR 2026 retrospective](https://blog.iclr.cc/2026/03/31/a-retrospective-on-the-iclr-2026-review-process/) |
| ICLR withdrawal rates | 22% (2024), 25.6% (2025), 25.8% (2026) | P / S | 2024 partly confirmed (22.66% of 7,304, secondary); 2025 confirmed (secondary); 2026 confirmed (5,042 / 19,525) | [Paper Copilot](https://papercopilot.com/statistics/iclr-statistics/); [ICLR 2026 retrospective](https://blog.iclr.cc/2026/03/31/a-retrospective-on-the-iclr-2026-review-process/) |
| ICML 2026 desk rejections for LLM-review violations | 497 papers (about 2%), from 398 reciprocal reviewers who broke Policy A | P / S | confirmed | [ICML blog](https://blog.icml.cc/2026/03/18/on-violations-of-llm-review-policies/) |
| NeurIPS oral share of submissions | about 1.2% (2014) to about 0.4% (2025 to 2026) | derived | partly confirmed: 20 / 1,678 = 1.19% (2014); 77 / 21,575 = 0.36% (2025 main track; 87 gives 0.40%); 112 / 30,709 = 0.36% (2026, unverified inputs) | `data/venues.csv` |

## §10.6 Background literature

Handoff §10.6 lists the methods and context papers. They supply no data to the study, so they were not checked.
