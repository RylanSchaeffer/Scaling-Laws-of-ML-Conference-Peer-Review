# Verification notes: NeurIPS claims in handoff §10

All sources were accessed on 2026-10-02. "Primary" means an official NeurIPS page, fact sheet, press release, program-chair post, official schedule or virtual-site data, or the paper itself. Paper Copilot, news and similar pages are "secondary".

Scope: every NeurIPS row of §10.4; the NeurIPS rows of §10.3 and §10.5; the NeurIPS 2014 and 2021 rows of §10.1. The Cole/Bornmann row of §10.1 was not checked.

Outcome key: **confirmed**, **partly confirmed**, **contradicted**, **not found** (no primary source located).

Working files (downloads, text extracts, small scripts) are in the session scratchpad, folder `claims-neurips/`. The script `table1_2021.py` there recomputes every 2021 statistic from Table 1.

## 1. Corrections the handoff needs

1. **NeurIPS 2025 orals: use 77, not 87.** The fact sheet gives 87 orals for all 3 tracks. The official virtual-site data gives 77 main-track orals, 7 Datasets and Benchmarks orals and 3 Position-track orals. 77 + 7 + 3 = 87, and the San Diego oral page lists exactly these 87. The §10.7 note that resolved "77" as wrong is itself wrong. The 2023 row uses the same convention: the 2023 fact sheet gives 77 orals, and 67 of them are main track.
2. **NeurIPS 2021 committee correlation is published.** The caption of Figure 1 of arXiv:2306.03262 gives the Pearson correlation of the two committees' mean scores: 0.575 for initial scores, 0.586 for final scores. §10.1 ("V (absence)") and §10.7 must change. This value is a direct calibration target for §7.
3. **NeurIPS 2024 orals: 61 is confirmed** (status U can become V). The virtual-site data gives 61 main-track orals and 11 Datasets and Benchmarks orals. The 2024 oral page lists 72 events, which is 61 + 11.
4. **NeurIPS 2020 submissions: 9,467, not 9,454.** Four primary sources give 9,467: the PC Medium post, the 2020 press release, the 2021 fact sheet and the 2025 PC post.
5. **NeurIPS 2021 acceptance rate: 25.6%, not 25.7%.** The fact sheet and the paper both give 25.6% (2,334 / 9,122).
6. **NeurIPS 2022: the fact sheet does not give 10,411 or 25.6%.** It gives 9,634 full submissions, 2,905 accepted (all tracks) and "20%", which do not agree with each other. The 2022 PC post gives 9,634 full submissions and "over 10,000" received. The figure 10,411 (2,671 accepted, 25.66%) is from Paper Copilot, so it is secondary. The proceedings list 2,671 main-track papers. The fact sheet also gives 184 main-track orals; the handoff row is blank.
7. **NeurIPS 2025 awards: 3 main-track best papers, not 4.** The fact sheet lists 4 best papers, but one of them is from the Datasets and Benchmarks track. It also lists 3 runners-up.
8. **NeurIPS 2014 rejection shares: 50% and 49%, not 50% and 51%.** Of committee 2's 44 accepts, committee 1 rejected 22 (50%). Of committee 1's 43 accepts, committee 2 rejected 21 (49%). The 51% is the share that the other committee accepted.
9. **The 0.544 in the 2014 notebook is not the calibrated correlation.** In the Reviewer Calibration notebook, 0.544 is the correlation of raw mean quality scores. The correlation of calibrated mean scores is 0.546, which rounds to the published 0.55.
10. **§8.1 must pair each set size with the correct rejection count.** See §2 below. For the Spotlight or Better set (Orals and Spotlights; 29 and 25 papers), the other committee rejected 13 of 29 and 13 of 25. The figures 13 of 25 and 13 of 23 are for the Spotlight tier alone (Orals excluded). The two "13 of 25" figures come from different committees.
11. **NeurIPS 2025 space constraint.** The PC post says space played a negligible role for the main track. A news report (36kr) gives the figure of about 400 papers rejected after AC acceptance. The §10.5 wording ("volume forced SAC-level ranking") is not in the PC post.
12. **NeurIPS 2026 has no primary source yet.** The virtual site is not public (HTTP 403). There is no fact sheet and no PC post. The official data export `neurips-2026-orals-posters.json` has 9,236 records but only 6,285 unique ids, so it cannot give counts. The 2026 row must stay unverified.

