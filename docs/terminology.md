# Terminology

One vocabulary for the paper, the figures, the code and the docs. Agreed with Rylan on
2026-10-10. Every tier is named by the decision itself, and "award" is the one umbrella word
for everything above plain acceptance.

| Term | Meaning | Do not say |
|---|---|---|
| tier | one rung of a venue's decisions. Tiers are nested: Best Paper ⊂ oral ⊂ spotlight ⊂ accepted. Each tier includes the tiers above it. | |
| accepted | the acceptance tier, a fixed proportion of submissions (NeurIPS: N^1.05) | "accepts" as a noun |
| award | any decision above acceptance: spotlight, oral or Best Paper | "highlight", "distinction"; "award" meaning the Best Paper alone |
| spotlight, oral | the two award tiers that grow more slowly than submissions (N^0.72, N^0.59) | "highlights (spotlights and orals)" |
| Best Paper | the top award tier, a constant number (1 to 13 a year; the model holds it at N^0; the NeurIPS fit, N^0.34, rests on too few papers to show a trend); "the best-paper award" when the noun is needed | "the award", "awards" for this tier alone |
| fixed proportion, constant number, between | the three scaling classes of a tier's count in N | "share" |
| a second review | peer review run again on the same papers with new reviewers and area chairs, as in the NeurIPS 2014 and 2021 experiments; the model redraws u and ε, so a paper's two scores correlate at ρ² | "a second committee" (reads as a best-paper committee) |
| lands in tier X / X again | under a second review the Best Paper is ranked within tier X's count | "oral range" |
| in the top ten again | ranked within the second review's ten best scores: a constant-number tier larger than one | |
| merely accepted | accepted with no award, so below the spotlight cutoff | "accepted but outside the oral range" |
| overlap of a tier | the proportion of one review's tier that the other also puts in that tier | |
| the quality variants that keep the Best Paper reproducible | name them: exponential, lognormal and $t_3$ quality, under which the best papers stand far apart. No tail-class label: the exponential is not heavy-tailed | "the three heavy-tailed variants" |
| the model, the main model | the NeurIPS review process: the integer 1 to 10 score of 2014 to 2024 and the four reviews per paper of 2020 on, the form of the NeurIPS 2021 experiment. Four reviews per paper, each the integer from 1 to 10 nearest to quality plus noise, Gaussian quality and reviewer noise, no shared noise, mean score, ties at random (`peerreview.model.MAIN_FORM`). Sections 3 and 4 use it; the ICLR test (Section 2.2) scores on ICLR's own form because its data are ICLR reviews, and Section 5 runs the other forms. Its row in Figs 3 and 6 is "Main model" (Gaussian quality and noise on this form) | "the Gaussian model" for the main results; "continuous" anywhere but the scale section |
| committee | only the real program committees of the NeurIPS 2014 and 2021 experiments, and real award committees | |

Where the terms live in the code: `results/best_paper.csv` and `results/best_paper_robustness.csv`
carry `p2_best`, `p2_top10`, `p2_oral`, `p2_spot`, `p2_accept` (nested cutoffs; merely accepted
= `p2_accept - p2_spot`); the grid rows of `best_paper.csv` (`source == "grid"`) carry the same on the N grid
plus the overlaps `overlap_*`; `results/tier_scaling.csv` is the continuous-score closed form (`ovl_*`). Figure legends: Fig 1c "Top 10, Oral, Spotlight, Merely accepted, Rejected";
Fig 3a,b "Accepted, Spotlight, Oral, Top 10, Best Paper".
