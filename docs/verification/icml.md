# Verification of the ICML claims in handoff §10.3, §10.4 and §10.5

All sources were accessed on 2026-10-02. "Primary" means an official ICML page,
fact sheet, program-chair letter or blog post, the official ICML virtual-site
data, the PMLR proceedings, or a paper written with ICML organiser data.
Paper Copilot, csconfstats and news sites are secondary. Local copies of the
downloaded files and the counting scripts are in the session scratchpad
folder `claims-icml/` (not in the repository).

## Summary of the changes the handoff needs

1. ICML 2026 reviews per paper is about 3.8, not 3.3 (90,822 main-track reviews, 23,918 main-track papers).
2. ICML 2023 orals: the official virtual site lists 155, not 158.
3. ICML 2025 orals: 120 includes 12 position-track orals. The main-track count is 108.
4. ICML 2024 orals and awards include position papers: 15 of the 144 orals and 2 of the 10 best papers. The main-track counts are 129 orals and 8 awards.
5. ICML 2024 and 2025 fact sheets do not give the submission count. The 9,473 and 12,107 figures come only from secondary sources.
6. The ICML 2026 fact sheet gives 24,661 submissions and 6,552 accepted. These numbers include the position track (743 submissions). The main-track numbers 23,918 and 6,352 are correct.
7. Two §10.3 source links point to the wrong page (see the notes for those rows).
8. Submission counts for 2014 and 2019 to 2022 have only secondary sources. The accepted counts for those years agree with PMLR and the virtual site.

## Method

- Accepted counts: I counted the papers on each PMLR volume page (v32, v37, v48, v70, v80, v97, v119, v139, v162, v202, v235, v267).
- Orals and tracks: I counted the records in the official virtual-site files `https://icml.cc/static/virtual/data/icml-<year>-orals-posters.json` for 2021 to 2026. I split them by event type, decision and source group (main `Conference` group or `Position_Paper_Track` group). For 2024 the position papers sit in the main group, so I used the "Position:" title prefix.
- Awards: I counted the award lists on the official award pages (icml.cc and blog.icml.cc).
- PDFs were read with pymupdf.

## §10.4 ICML rows (submissions, acceptance rate, orals, awards)

