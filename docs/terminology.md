# Terminology

One vocabulary for the paper, the figures, the code and the docs. Agreed with Rylan on
2026-10-10. Every tier is named by the decision itself, and "award" is the one umbrella word
for everything above plain acceptance.

One Best Papers notion (Rylan, 2026-10-17): the Best Papers are the first three papers of the award ordering
at every size, a constant number. NeurIPS named 1 to 13 main-track Best Papers a year from 2014 to 2025
(median 2.5, mean 3.5) and 1 to 15 across all tracks (median 3, mean 4.2; data/neurips_best_papers.csv);
three sits between. There is no single #1 paper and no top ten anywhere in the paper, figures or code
the paper reads. Tiers, top to bottom: Best Papers, Oral, Spotlight, Accepted, Rejected.

Always "Best Papers", plural (Rylan, 2026-10-17): the tier, its legend and panel labels, and the outcome "Best Papers
again". Never the singular "Best Paper" as our term: write "one of the Best Papers", "the Best Papers' overlap",
"the probabilities for the Best Papers". The singular stays only in a conference's own award name ("Best Paper"
award) and in cited titles.

Tier names are proper nouns (Rylan, 2026-10-17): Best Papers, Oral, Spotlight, Poster, capitalised
everywhere in the text, captions and figure labels, also as adjectives ("the Oral tier", "an Oral
paper"). "Accepted" and "Rejected" are capitalised only when they name a tier in a list of tiers
(Rylan: "Rejected, Accepted, Spotlight, Oral, Best Papers") or a decision label in a pair ("Spotlight/Reject");
"accepted papers", "rejects", "merely accepted" stay lowercase as ordinary words. "The best papers stand far
apart" (the top of the quality distribution, not the tier) stays lowercase.

| Term | Meaning | Do not say |
|---|---|---|
| tier | one rung of a venue's decisions. Tiers are nested: Best Papers ⊂ Oral ⊂ Spotlight ⊂ accepted. Each tier includes the tiers above it. | |
| accepted | the acceptance tier, a fixed proportion of submissions (NeurIPS: N^1.05) | "accepts" as a noun |
| award | any decision above acceptance: Spotlight, Oral or Best Papers | "highlight", "distinction"; "award" meaning the Best Papers alone |
| Spotlight, Oral | the two award tiers that grow more slowly than submissions (N^0.72, N^0.59) | "highlights (spotlights and orals)" |
| Best Papers | the top award tier: the first three papers of the award ordering at every N, a constant number (N^0; the NeurIPS main-track count fits N^0.27±0.25, 2014-2025); one paper of the tier is "one of the Best Papers" | "Best Paper" (singular) in any form; "the Best Paper" for the #1 paper; "the top paper"; "the award" or "awards" for this tier alone |
| fixed proportion, constant number, between | the three scaling classes of a tier's count in N | "share" |
| award ordering | the ranking on which the award tiers are cut within the accepted papers: the score plus a chair noise η (SD σ_η = 0.59 on the 1-10 axis, fitted on the NeurIPS 2021 pairs' scores); the Best Papers are its first three papers; two reviews' award orderings correlate at ρ_a² < ρ² | "award score", "the chairs' ranking" |
| chair noise | η in the award ordering: the area, senior area and program chairs' own call on a paper's tier, redrawn by a second review with u and ε | "AC noise", "subjectivity" |
| independent chair calls (k) | a what-if lever in Table tab:levers: k chairs judge each accepted paper independently and their calls are averaged, so the chair noise shrinks to σ_η/√k; k = ∞ is an award that follows the scores alone (`scripts/run_chair_calls.py`, `results/chair_calls.csv`) | |
| a second review | peer review run again on the same papers with new reviewers and area chairs, as in the NeurIPS 2014 and 2021 experiments; the model redraws u and ε, so a paper's two scores correlate at ρ² | "a second committee" (reads as a best-paper committee) |
| lands in tier X / X again | under a second review one of the Best Papers (the first review's three) is ranked within tier X's count; every probability is the mean over the three | "oral range" |
| Best Papers again | a second review also ranks a paper among the first review's Best Papers among its own three; its probability equals the overlap of the two reviews' Best Papers | "Best Paper again", "confirms the Best Paper", "ranks it first (again)", "top ten (again)" |
| merely accepted | accepted with no award, so below the Spotlight cutoff | "accepted but outside the oral range" |
| overlap of a tier | the proportion of one review's tier that the other also puts in that tier | |
| the quality variants that keep the Best Papers reproducible | name them: exponential, lognormal and $t_3$ quality, under which the best papers stand far apart. No tail-class label: the exponential is not heavy-tailed | "the three heavy-tailed variants" |
| the model, the main model | the NeurIPS review process: the integer 1 to 10 score of 2014 to 2024 and the four reviews per paper of 2020 on, the form of the NeurIPS 2021 experiment. Four reviews per paper, each the integer from 1 to 10 nearest to quality plus noise, Gaussian quality and reviewer noise, no shared noise; acceptance by mean score, ties at random; award tiers cut on the award ordering, σ_η = 0.59 (`peerreview.model.MAIN_FORM`, `peerreview.levels.main_model`). Sections 3 and 4 use it; the ICLR test (Section 2.2) scores on ICLR's own form because its data are ICLR reviews, and Section 5 runs the other forms. Its row in Figs 4 and 6 is "Main model" (Gaussian quality and noise on this form) | "the Gaussian model" for the main results; "continuous scores" only for the scale section's form and for the closed form of Section 3 (`tier_scaling.csv`), which labels each level by its reliability |
| committee | only the real program committees of the NeurIPS 2014 and 2021 experiments, and real award committees | |

Where the terms live in the code: `results/best_paper.csv` and `results/best_paper_robustness.csv`
carry `p2_best`, `p2_oral`, `p2_spot`, `p2_accept` (nested cutoffs, each the mean over the three Best Papers;
`p2_best` = `overlap_best` is Best Papers again; merely accepted = `p2_accept - p2_spot`); the grid rows of `best_paper.csv` (`source == "grid"`) carry the same on the N grid
plus the overlaps `overlap_*`; `results/tier_scaling.csv` is the continuous-score closed form (`ovl_*`). Figure legends: Fig 1c "Best Papers, Oral, Spotlight, Accepted, Rejected";
Fig 1d-g "Accepted, Spotlight, Oral, Best Papers" (nested: each tier includes the tiers to its right);
Fig 3a,b rows "Main model, No award step, Bounded quality, Exponential quality, Lognormal quality, $t_3$ quality,
$t_3$ noise, Shared noise, 1% rave reviews, 5% rave reviews, 5% random reviews"; Fig 5 the same rows without "No award step".
