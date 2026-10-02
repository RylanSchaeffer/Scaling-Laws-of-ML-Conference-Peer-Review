# Verification of the ICLR claims in handoff §10

Scope: every ICLR row of handoff §10.4; the ICLR rows of §10.2 and §10.3; the
desk-rejection and withdrawal figures of §10.5 (ICLR and the ICML 2026 figure).

All sources were accessed on **2026-10-02**.

Outcome key: **confirmed**; **partly confirmed** (part of the claim holds, or
it holds only under a stated definition); **contradicted**; **not found** (no
source with this value); **not checked**.

Source kind: **primary** = official ICLR/ICML fact sheet, press release, blog
post, conference web page, OpenReview review form, or the paper itself.
**secondary** = Paper Copilot, its `paperlists` dumps, news, other lists.

Access limits:

- `openreview.net` and the `api2.openreview.net/notes` endpoint return a
  "challenge verification" page. I did not try to get around it. So no counts
  come directly from OpenReview venue pages.
- The `api2.openreview.net/invitations` endpoint is open. It gave the official
  review forms (rating scales) for 2024, 2025 and 2026.
- Where no primary count exists, I used the `papercopilot/paperlists` dumps
  (OpenReview mirrors, secondary) and recomputed the numbers myself.

## Main corrections

1. **ICLR 2026 orals = 224 is now confirmed** (2026 fact sheet; 224 papers with
   decision "Accept (Oral)" on the official virtual site). The 2026 awards
   count (2, plus 1 honorable mention) is confirmed.
2. **ICLR 2026 rating scale {0,2,4,6,8,10} is confirmed** from the OpenReview
   review form. But the handoff phrase "no borderline point" is wrong: 4 and 6
   carry the labels "marginally below" and "marginally above the acceptance
   threshold". The scale has no neutral midpoint. The ICLR reviewer-guide pages
   (2024, 2025, 2026) do not list any rating scale; cite the review form.
3. **ICLR 2026 counts in the retrospective do not add up.**
   779 + 5,042 + 13,763 = 19,584, not 19,525 (a gap of 59). The retrospective
   says 5,355 accepted; the fact sheet says 5,357. The retrospective itself
   calls 27.4% (accepted / valid submissions) "the acceptance rate". 38.9% is
   accepted / decided. Both arithmetic values are right.
4. **ICLR 2026 "about 4.1 reviews per paper" is too high.** The 18,746
   denominator is not in the source; it is 19,525 − 779. The dump has 75,859
   reviews on 19,474 reviewed papers (3.90 per paper), and 3.90 per decided
   paper. Withdrawn and desk-rejected papers also got reviews.
5. **ICLR 2022 row is wrong.** Fact sheet: 3,391 submissions, 1,095 accepted,
   32.26%, 55 orals (handoff: 3,328, 32.9%, 54).
6. **ICLR 2021 submissions.** Fact sheet: 3,014 submitted, 860 accepted, so
   28.5% (handoff: 2,997 and 28.7%; 2,997 = 3,014 minus 17 desk rejects).
7. **ICLR 2018 acceptance rate 32.0% is wrong.** The official 2018 schedule
   lists 336 accepted conference papers (orals included; dump: 314 posters +
   23 orals = 337). The 32.0% figure (lixin4ever list, 314/981) counts only
   posters as accepted. With N = 981 the rate is about 34.3%. The submission
   count itself has no primary source; secondary sources give 935, 981, 1,013.
8. **ICLR 2020 awards = 2 is contradicted.** Synced reports the general chair
   said the PCs decided against a best-paper award in 2020. No official ICLR
   2020 award page lists any paper.
9. **ICLR 2025 fact sheet says "85 Spotlight Posters", not 380.** The official
   virtual site lists 380 papers with "Accept (Spotlight)". So 380 is right,
   but the handoff attributes it to the fact sheet.
10. **ICLR 2023 "91 orals"** is the count of "notable-top-5%" papers. The
    conference ran 248 oral-session talks (69 top-5% and 178 top-25%).
11. **"Acceptance threshold near 5.11 (2024) and 5.12 (2025)"** equals the
    all-paper mean, not a threshold. A logistic fit on decided papers in the
    dumps puts the 50% acceptance point at 5.83 (2024) and 5.81 (2025).