## 2. NeurIPS 2021 consistency experiment: facts for the §8.1 test

Source: Beygelzimer, Dauphin, Liang and Wortman Vaughan, arXiv:2306.03262 v1 (the only version), https://arxiv.org/pdf/2306.03262 (primary). Also the NeurIPS blog post of 8 Dec 2021, https://blog.neurips.cc/2021/12/08/the-neurips-2021-consistency-experiment/ (primary). The blog shows the same table as an image.

### How the experiment worked

- At assignment, 10% of papers were chosen uniformly at random and duplicated. Each duplicated paper got two ACs and twice the usual number of reviewers. These were split at random between the two copies. The two ACs were under two different SACs.
- The committees did not know about the experiment. Authors were told just before initial reviews and responded to each copy separately.
- 882 duplicated papers were still under review when initial reviews were released (out of 8,765 papers under review and 9,122 submitted). The 882 include 118 papers that the authors withdrew after initial reviews. These 118 appear as "withdrawn" for both copies, so they agree by construction.
- A duplicated paper was accepted if either copy was recommended for acceptance and no fatal flaw was found. This added 92 accepts and raised the conference rate from 24.6% to 25.6%.

### How oral and spotlight recommendations were made

- The AC meta-review form had a mandatory Recommendation field with four options: Accept (Oral), Accept (Spotlight), Accept (Poster), Reject (paper, Appendix B).
- A mandatory qualifier went with it: certain; can be bumped up; can be bumped down; not certain (to discuss with the SAC).
- Section 2 states that oral and spotlight decisions were made jointly by SACs and the program chairs.
- Section 4.2 states that ACs, SACs and PCs made these recommendations, and that they used factors beyond raw reviewer scores, for example interest to a broad audience.
- Section 5.1 states that during calibration ACs were often asked to edit their meta-reviews between poster and reject, or between spotlight and poster. So Table 1 shows recommendations after SAC/PC calibration, not raw AC proposals.
- Inference (not stated in the paper): each copy had its own AC and SAC, but the same four PCs worked on decisions for both copies. So the oral and spotlight decisions have a component that both committees may share.

### Table 1 (rows: original committee; columns: copy committee)

| original \ copy | Oral | Spotlight | Poster | Reject | Withdrawn | row total |
|---|---|---|---|---|---|---|
| Oral | 0 | 0 | 4 | 0 | 0 | 4 |
| Spotlight | 0 | 3 | 9 | 13 | 0 | 25 |
| Poster | 2 | 7 | 74 | 94 | 0 | 177 |
| Reject | 0 | 13 | 83 | 462 | 0 | 558 |
| Withdrawn | 0 | 0 | 0 | 0 | 118 | 118 |
| column total | 2 | 23 | 170 | 569 | 118 | 882 |

The orientation was checked from the rendered PDF page: the row sums of accepts are 206 and the column sums are 195, as the text states.

### Figures derived from Table 1 (checked by script)

- Accepts: 206 (original), 195 (copy); both accept 99; inconsistent 203 of 882 = 23.0%. Mean acceptance rate 22.7%; random baseline 2p(1-p) = 35.1%. All match the paper.
- Share of one committee's accepts rejected by the other: 107/206 = 51.9% and 96/195 = 49.2%; pooled 50.6%. These match the paper.
- Share of rejects (withdrawn counted as rejects) accepted by the other: 14.9% pooled. This matches the paper.
- **Spotlight or Better = Orals and Spotlights** (the experiment had no Best Papers tier). Sizes 29 (original) and 25 (copy); overlap 3. All 3 are Spotlights in both copies; no paper was an Oral in both.
  - The original's 29 in the copy: 3 Spotlight or Better, 13 poster, 13 reject. P(reject | Spotlight or Better) = 13/29 = 0.448.
  - The copy's 25 in the original: 3 Spotlight or Better, 9 poster, 13 reject. P(reject | Spotlight or Better) = 13/25 = 0.520.