| Year | Item | Handoff | Found | Outcome | Source | Primary |
|---|---|---|---|---|---|---|
| 2014 | Submissions | 1,238 | Not found in a primary source; csconfstats gives 1,238 | not found (primary) | https://csconfstats.xoveexu.com/conferences/icml/ | secondary |
| 2014 | Accepted / rate | 25.0% | 310 papers in PMLR v32 (both cycles); 310/1,238 = 25.0% | partly confirmed (count primary, N secondary) | https://proceedings.mlr.press/v32/ | primary |
| 2015 | Submissions, rate | 1,037; 26.0% | PC letter: 270 papers from 1,037 submissions (26.0%) | confirmed | https://icml.cc/2015/booklet-icml2015.online.pdf (p. 5) | primary |
| 2016 | Submissions, rate | 1,320; 24.4% | PC letter: 322 papers from 1,320 submissions (24.4%) | confirmed | https://web.archive.org/web/20160615062007id_/http://icml.cc:80/2016/wp-content/uploads/ICML-Book-Web-Version.pdf (p. 2; the live icml.cc copy is 404) | primary (archived) |
| 2017 | Submissions, rate | 1,676; 25.9% | PC letter: 1,676 submissions, 434 accepted (25.9%) | confirmed | https://media.nips.cc/Conferences/ICML2017/ICML-2017-Conference-Book.pdf (p. 7) | primary |
| 2018 | Submissions, rate | 2,473; 25.1% | PC letter: 2,473 submissions, 621 accepted (25.1%) | confirmed | https://media.nips.cc/Conferences/ICML2018/ICML-2018-Conference-Book.pdf (p. 2) | primary |
| 2019 | Submissions | 3,424 | Only secondary sources (Paper Copilot, csconfstats) | not found (primary) | https://papercopilot.com/statistics/icml-statistics/ | secondary |
| 2019 | Rate | 22.6% | 773 papers in PMLR v97 and 773 entries on the accepted-papers page; 773/3,424 = 22.6% | partly confirmed | https://proceedings.mlr.press/v97/ ; https://icml.cc/Conferences/2019/AcceptedPapersInitial | primary (count) |
| 2020 | Submissions | 4,990 | Only secondary sources | not found (primary) | https://papercopilot.com/statistics/icml-statistics/ | secondary |
| 2020 | Rate | 21.8% | 1,084 papers in PMLR v119 (21.7%); 1,088 announced per secondary sources (21.8%) | partly confirmed | https://proceedings.mlr.press/v119/ | primary (count) |
| 2020 | Awards | 2 | 2 Outstanding Papers (plus 2 honourable mentions) | confirmed | https://icml.cc/Conferences/2020/Awards | primary |
| 2021 | Submissions | 5,513 | Only secondary sources | not found (primary) | https://papercopilot.com/statistics/icml-statistics/ | secondary |
| 2021 | Rate | 21.5% | 1,183 papers (PMLR v139, virtual site); 1,184 entries on the accepted page; 21.5% | partly confirmed | https://proceedings.mlr.press/v139/ ; https://icml.cc/Conferences/2021/AcceptedPapersInitial | primary (count) |
| 2021 | Orals | 166 | 166 oral (long-talk) records | confirmed | https://icml.cc/static/virtual/data/icml-2021-orals-posters.json | primary |
| 2021 | Awards | 1 | 1 Outstanding Paper (plus 4 honourable mentions) | confirmed | https://icml.cc/virtual/2021/awards_detail | primary |
| 2022 | Submissions | 5,630 | Only secondary sources | not found (primary) | https://papercopilot.com/statistics/icml-statistics/ | secondary |
| 2022 | Rate | 21.9% | 1,233 papers (PMLR v162, virtual site); 1,233/5,630 = 21.9% | partly confirmed | https://proceedings.mlr.press/v162/ | primary (count) |
| 2022 | Orals | 118 | 118 "Accept for Long Presentation" records | confirmed | https://icml.cc/static/virtual/data/icml-2022-orals-posters.json | primary |
| 2022 | Awards | 10 | 10 Outstanding Papers (plus 5 runners-up) | confirmed | https://icml.cc/virtual/2022/awards_detail | primary |
| 2023 | Submissions, rate | 6,538; 27.9% | 6,538 submissions (paper with ICML 2023 data, co-author K. Cho was a PC); 1,828 papers in PMLR v202 and the virtual site; 1,828/6,538 = 27.96% | confirmed (27.9% vs 28.0% is rounding of 1,827 vs 1,828) | https://arxiv.org/pdf/2408.13430 (p. 2, 5); https://proceedings.mlr.press/v202/ | primary |
| 2023 | Orals | 158 | 155 oral records; all 6 award papers are among them; Paper Copilot also gives 155 | contradicted | https://icml.cc/static/virtual/data/icml-2023-orals-posters.json | primary |
| 2023 | Awards | 6 | "six papers" received the Outstanding Paper Award | confirmed | https://icml.cc/Conferences/2023/Awards | primary |
| 2024 | Submissions | 9,473 | The fact sheet does not state submissions. 9,473 appears only in secondary sources. Paper Copilot gives 9,653 | partly confirmed (secondary only) | https://media.icml.cc/Conferences/ICML2024/ICML2024_Fact_Sheet.pdf | primary (fact sheet), N secondary |
| 2024 | Rate | 27.5% | Fact sheet: 27.5%, "over 2600" main-track papers; PMLR v235 has 2,610 papers, of which 76 are position papers | confirmed (rate); the count includes position papers | same; https://proceedings.mlr.press/v235/ | primary |
| 2024 | Orals | 144 | Fact sheet: 144 orals. The virtual site has 144 orals, of which 15 are position papers (main track 129) | partly confirmed | fact sheet; https://icml.cc/static/virtual/data/icml-2024-orals-posters.json | primary |
| 2024 | Awards | 10 | 10 Best Papers, of which 2 are position papers (main track 8) | partly confirmed | https://icml.cc/virtual/2024/awards_detail | primary |
| 2025 | Submissions | 12,107 | The fact sheet does not state submissions. 12,107 appears only in secondary sources | partly confirmed (secondary only) | https://media.icml.cc/Conferences/ICML2025/ICML2025_Fact_Sheet.pdf | N secondary |
| 2025 | Accepted, rate | 3,260; 26.9% | Fact sheet: main track 3,260, rate "27%"; 3,260/12,107 = 26.9%. PMLR v267 has 3,330 papers (75 position) | confirmed | same; https://proceedings.mlr.press/v267/ | primary |
| 2025 | Orals | 120 | Fact sheet: 120 orals. Virtual site: 108 main-track orals plus 12 position-track orals | partly confirmed (main track is 108) | fact sheet; https://icml.cc/static/virtual/data/icml-2025-orals-posters.json | primary |
| 2025 | Awards | 6 | 6 Outstanding Papers (main track) plus 2 Outstanding Position Papers | confirmed | https://icml.cc/virtual/2025/awards_detail | primary |
| 2026 | Submissions, accepted, rate | 23,918; 6,352; 26.6% | Official ICML post: 23,918 entered review, 6,352 accepted, 26.6%, 536 spotlights. Paper by the 2026 PCs: 24,661 total = 23,918 main + 743 position; 6,552 accepted overall. Fact sheet: 24,661 and 6,552 (both include position track) | confirmed (main-track figures) | https://x.com/icmlconf/status/2049919242862985559 ; https://arxiv.org/pdf/2609.19420 (p. 3, 5); https://media.icml.cc/Conferences/ICML2026/ICML2026_Fact_Sheet.pdf | primary |
| 2026 | Orals | 159 main + 9 position = 168 | Virtual site: 159 orals from the main-track group, 9 from the position-track group | confirmed | https://icml.cc/static/virtual/data/icml-2026-orals-posters.json | primary |
| 2026 | Awards | 2 | 2 Outstanding Papers (main track), plus 1 Outstanding Position Paper and 5 + 1 honourable mentions | confirmed | https://blog.icml.cc/2026/07/05/announcing-the-icml-2026-awards/ | primary |