12. **berenslab "244,226 pairs" counts ordered pairs.** My recompute from the
    dumps gives 244,234 ordered pairs = 122,117 distinct pairs, r = 0.399,
    mean 3.66 reviews per reviewed paper, 92.8% with 3 or 4 reviews.
13. **Desk rejects 2024 (53) and 2025 (148), withdrawals 2024 (22%) and 2025
    (25.6%) have no primary source.** Paper Copilot gives 54 and 148, and
    22.66% and 25.64%. Only the 2026 figures are primary.

## §10.4 ICLR rows: submissions, acceptance rate, orals, awards

"accepted" below is the count of accepted main-track papers.

| Year | Quantity | Handoff | Found | Outcome | Source | Kind |
|---|---|---|---|---|---|---|
| 2017 | N | 507 | no primary; Paper Copilot and dump 490; lixin4ever 507 | not found | papercopilot.com/statistics/iclr-statistics/ ; github.com/lixin4ever/Conference-Acceptance-Rate | secondary |
| 2017 | rate | 39.1% | 198 accepted (official poster list, orals included); 198/507 = 39.1%; 198/490 = 40.4% | partly confirmed | https://iclr.cc/archive/www/doku.php%3Fid=iclr2017:conference_posters.html | primary (count) |
| 2017 | orals | 15 | 15 contributed talks | confirmed | https://iclr.cc/archive/www/doku.php%3Fid=iclr2017:schedule.html | primary |
| 2017 | awards | 3 | 3 best papers | confirmed | https://iclr.cc/archive/www/doku.php%3Fid=iclr2017:main.html | primary |
| 2018 | N | 981 | no primary; Synced 935; Paper Copilot 1,013; lixin4ever 981 | not found | https://syncedreview.com/2018/04/30/iclr-2018-kicks-off-in-vancouver/ | secondary |
| 2018 | rate | 32.0% | 336 accepted on official schedule; 336/981 = 34.3% | contradicted | https://iclr.cc/Conferences/2018/Schedule?type=Poster | primary (count) |
| 2018 | orals | 23 | 23 | confirmed | https://iclr.cc/Conferences/2018/Schedule?type=Oral | primary |
| 2018 | awards | 3 | 3 best papers (no official page found) | confirmed | https://syncedreview.com/2018/04/30/iclr-2018-kicks-off-in-vancouver/ | secondary |
| 2019 | N | 1,591 | 1,591 per Synced; Paper Copilot 1,579 | confirmed | https://syncedreview.com/tag/iclr-2019/ | secondary |
| 2019 | rate | 31.4% | 500 accepted on official schedule; 500/1,591 = 31.4% | confirmed | https://iclr.cc/Conferences/2019/Schedule?type=Poster | primary (count) |
| 2019 | orals | 24 | 24 (plus one debate session) | confirmed | https://iclr.cc/Conferences/2019/Schedule?type=Oral | primary |
| 2019 | awards | 2 | 2 best papers | confirmed | https://iclr.cc/Conferences/2019/Awards | primary |
| 2020 | N | 2,594 | 2,594 (Synced, citing PCs; Paper Copilot) | confirmed | https://syncedreview.com/2019/12/20/iclr-2020-accepted-papers-announced/ | secondary |
| 2020 | rate | 26.5% | 687 accepted on official virtual site; 687/2,594 = 26.5% | confirmed | https://iclr.cc/virtual_2020/papers.json | primary (count) |
| 2020 | orals | 48 | 48 talks (Synced; dump status "Talk" 48) | confirmed | https://syncedreview.com/2019/12/20/iclr-2020-accepted-papers-announced/ | secondary |
| 2020 | awards | 2 | none: PCs decided against best paper (Synced, quoting general chair); no official award list | contradicted | https://syncedreview.com/2020/05/04/iclr-2020-virtual-conference-openly-available-online-no-best-paper-awards-this-year/ | secondary |
| 2021 | N | 2,997 | 3,014 submitted | contradicted | https://iclr.cc/media/Press/ICLR_2021_Fact_Sheet.pdf | primary |
| 2021 | rate | 28.7% | 860 accepted; 860/3,014 = 28.5% | contradicted | same | primary |
| 2021 | orals | 53 | 53 | confirmed | same | primary |
| 2021 | awards | 8 | 8 outstanding papers | confirmed | same | primary |
| 2022 | N | 3,328 | 3,391 | contradicted | https://iclr.cc/media/Press/ICLR_2022_Fact_Sheet.pdf | primary |
| 2022 | rate | 32.9% | 1,095 accepted, 32.26% | contradicted | same | primary |
| 2022 | orals | 54 | 55 (fact sheet and virtual site) | contradicted | same; https://iclr.cc/static/virtual/data/iclr-2022-orals-posters.json | primary |
| 2022 | awards | 7 | 7 outstanding (+3 honorable mentions) | confirmed | https://blog.iclr.cc/2022/04/20/announcing-the-iclr-2022-outstanding-paper-award-recipients/ | primary |
| 2023 | N | 4,938 | 4,938 | confirmed | https://iclr.cc/media/Press/ICLR_2023_Press_Release.pdf | primary |
| 2023 | rate | 31.8% | 1,574 accepted; 1,574/4,938 = 31.87%, rounds to 31.9% | partly confirmed | same | primary |
| 2023 | orals | 91 | 91 "notable-top-5%"; 248 oral-session talks | partly confirmed | https://iclr.cc/static/virtual/data/iclr-2023-orals-posters.json | primary |
| 2023 | awards | 4 | 4 outstanding (+5 honorable mentions) | confirmed | https://blog.iclr.cc/2023/03/21/announcing-the-iclr-2023-outstanding-paper-award-recipients/ | primary |
| 2024 | N | 7,262 | 7,262 (press release); Paper Copilot 7,304 | confirmed | https://media.iclr.cc/Conferences/ICLR2024/ICLR2024_Press_Release.pdf | primary |
| 2024 | rate | 31.1% | 2,260 accepted, 31.1% | confirmed | same | primary |
| 2024 | orals | 86 | 86 | confirmed | same; virtual site JSON 2024 | primary |
| 2024 | awards | 5 | 5 outstanding (+11 honorable mentions) | confirmed | same; https://blog.iclr.cc/2024/05/06/iclr-2024-outstanding-paper-awards/ | primary |
| 2025 | N | 11,603 | 11,603 | confirmed | https://media.iclr.cc/Conferences/ICLR2025/ICLR2025_Fact_Sheet.pdf | primary |
| 2025 | rate | 31.9% | 3,704 accepted; 31.9% (fact sheet rounds to 32%) | confirmed | same | primary |
| 2025 | orals | 213 | 213 | confirmed | same; virtual site JSON 2025 | primary |
| 2025 | spotlights (note) | 380, "fact sheet" | fact sheet: 85 spotlight posters; virtual site: 380 "Accept (Spotlight)" | partly confirmed | same; https://iclr.cc/static/virtual/data/iclr-2025-orals-posters.json | primary |
| 2025 | OpenReview entries (note) | 11,672 entries, 11,565 reviewed | Paper Copilot 11,672; dump 11,677 entries, 11,521 with at least one review; OpenReview blocked | partly confirmed | papercopilot.com/statistics/iclr-statistics/ | secondary |
| 2025 | awards | 3 | 3 outstanding (+3 honorable mentions) | confirmed | https://blog.iclr.cc/2025/04/22/announcing-the-outstanding-paper-awards-at-iclr-2025/ | primary |
| 2026 | N (valid) | 19,525 | 19,525 | confirmed | https://blog.iclr.cc/2026/03/31/a-retrospective-on-the-iclr-2026-review-process/ | primary |
| 2026 | desk-rejected / withdrawn / decided | 779 / 5,042 / 13,763 | same values; but 779 + 5,042 + 13,763 = 19,584 ≠ 19,525 | partly confirmed | same | primary |
| 2026 | accepted | 5,355 | 5,355 (retrospective); 5,357 (fact sheet); 5,353 main-track on virtual site | partly confirmed | same; https://media.iclr.cc/Conferences/ICLR2026/ICLR2026_Fact_Sheet.pdf | primary |
| 2026 | rate | 27.4% of valid / 38.9% of decided | retrospective states 27.4%; 5,355/13,763 = 38.9% | confirmed | retrospective | primary |
| 2026 | orals | 224 (U) | 224 (fact sheet); 224 "Accept (Oral)" papers; 223 oral-session events | confirmed | https://media.iclr.cc/Conferences/ICLR2026/ICLR2026_Fact_Sheet.pdf ; https://iclr.cc/static/virtual/data/iclr-2026-orals-posters.json | primary |
| 2026 | awards | 2 | 2 outstanding (+1 honorable mention) | confirmed | https://blog.iclr.cc/2026/04/23/announcing-the-iclr-2026-outstanding-papers/ | primary |
| 2026 | reviews | 76,139 | 76,139 | confirmed | retrospective | primary |