- **The Spotlight tier alone.** Original 25: 3 Spotlight, 9 poster, 13 reject in the copy, so 13/25 = 0.520. Copy 23: 3 Spotlight, 7 poster, 13 reject in the original, so 13/23 = 0.565. The blog states "13/25 and 13/23" for spotlights. The paper gives the table only.
- **The Oral tier alone.** Original 4 and copy 2. All 6 were posters in the other copy, so the other committee rejected no Oral.
- **If only Spotlight or Better (Orals and Spotlights) were accepted.** The rate is 27/882 = 3.1%. Of each committee's Spotlight or Better set, the other's Spotlight or Better set excludes 26/29 and 22/25; the mean is 88.8%, which matches the paper. Disagreement is 48/882 = 5.4%. The paper text gives 5.8%, but its "8% relative improvement" over the 5.9% random baseline fits 5.4%. The blog gives a 3% improvement. So the paper and the blog disagree slightly here.

### Other numbers in the paper

- Committee mean-score Pearson correlation: 0.575 (initial), 0.586 (final) (Figure 1).
- Figure 2 shows disagreement as a function of acceptance rate if the top x% by mean initial or final score were accepted. Figure 3 shows the same for the share of accepts rejected by the other committee. Neither gives a table by score band.
- Bump-down variant: acceptance 16.0%, disagreement 20.3%, 63.2% of accepts rejected by the other. Bump-up variant: acceptance 34.4%, disagreement 29.4%, 42.7%. Treating "can be bumped" pairs as consistent: inconsistency 16.0%.
- 24 papers had each committee unanimous internally, with the two committees disagreeing.
- Duplicated papers had a lower acceptance rate (22.7%) than other papers under review (2,036/7,883 = 25.8%). The paper names author effort as a likely cause: in 50 pairs the authors commented only on the copy with the higher score.
- Ethics flags: 23 and 22 papers, overlap 3.
- The paper and the blog both say the 2014 experiment "included only 116 papers". This is a typo for 166.
- Conference totals (paper §2): 9,122 submitted, 2,334 accepted (25.6%), 55 orals, 260 spotlights, 2,019 posters. The program committee had more than 8,000 reviewers, 708 ACs and 95 SACs. At initial review release, 99.7% of submissions had at least three reviews. Overall score scale in 2021: 1 to 10 with percentile anchors (10 = top 5% of accepted papers, 9 = top 15%, 8 = top 50%).

## 3. §10.1 rows (NeurIPS 2014 and 2021)