Notes on §10.4:

- The §10.4 source line says the ICML 2026 awards post holds the 2026 counts. It does not. It lists only the awards. The 2026 counts are in the ICML post on X, the PC paper (arXiv:2609.19420) and the 2026 fact sheet.
- The ICML thread's fourth post gives the position track separately: 742 reviewed, 215 accepted, 39 spotlights (https://x.com/icmlconf/status/2049925366949581092).
- The official ICML account on X is an official channel, so I count it as primary.
- 2016 had a talk for every accepted paper (PC letter), so "orals" has no meaning for 2016.

## §10.3 ICML rows (reviewers per paper and score scales)

| Claim | Handoff | Found | Outcome | Source | Primary |
|---|---|---|---|---|---|
| ICML 2025 reviewers assigned | 4 assigned, at least 3 required | AC instructions: check that each paper has four qualified reviewers; each paper must get at least three high-quality reviews | confirmed; the cited ReviewerInstructions page does not hold this text, the AC page does | https://icml.cc/Conferences/2025/AreaChairInstructions | primary |
| ICML 2026 reviewers assigned | 4 assigned, at least 3 required | AC instructions: four qualified reviewers ("we may revise this"); at least three reviews. FAQ: over 99% of papers had at least three reviews at rebuttal start | confirmed | https://icml.cc/Conferences/2026/AreaChairInstructions ; https://icml.cc/Conferences/2026/PeerReviewFAQ | primary |
| ICML 2024 assignment | 3 auto-assigned + 1 AC-chosen | PC blog: four reviewers per paper, three auto-assigned by OpenReview, one by the AC; some papers may end with three reviews | confirmed | https://medium.com/@icml2024pc/reviewing-at-icml-2024-a7aa81169d8c (read through https://medium.com/feed/@icml2024pc because the page returns 403) | primary |
| ICML 2026 realised reviews per paper | about 3.3 (S) | PC paper: 90,822 main-track reviews over 23,918 main-track papers = 3.80. The policy split (about 53,000 + 34,000) gives about 3.6. Of the analysed permissive-policy papers, 80.9% had exactly four reviewers. The 3.3 figure matches only the rough "795 reviews = about 1% of all reviews" statement in the LLM blog post | contradicted | https://arxiv.org/pdf/2609.19420 (p. 7, 9, 40); https://blog.icml.cc/2026/03/18/on-violations-of-llm-review-policies/ | primary |
| ICML 2023 overall score | 1 to 10 | PC co-authored paper: scale from 1 (very strong reject) to 10 (award quality); papers "generally" had three or four reviewers | confirmed | https://arxiv.org/pdf/2408.13430 (p. 5) | primary |
| ICML 2024 overall score | 1 to 10 | Reviewer instructions: 10 award quality down to 1 very strong reject; confidence 1 to 5 | confirmed | https://icml.cc/Conferences/2024/ReviewerInstructions | primary |
| ICML 2025 overall score | 1 to 5 (5 strong accept ... 1 reject), no confidence | Main-track form: 5 strong accept, 4 accept, 3 weak accept, 2 weak reject, 1 reject; no confidence item. AC page: no numerical confidence scores this year. The position-paper form still had a 1 to 5 confidence item | confirmed (main track) | https://icml.cc/Conferences/2025/ReviewerInstructions ; https://icml.cc/Conferences/2025/AreaChairInstructions | primary |
| ICML 2026 overall score | 1 to 6 with 1 to 5 confidence | Reviewer instructions: 6 strong accept, 5 accept, 4 weak accept, 3 weak reject, 2 reject, 1 strong reject; confidence 1 to 5 | confirmed; the cited PeerReviewFAQ does not hold the scale, the ReviewerInstructions page does | https://icml.cc/Conferences/2026/ReviewerInstructions | primary |