Notes:

- ICLR 2026 has no spotlight tier: the virtual site lists only "Accept (Oral)"
  and "Accept (Poster)".
- The handoff's older secondary values (2017 to 2022) match the
  `lixin4ever/Conference-Acceptance-Rate` list exactly, including its
  errors for 2018 and 2022.

## §10.2 ICLR rows: inter-review agreement and score dispersion

| Claim | Handoff | Found | Outcome | Source | Kind |
|---|---|---|---|---|---|
| berenslab dataset, 2017 to 2024 | r = 0.40 over 244,226 pairs; 3.7 reviews/paper; 24,445 papers; 93% with 3 or 4 reviews | all four values stated in the README and in the paper. My recompute (dumps): r = 0.399 over 244,234 ordered pairs (122,117 distinct), mean 3.66, 92.8% | confirmed | https://github.com/berenslab/iclr-dataset ; https://arxiv.org/abs/2404.08403 | primary |
| Paper Copilot mean paper-average rating | 5.18 (2022); 5.13, SD 1.33 (2023); 5.11 (2024); 5.12, SD 1.25 (2025) | same values on the summary table | confirmed | https://papercopilot.com/statistics/iclr-statistics/ | secondary |
| ICLR 2025 accepted / rejected means | accepted 6.43 (SD 0.68), poster 6.23, spotlight 7.35, oral 7.79; rejected 4.77 (SD 0.92) | same values | confirmed | same | secondary |
| Acceptance threshold in mean score | near 5.11 (2024), 5.12 (2025) | these are the all-paper means. Logistic 50% point on decided papers (dumps): 5.83 (2024), 5.81 (2025) | contradicted | own computation on `papercopilot/paperlists` | secondary |
| Mean score before/after discussion, 2025 | 4.78 → 5.14 | 4.78 → 5.14 | confirmed | https://media.iclr.cc/Conferences/ICLR2025/ICLR2025_Fact_Sheet.pdf | primary |
| Own ICC(1) decomposition | 0.58 / 0.41 / 0.46 / 0.39 (2017 to 2020); within SD 1.03 to 1.19; between SD 1.00 to 1.20 | ICC(1) 0.576 / 0.413 / 0.464 / 0.392. SD ranges hold for 2017 to 2019 only; 2020 (1/3/6/8 scale) has within SD 1.72, between SD 1.38 | partly confirmed | own computation on `papercopilot/paperlists` | secondary |
| Rebuttal effects, 2024 and 2025 | 75 to 81% unchanged; 17 to 23% up; about 1% down; modal 5 → 6; accepted 56 to 58% (improved) vs 8 to 12% (unchanged) | 81% / 75% unchanged; 17% / 23% up; 1% / 1% down; most frequent 5 → 6; accepted 57.6% / 55.7% vs 12.4% / 7.8% | confirmed | Kargaran et al., "Insights from the ICLR Peer Review and Rebuttal Process", https://arxiv.org/abs/2511.15462 | primary |
| Reviewer IDs are per paper | anonymised IDs are per paper | in the 2024 to 2026 dumps, 99.5% or more of 4-character reviewer IDs occur once; reuse rate fits random collisions | confirmed | own check on `papercopilot/paperlists` | secondary |
| No published leniency estimate for ICLR/ICML | absence | not searched in full | not checked | — | none |