| # | Claim (handoff) | Found | Outcome | Source (primary unless marked) |
|---|---|---|---|---|
| 1.1 | 2014: 166 papers (about 10%) reviewed twice | 170 chosen (about 10% of 1,678); 4 withdrawn or rejected without review; 166 completed | confirmed | https://arxiv.org/pdf/2109.09774 (§2, Table 1) |
| 1.2 | 2014 2×2 table 22 / 22 / 21 / 101 | Same table (rows committee 2, columns committee 1) | confirmed | https://arxiv.org/pdf/2109.09774 |
| 1.3 | 2014: 43/166 = 25.9% inconsistent | 25.9% (blog and Appendix C; §2.2 text has the typo "25.0%") | confirmed | https://inverseprobability.com/2014/12/16/the-nips-experiment ; arXiv:2109.09774 |
| 1.4 | 2014: committees accepted 44/166 and 43/166 | Committee 1: 43, committee 2: 44. On the 170 denominator: 25.3% and 25.8% | confirmed | arXiv:2109.09774 Appendix E |
| 1.5 | 2014: of one committee's accepts, 50% and 51% rejected by the other | 22/44 = 50% and 21/43 = 49% rejected; mean 49.5% | partly confirmed | arXiv:2109.09774 §2.2, Appendix C |
| 1.6 | "57%" comes from using 22.5% instead of the committees' own rate | Price applied a 22.5% rate (the target rate he says the committees were "tasked with") to get 21/37 or 22/38, about 57%. Cortes & Lawrence say the debate used the main conference rate as a proxy. The realised 2014 rate was 24.7% | confirmed (22.5% is a target rate, not the realised rate) | http://blog.mrtz.org/2014/12/15/the-nips-experiment.html (E. Price guest post; origin of the claim); arXiv:2109.09774 Appendix C.1 |
| 1.7 | 2014: correlation 0.55 ± 0.065 (0.544 in notebook) | Paper: 0.55, SE 0.065. Notebook: 0.5440 for raw mean quality, 0.5456 for calibrated mean quality | partly confirmed (0.544 is the raw-score value) | arXiv:2109.09774 §2.2, Fig. 2; https://raw.githubusercontent.com/lawrennd/neurips2014/master/notebooks/Reviewer%20Calibration.ipynb |
| 1.8 | 2014 variance components 1.28 / 0.24 / 1.27; offset share 8.6%; about half subjective after offsets | Table 2: 1.28, 0.24, 1.27. 0.24/2.79 = 8.6%; 1.27/2.55 = 49.8% | confirmed | arXiv:2109.09774 Table 2; https://inverseprobability.com/slides/2021-06-16-the-neurips-experiment.slides.html |
| 1.9 | 2014: no significant score-citation correlation among accepted papers; 0.22 ± 0.038 among rejected | Accepted or Better (n = 414): 0.051 ± 0.049. Rejected: 0.22 ± 0.038 | confirmed | arXiv:2109.09774 Figs. 4 and 8 |
| 1.10 | 2021: 882 papers, 203 (23.0%) inconsistent, mean rate 22.7%, random 35.1% | Same | confirmed | https://arxiv.org/pdf/2306.03262 §4.1; NeurIPS blog 8 Dec 2021 |
| 1.11 | 2021: Spotlights rejected by the other committee 13 of 25 and 13 of 23; Spotlight or Better (Orals and Spotlights) 29 and 25, agree on 3 | Same. 13/25 and 13/23 are the Spotlight tier alone; for Spotlight or Better the counts are 13/29 and 13/25 | confirmed | arXiv:2306.03262 Table 1 and §4.1; https://blog.neurips.cc/2021/12/08/the-neurips-2021-consistency-experiment/ |
| 1.12 | 2021 reported no committee-score correlation and no disagreement by score band | Correlation reported: 0.575 initial, 0.586 final (Fig. 1). Disagreement versus score-threshold acceptance rate is plotted (Fig. 2), not tabulated by band | contradicted (correlation) / partly (score band) | arXiv:2306.03262 Fig. 1, Fig. 2 |
| 1.13 | 2021 main track: 9,122 submissions, 25.7% accepted | 9,122; 2,334 accepted; 25.6% | partly confirmed (rate is 25.6%) | https://neurips.cc/media/Press/NeurIPS_2021-Fact_Sheet.pdf ; arXiv:2306.03262 §2 |

## 4. §10.3 rows (NeurIPS)

| # | Claim (handoff) | Found | Outcome | Source |
|---|---|---|---|---|
| 3.1 | NeurIPS 2024 and 2025: at least three quality reviews per paper before the author response | Both SAC guideline pages say every paper must have at least 3 quality reviews before the author response | confirmed | https://neurips.cc/Conferences/2025/SAC-Guidelines ; https://neurips.cc/Conferences/2024/SAC-Guidelines |
| 3.2 | ACs aim for four qualified reviewers; four always assigned is unsubstantiated | 2024 SAC guidelines tell SACs to check that each AC has four qualified reviewers per paper. No such sentence was found in the 2024 AC page or the 2025 AC and SAC pages. The 2025 PC post does not give a count | partly confirmed (2024 only; it is in the SAC page, not the AC page) | https://neurips.cc/Conferences/2024/SAC-Guidelines ; https://neurips.cc/Conferences/2024/AC-Guidelines ; https://neurips.cc/Conferences/2025/AC-Guidelines |
| 3.3 | Overall score 1 to 10 through 2024 with labels 10 award quality ... 1 very strong reject; 1 to 4 sub-scores; 1 to 5 confidence | 2024 page: exactly these ten labels; soundness, presentation and contribution on 1 to 4; confidence 1 to 5. The same labels are on the 2022 and 2023 pages. 2021 and 2014 also used 1 to 10, but with different labels (2021: "Top 5% of accepted papers" for 10, and so on) | partly confirmed (labels hold for 2022 to 2024 only) | https://neurips.cc/Conferences/2024/ReviewerGuidelines ; https://neurips.cc/Conferences/2022/ReviewerGuidelines ; arXiv:2306.03262 App. B |
| 3.4 | From 2025, six-point 1 to 6 scale (6 strong accept "top 2 to 3 percent" ... 1 strong reject) | 2025 page: 6 Strong Accept, 5 Accept, 4 Borderline accept, 3 Borderline reject, 2 Reject, 1 Strong Reject. No percentile anchor appears on the page. Sub-scores (quality, clarity, significance, originality) are 1 to 4; confidence is 1 to 5 | partly confirmed (no "top 2 to 3 percent" anchor found) | https://neurips.cc/Conferences/2025/ReviewerGuidelines |