## §10.5 ICML-related rows (how decisions are made)

| Claim | Handoff | Found | Outcome | Source | Primary |
|---|---|---|---|---|---|
| No venue decides by mean score alone (ICML part; the row cites only NeurIPS and ICLR) | ACs recommend with a meta-review; SACs calibrate | ICML 2025 and 2026 AC instructions: ACs write meta-reviews and make accept/reject recommendations from review content, not from average scores; SACs may ask for adjustments or calibration. 2026 FAQ: the average score is not a direct indication of the decision. 2026 awards: PCs chose candidates from reviewer scores and AC nominations | confirmed for ICML | https://icml.cc/Conferences/2025/AreaChairInstructions ; https://icml.cc/Conferences/2026/AreaChairInstructions ; https://icml.cc/Conferences/2026/PeerReviewFAQ | primary |
| ICML 2026 desk rejections for LLM-review violations | 497 | 497 papers (about 2% of submissions) desk-rejected; they belong to 398 reciprocal reviewers who broke Policy A; 795 flagged reviews from 506 reviewers | confirmed | https://blog.icml.cc/2026/03/18/on-violations-of-llm-review-policies/ | primary |

## Sources that failed or were not reachable

- The ICML 2019 to 2023 fact sheets do not exist at the media.icml.cc fact-sheet path (HTTP 404). Fact sheets exist only for 2024 to 2026.
- The ICML press pages for 2019 to 2023 redirect to the 2026 press page.
- The Wayback Machine returned errors for ICML 2019 to 2023 media listings, so I found no archived 2019 to 2022 conference books.
- The ICML 2024 PC Medium page returns HTTP 403; its RSS feed has the full text.

## Code check

This task did not touch model.py, simulate.py or calibrate.py. I found no bug in them during this task.