Extra observation (not a handoff claim): the same ICC(1) recompute gives 0.36
to 0.42 for 2021 to 2025 and 0.18 for 2026. The 2026 scores are the
pre-rebuttal scores (the PCs reset them after the security incident), and the
scale changed. Treat 2026 separately in any calibration.

## §10.3 ICLR rows: reviews per paper and score scales

| Claim | Handoff | Found | Outcome | Source | Kind |
|---|---|---|---|---|---|
| ICLR 2026 reviews per paper | about 4.1 = 76,139 / 18,746 | 76,139 is primary. 18,746 is not in the source (= 19,525 − 779). Dump: 75,859 reviews on 19,474 reviewed papers = 3.90; per decided paper 3.90 | partly confirmed | retrospective; own check on `papercopilot/paperlists` | primary + secondary |
| ICML 2026 about 3.3 | 3.3 | outside ICLR scope | not checked | — | none |
| ICLR 2017 to 2019 and 2021: integer 1 to 10 | 1 to 10 | all ten values occur in each dump | confirmed | `papercopilot/paperlists` | secondary |
| ICLR 2021 value counts | 14/167/905/2,289/2,685/2,832/1,999/495/112/10 | identical | confirmed | `papercopilot/paperlists` iclr2021.json | secondary |
| ICLR 2020: 1/3/6/8 | {1,3,6,8} | only these values in the dump; Synced describes the four-option form | confirmed | dump; https://syncedreview.com/2019/12/20/iclr-2020-accepted-papers-announced/ | secondary |
| ICLR 2022 and 2023 value counts | 2022: 310/3,223/3,771/3,714/2,089/54; 2023: 465/4,711/5,126/5,326/2,846/101 | identical (field `recommendation`) | confirmed | `papercopilot/paperlists` | secondary |
| ICLR 2024 to 2025 labels | 1 strong reject, 3 reject, 5 marginally below, 6 marginally above, 8 accept, 10 strong accept | same labels in the OpenReview review forms. The reviewer-guide pages contain no scale | confirmed | https://api2.openreview.net/invitations?id=ICLR.cc/2025/Conference/Submission5825/-/Official_Review&expired=true (and Submission4480 for 2024) | primary |
| ICLR 2026 scale | {0,2,4,6,8,10}; "0/2/4 reject, 6/8/10 accept, no borderline point" (U) | {0,2,4,6,8,10} confirmed. 4 and 6 are "marginally below/above the acceptance threshold" (borderline points); there is no neutral midpoint | partly confirmed | https://api2.openreview.net/invitations?id=ICLR.cc/2026/Conference/Submission18691/-/Official_Review&expired=true | primary |