## 5. §10.4 rows (NeurIPS main track)

Accepted counts in brackets come from the source named. "Virtual-site data" means `https://neurips.cc/static/virtual/data/neurips-{year}-orals-posters.json`. Counts from it are unique main-track papers by decision, from records whose OpenReview group is `NeurIPS.cc/{year}/Conference`. "Schedule" means `https://neurips.cc/Conferences/{year}/Schedule?type=Oral` (or Spotlight, Poster).

| Year | Field | Handoff | Found | Outcome | Source |
|---|---|---|---|---|---|
| 2014 | N | 1,678 | 1,678 (414 accepted) | confirmed | https://media.nips.cc/Conferences/2014/NIPS-2014-Conference-Book.pdf ; arXiv:2109.09774 §7 |
| 2014 | rate | 24.7% | 414/1,678 = 24.7% (proceedings list 411) | confirmed | same; https://proceedings.neurips.cc/paper_files/paper/2014 |
| 2014 | orals | 20 (62 spotlights) | 20 orals, 62 spotlights, 331 posters (the slide breakdown adds to 413, not 414) | confirmed | https://inverseprobability.com/slides/2021-06-16-the-neurips-experiment.slides.html ; schedule 2014 |
| 2014 | awards | blank | 2 Outstanding Paper Awards | (new value) | https://neurips.cc/Conferences/2014/Awards |
| 2015 | N, rate | 1,838, 21.9% | 1,838; 403 accepted; 21.9% | confirmed | https://media.nips.cc/Conferences/2015/NIPS-2015-Conference-Book.pdf |
| 2015 | orals, awards | blank | 15 orals (67 spotlights); 2 best papers | (new values) | schedule 2015; https://neurips.cc/Conferences/2015/Awards |
| 2016 | N | 2,403 | 2,403 "considered by the program committee" (book); 2,425 submitted (Shah et al.) | confirmed (2,403 is the reviewed count) | https://media.nips.cc/Conferences/2016/NIPS-2016-Conference-Book.pdf ; https://arxiv.org/pdf/1708.09794 |
| 2016 | rate | 23.6% | Book: 569 accepted; it says 24%. Shah et al.: 568 accepted. 568/2,403 = 23.6%; 569/2,403 = 23.7% | confirmed (within rounding) | same |
| 2016 | orals | blank | 45 | (new value) | arXiv:1708.09794 §5; schedule 2016 |
| 2016 | awards | 1 | 1 best paper plus 1 best student paper | partly confirmed (2 if the student award counts) | https://neurips.cc/Conferences/2016/Awards |
| 2017 | N | 3,240 | 3,240 submitted and sent for review | confirmed | https://media.nips.cc/Conferences/NIPS2017/Eventmedia/opening_remarks.pdf |
| 2017 | rate | 20.9% | 679 accepted; slide says 21%; 679/3,240 = 20.96% | partly confirmed (rounds to 21.0%) | same |
| 2017 | orals | 40 | 40 orals, 112 spotlights, 527 posters | confirmed | same; schedule 2017 (41 entries incl. Test of Time talk) |
| 2017 | awards | 3 | 3 best papers | confirmed | same; https://neurips.cc/Conferences/2017/Awards |
| 2018 | N | 4,856 | 4,856 only in secondary sources; no primary page found | not found (primary) | secondary: https://papercopilot.com/statistics/neurips-statistics/ ; https://signalprocessingsociety.org/get-involved/speech-and-language-processing/newsletter/neurips-2018-conference-review |
| 2018 | rate | 20.8% | Proceedings and schedule list 1,009 papers; 1,009/4,856 = 20.8% | confirmed (counts primary, N secondary) | https://proceedings.neurips.cc/paper_files/paper/2018 ; schedule 2018 |
| 2018 | orals | 30 | 30 orals, 167 spotlights | confirmed | schedule 2018 |
| 2018 | awards | 4 | 4 best papers | confirmed | https://neurips.cc/Conferences/2018/Awards |
| 2019 | N | 6,743 | 6,743 after filtering; 6,614 at notification | confirmed | https://web.archive.org/web/20200624120539/https://medium.com/@NeurIPSConf/what-we-learned-from-neurips-2019-data-111ab996462c |
| 2019 | rate | 21.2% | PCs give 21.6% (1,428 / 6,614). 1,428 / 6,743 = 21.2% | partly confirmed (denominator differs) | same |
| 2019 | orals | 36 | 36 orals, 164 spotlights | confirmed | schedule 2019; https://neurips.cc/virtual/2019/events/oral |
| 2019 | awards | 2 | 1 Outstanding Paper plus 1 Outstanding New Directions Paper (plus honorable mentions) | confirmed | https://neurips.cc/Conferences/2019/Awards |
| 2020 | N | 9,454 | 9,467 full submissions (12,115 abstracts; 1,097 summarily rejected) | contradicted | https://web.archive.org/web/20260101045110/https://neuripsconf.medium.com/what-we-learned-from-neurips-2020-reviewing-process-e24549eea38f ; https://neurips.cc/media/Press/2020_NeurIPS_Press_Release.pdf ; 2021 fact sheet; 2025 PC post |
| 2020 | rate | 20.1% | 1,900 / 9,467 = 20.1% (press release and proceedings: 1,898) | confirmed | same |
| 2020 | orals | 105 | 105 orals, 280 spotlights | confirmed | 2020 PC Medium post (archived) |
| 2020 | awards | 3 | 3 best papers | confirmed | https://blog.neurips.cc/2020/12/07/announcing-the-neurips-2020-award-recipients/ ; 2020 press release |
| 2021 | N | 9,122 | 9,122 (11,292 abstracts) | confirmed | https://neurips.cc/media/Press/NeurIPS_2021-Fact_Sheet.pdf |
| 2021 | rate | 25.7% | 25.6% (2,334 accepted) | contradicted (minor) | same; arXiv:2306.03262 |
| 2021 | orals | 55 | 55 orals, 260 spotlights, 2,019 posters | confirmed | same; virtual-site data 2021 |
| 2021 | awards | 6 | 6 Outstanding Paper Awards (the fact sheet lists only 5) | confirmed | https://blog.neurips.cc/2021/11/30/announcing-the-neurips-2021-award-recipients/ |
| 2022 | N | 10,411 | Fact sheet and PC post: 9,634 full submissions; the PC post says "over 10,000" received. 10,411 is in Paper Copilot only | contradicted as a fact-sheet value (10,411 is secondary) | https://media.neurips.cc/Conferences/NeurIPS2022/NeurIPS_2022_Fact_Sheet.pdf ; https://blog.neurips.cc/2022/08/01/updates-from-the-program-chairs/ ; secondary: Paper Copilot |
| 2022 | rate | 25.6% | Fact sheet: 2,905 accepted, "20%" (these do not agree). Proceedings: 2,671 main-track papers. 2,671/10,411 = 25.7%; 2,671/9,634 = 27.7% | contradicted as a fact-sheet value | same; https://proceedings.neurips.cc/paper_files/paper/2022 |
| 2022 | orals | blank | Fact sheet: 184 main-track orals (16 D&B). The virtual site lists no oral events | (new value) | 2022 fact sheet |
| 2022 | awards | 13 | 13 Outstanding Paper Awards (main) | confirmed | 2022 fact sheet |
| 2023 | N, rate | 12,343, 26.1% | 12,343 main; 3,218 accepted; 26.1% | confirmed | https://media.neurips.cc/Conferences/NeurIPS2023/NeurIPS2023-Fact_Sheet.pdf |
| 2023 | orals | 67 (378 spotlights) | Fact sheet: 77 orals for all tracks. Virtual-site data: 67 main, 10 D&B; 378 main-track spotlights | confirmed | same; virtual-site data 2023; https://neurips.cc/virtual/2023/events/oral |
| 2023 | awards | 2 | 2 Outstanding Main Track Papers (plus 2 runners-up) | confirmed | 2023 fact sheet |
| 2024 | N, rate | 15,671, 25.8% | 15,671 main; 4,037 accepted; 25.8% | confirmed | https://media.neurips.cc/Conferences/NeurIPS2024/NeurIPS2024-Fact_Sheet.pdf |
| 2024 | orals | 61 (U) | 61 main-track orals, 326 spotlights, 3,648 posters (4,035 papers). Oral page: 72 events = 61 main + 11 D&B. The fact sheet gives only "69 Oral Sessions". Paper Copilot (secondary) also gives 61 | confirmed | virtual-site data 2024; https://neurips.cc/virtual/2024/events/oral |
| 2024 | awards | 2 | 2 best papers for the main track (plus 2 runners-up) | confirmed | 2024 fact sheet |
| 2025 | N, rate | 21,575, 24.5% (5,290) | 21,575 valid main-track submissions; 5,290 accepted; 24.52% | confirmed | https://blog.neurips.cc/2025/09/30/reflections-on-the-2025-review-process-from-the-program-committee-chairs/ ; https://media.neurips.cc/Conferences/NeurIPS2025/press/NeurIPS2025-Fact_Sheet.pdf |
| 2025 | orals | 87 | Fact sheet: 87 orals for 3 tracks. Virtual-site data: 77 main, 7 D&B, 9 Position (3 of them in San Diego). San Diego oral page: 87 = 77 + 7 + 3. Main track: 687 spotlights, 4,523 posters (5,287 papers) | contradicted (main-track value is 77) | same; virtual-site data 2025; https://neurips.cc/virtual/2025/events/oral |
| 2025 | awards | 4 | 4 best papers, one of them D&B, so 3 main track (plus 3 runners-up) | contradicted (3 main track) | 2025 fact sheet |
| 2026 | N, rate, orals | 30,709, 25.7%, 112 (7,496 + 292 + 112 = 7,900) | No fact sheet, PC post or public virtual site. The official JSON export is duplicated (9,236 records, 6,285 unique ids; main track 8,000 records, 5,369 unique OpenReview forums), so it cannot verify counts. The record proportions are close to the reported split: 7,502 poster, 302 spotlight and 113 oral-poster records | not found | https://neurips.cc/static/virtual/data/neurips-2026-orals-posters.json ; https://blog.neurips.cc/2026/ |