## §10.5 desk rejections and withdrawals

| Claim | Handoff | Found | Outcome | Source | Kind |
|---|---|---|---|---|---|
| ICLR 2024 desk rejects | 53 | 54 (Paper Copilot; 54 in dump); no primary | contradicted | https://papercopilot.com/statistics/iclr-statistics/ | secondary |
| ICLR 2025 desk rejects | 148 | 148 (Paper Copilot; only 70 public in dump); no primary | partly confirmed | same | secondary |
| ICLR 2026 desk rejects | 779 | 779 (Paper Copilot shows 907) | confirmed | https://blog.iclr.cc/2026/03/31/a-retrospective-on-the-iclr-2026-review-process/ | primary |
| ICLR 2024 withdrawals | 22% | 1,655 / 7,304 = 22.66% (22.8% of 7,262); no primary | partly confirmed | https://papercopilot.com/statistics/iclr-statistics/ | secondary |
| ICLR 2025 withdrawals | 25.6% | 2,993 / 11,672 = 25.64%; no primary | confirmed | same | secondary |
| ICLR 2026 withdrawals | 25.8% | 5,042 / 19,525 = 25.8% | confirmed | retrospective | primary |
| ICML 2026 desk rejects for LLM-review violations | 497 | 497 papers (about 2% of submissions), from 398 reciprocal reviewers | confirmed | https://blog.icml.cc/2026/03/18/on-violations-of-llm-review-policies/ | primary |

The handoff cites "ICLR retrospectives" for 2024 and 2025. Only a 2026
retrospective exists on blog.iclr.cc (full post list read through the blog's
WordPress API). The 2024 press release and 2025 fact sheet give no
desk-reject or withdrawal counts.

## §10.7 known gaps: effect of this check

- ICLR 2026 oral count (224) and rating scale: now verified (see above).
- New gaps: no primary source for ICLR 2017 to 2020 submission counts, ICLR
  2018 awards, or ICLR 2024 to 2025 desk-reject and withdrawal counts.

## Sources (all accessed 2026-10-02)

Primary:

- https://blog.iclr.cc/2026/03/31/a-retrospective-on-the-iclr-2026-review-process/
- https://media.iclr.cc/Conferences/ICLR2026/ICLR2026_Fact_Sheet.pdf
- https://iclr.cc/static/virtual/data/iclr-2026-orals-posters.json (and the 2020 to 2025 equivalents; 2020 uses https://iclr.cc/virtual_2020/papers.json)
- https://blog.iclr.cc/2026/04/23/announcing-the-iclr-2026-outstanding-papers/
- https://media.iclr.cc/Conferences/ICLR2025/ICLR2025_Fact_Sheet.pdf
- https://blog.iclr.cc/2025/04/22/announcing-the-outstanding-paper-awards-at-iclr-2025/
- https://media.iclr.cc/Conferences/ICLR2024/ICLR2024_Press_Release.pdf
- https://blog.iclr.cc/2024/05/06/iclr-2024-outstanding-paper-awards/
- https://iclr.cc/media/Press/ICLR_2023_Press_Release.pdf
- https://blog.iclr.cc/2023/03/21/announcing-the-iclr-2023-outstanding-paper-award-recipients/
- https://iclr.cc/media/Press/ICLR_2022_Fact_Sheet.pdf and https://iclr.cc/media/Press/ICLR_2022_Press_Release.pdf
- https://blog.iclr.cc/2022/04/20/announcing-the-iclr-2022-outstanding-paper-award-recipients/
- https://iclr.cc/media/Press/ICLR_2021_Fact_Sheet.pdf
- https://iclr.cc/Conferences/2019/Awards ; https://iclr.cc/Conferences/2019/Schedule?type=Oral ; https://iclr.cc/Conferences/2019/Schedule?type=Poster
- https://iclr.cc/Conferences/2018/Schedule?type=Oral ; https://iclr.cc/Conferences/2018/Schedule?type=Poster
- https://iclr.cc/archive/www/doku.php%3Fid=iclr2017:main.html ; https://iclr.cc/archive/www/doku.php%3Fid=iclr2017:schedule.html ; https://iclr.cc/archive/www/doku.php%3Fid=iclr2017:conference_posters.html
- https://iclr.cc/Conferences/2024/ReviewerGuide ; https://iclr.cc/Conferences/2025/ReviewerGuide ; https://iclr.cc/Conferences/2026/ReviewerGuide (checked: no rating scale)
- OpenReview review forms: https://api2.openreview.net/invitations?id=ICLR.cc/2026/Conference/Submission18691/-/Official_Review&expired=true ; same pattern for ICLR.cc/2025/Conference/Submission5825 and ICLR.cc/2024/Conference/Submission4480
- https://github.com/berenslab/iclr-dataset (README) ; https://arxiv.org/abs/2404.08403
- https://arxiv.org/abs/2511.15462
- https://blog.icml.cc/2026/03/18/on-violations-of-llm-review-policies/

Secondary:

- https://papercopilot.com/statistics/iclr-statistics/
- https://github.com/papercopilot/paperlists (iclr2017.json to iclr2026.json; 2025 and 2026 through media.githubusercontent.com because of Git LFS)
- https://github.com/lixin4ever/Conference-Acceptance-Rate
- https://syncedreview.com/2018/04/30/iclr-2018-kicks-off-in-vancouver/
- https://syncedreview.com/2019/12/20/iclr-2020-accepted-papers-announced/
- https://syncedreview.com/2020/05/04/iclr-2020-virtual-conference-openly-available-online-no-best-paper-awards-this-year/
- https://syncedreview.com/tag/iclr-2019/ (tag page; the 2019 opening-day article gives 1,591 submissions, 24 orals, 476 posters)

## Reproduction

The check scripts and the downloaded files are in the session scratchpad,
`claims-iclr/` (temporary). To redo the dump-based numbers, download the
`paperlists` ICLR files and run the same steps:

- rating values and review counts: count `rating` (or `recommendation` for
  2022 and 2023) values per paper;
- review-pair correlation: all ordered pairs of reviews within a paper,
  2017 to 2024, Pearson r;
- ICC(1): one-way random-effects ANOVA on papers with two or more reviews,
  with the unbalanced group-size correction k0;
- acceptance threshold: logistic regression of accept (yes/no) on the paper
  mean score, decided papers only.