## 6. §10.5 rows (NeurIPS)

| # | Claim (handoff) | Found | Outcome | Source |
|---|---|---|---|---|
| 5.1 | NeurIPS does not decide by mean score: AC meta-review and recommendation, SAC calibration across ACs, PC finalisation; orals and spotlights decided jointly by SACs and PCs | The 2025 AC and SAC pages describe this sequence: AC meta-review and recommendation, SAC calibration across ACs, then meetings with PCs to finalise. For orals and spotlights, the 2021 paper states joint SAC and PC decisions. The 2024 and 2025 guideline pages do not mention oral or spotlight selection | partly confirmed (oral/spotlight process sourced for 2021 only) | https://neurips.cc/Conferences/2025/SAC-Guidelines ; https://neurips.cc/Conferences/2025/AC-Guidelines ; arXiv:2306.03262 §2 |
| 5.2 | 2025: ACs overrode reviewers in both directions; volume forced SAC-level ranking that rejected some AC-recommended papers (about 400) | PC post: ACs often moved papers to accept against reviewers, and AC/SAC consensus led to rejects despite high ratings. The post also says space played a negligible role for the main track. The 400 figure is from news reports quoting an SAC | override confirmed; space-driven ranking contradicted by the PC post; 400 secondary only | https://blog.neurips.cc/2025/09/30/reflections-on-the-2025-review-process-from-the-program-committee-chairs/ ; secondary: https://www.36kr.com/p/3447809868404355 |
| 5.3 | 2025 committee: 20,518 reviewers, 1,663 ACs, 199 SACs (about 13 papers per AC) | Same numbers in the PC post (main track). 21,575 / 1,663 = 13.0. The fact sheet gives 21,921 reviewers, 1,985 ACs and 240 SACs for all tracks | confirmed | PC post above; 2025 fact sheet |
| 5.4 | Oral share fell from about 1.2% (2014) to about 0.4% (2025 to 2026) | 2014: 20/1,678 = 1.19%. 2025 main track: 77/21,575 = 0.36% (87 gives 0.40%). 2026: 112/30,709 = 0.36% (inputs unverified) | partly confirmed (about 0.36% with the main-track count) | derived from §5 |

## 7. Source list

Primary:
- https://arxiv.org/pdf/2306.03262 (v1, 5 Jun 2023)
- https://blog.neurips.cc/2021/12/08/the-neurips-2021-consistency-experiment/
- https://arxiv.org/pdf/2109.09774 (v1, 22 Sep 2021)
- https://inverseprobability.com/2014/12/16/the-nips-experiment
- https://inverseprobability.com/slides/2021-06-16-the-neurips-experiment.slides.html
- https://github.com/lawrennd/neurips2014 (notebooks "Reviewer Calibration" and "The NIPS Experiment")
- http://blog.mrtz.org/2014/12/15/the-nips-experiment.html (Eric Price; origin of the 57% claim)
- https://media.nips.cc/Conferences/2014/NIPS-2014-Conference-Book.pdf, .../2015/NIPS-2015-Conference-Book.pdf, .../2016/NIPS-2016-Conference-Book.pdf
- https://arxiv.org/pdf/1708.09794 (Shah et al., NIPS 2016 review process)
- https://media.nips.cc/Conferences/NIPS2017/Eventmedia/opening_remarks.pdf
- https://neurips.cc/Conferences/{2014..2019}/Awards and https://neurips.cc/Conferences/{2014..2019}/Schedule?type=Oral|Spotlight|Poster
- https://proceedings.neurips.cc/paper_files/paper/{year}
- Archived NeurIPS Medium posts for 2019 and 2020 (web.archive.org URLs above)
- https://neurips.cc/media/Press/2020_NeurIPS_Press_Release.pdf
- https://blog.neurips.cc/2020/12/07/announcing-the-neurips-2020-award-recipients/
- https://neurips.cc/media/Press/NeurIPS_2021-Fact_Sheet.pdf
- https://blog.neurips.cc/2021/11/30/announcing-the-neurips-2021-award-recipients/
- https://media.neurips.cc/Conferences/NeurIPS2022/NeurIPS_2022_Fact_Sheet.pdf
- https://blog.neurips.cc/2022/08/01/updates-from-the-program-chairs/
- https://media.neurips.cc/Conferences/NeurIPS2023/NeurIPS2023-Fact_Sheet.pdf
- https://media.neurips.cc/Conferences/NeurIPS2024/NeurIPS2024-Fact_Sheet.pdf
- https://media.neurips.cc/Conferences/NeurIPS2025/press/NeurIPS2025-Fact_Sheet.pdf
- https://blog.neurips.cc/2025/09/30/reflections-on-the-2025-review-process-from-the-program-committee-chairs/
- https://neurips.cc/static/virtual/data/neurips-{2021..2026}-orals-posters.json and https://neurips.cc/virtual/{year}/events/oral
- https://neurips.cc/Conferences/{2022,2023,2024,2025}/ReviewerGuidelines, https://neurips.cc/Conferences/{2024,2025}/AC-Guidelines, https://neurips.cc/Conferences/{2024,2025}/SAC-Guidelines

Secondary:
- https://papercopilot.com/statistics/neurips-statistics/
- https://signalprocessingsociety.org/get-involved/speech-and-language-processing/newsletter/neurips-2018-conference-review
- https://www.36kr.com/p/3447809868404355

Not reachable: Medium (HTTP 403; archived copies used), the OpenReview API (it requires a bot challenge, which was not attempted), and the NeurIPS 2026 virtual site (HTTP 403).
