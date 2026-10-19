# Terminology

One vocabulary for the paper, the figures, the code and the docs. **Read the tier rule first.**

## The tiers are separate, like gold, silver and bronze (Rylan, 2026-10-18)

Every paper gets exactly one tier. No tier contains another.

| Tier | Medal | Meaning | Code key |
|---|---|---|---|
| **Best Papers** | gold | the first three papers of the award ordering | `best` |
| **Oral** | silver | an Oral that is not one of the Best Papers | `oral` |
| **Spotlight** | bronze | a Spotlight, nothing higher | `spot` |
| **Accepted** | qualified for the race, did not place | accepted with no award | `accept` |
| **Rejected** | did not qualify | rejected | `reject` |

"Spotlight" means Spotlight only. "Oral" means Oral only. "Accepted" means accepted with no award.

A union of a tier and every tier above it is named **"X or Better"**, always in full:

| Set | Holds | Code key |
|---|---|---|
| **Oral or Better** | Oral, Best Papers | `oral_or_better` |
| **Spotlight or Better** | Spotlight, Oral, Best Papers | `spot_or_better` |
| **Accepted or Better** | every accepted paper: Accepted, Spotlight, Oral, Best Papers | `accept_or_better` |

Rules that follow:

- Never call an "or Better" set by a bare tier name. "The Spotlight tier, Orals plus Spotlights" is wrong; write "Spotlight or Better".
- Never write "nested tiers", "merely accepted" or "each tier includes the tiers above it".
- Capitalised "Accepted" is only the tier (no award). Lowercase "accept", "accepted" and "acceptance" name the accept/reject decision: "the papers the first review accepted" and "a second review accepts the paper" mean Accepted or Better.
- Name the set "Accepted or Better" in figures, tables, column names, and wherever the Accepted tier is also in view.
- "Award" is any tier above Accepted: Spotlight or Better.
- In code and result files a bare key (`oral`) is the separate tier and a key ending in `_or_better` is the set. `src/peerreview/tiers.py` holds the definitions; no other file defines a tier.

### How the model cuts the tiers

The model sizes the "or Better" sets and reads the separate tiers off as the gaps between them.
The first cut after the Best Papers is M_oob, the size of Oral or Better (NeurIPS's Oral count, which includes its Best Papers; series `oral_or_better` in results/tier_sizes.csv, column `M_oral_or_better` in results/tier_scaling.csv).
The fitted Spotlight count M_spot (series `spot`) counts Spotlights only. A is 25% of N.

| Award-ordering ranks | Tier |
|---|---|
| 1 to 3 | Best Papers |
| 4 to M_oob | Oral |
| M_oob + 1 to M_oob + M_spot | Spotlight |
| M_oob + M_spot + 1 to A (acceptance by mean score) | Accepted |
| the rest | Rejected |

Oral or Better = ranks 1 to M_oob; Spotlight or Better = ranks 1 to M_oob + M_spot; Accepted or Better = the A papers accepted by mean score.

### Result columns

| Column | Meaning |
|---|---|
| `p2_{tier}` | the probability that a second review gives one of the first review's Best Papers that tier (`best`, `oral`, `spot`, `accept`, `reject`); the five sum to 1 |
| `p2_{set}_or_better` | the same for an "or Better" set |
| `p_{tier}`, `p_{set}_or_better` | the same for the Best Papers' true-quality ranks |
| `overlap_{tier}` | the proportion of one review's tier that the other review also puts in that tier |
| `overlap_{set}_or_better` | the same for an "or Better" set; `overlap_accept_or_better` is the acceptance overlap of the NeurIPS experiments |
| `place_{first}_in_{second}` | for a paper in tier `first` of the first review (`best`, `oral`, `spot`, `accept`), the probability that the second review gives it tier `second` (`best` ... `reject`); each first tier's five sum to 1, and `place_X_in_X` is `overlap_X` |
| `n_oral_or_better` | the size of Oral or Better: NeurIPS's Oral count, which includes its Best Papers (not the Oral tier alone) |
| `spotlights` | the size of the Spotlight tier alone |
| `accepted` | the size of Accepted or Better, A (every accepted paper) |
| `M_oral_or_better`, `M_spot_or_better` | tier_scaling.csv: the fitted sizes of Oral or Better and Spotlight or Better |
| `group` | R_needed_tiers_curve.csv and _summary.csv: a separate tier or an "or Better" set |
| `series` | tier_sizes.csv: a fitted count series (`accept_or_better`, `spot`, `oral_or_better`, `best`, and `oral`, the Oral tier alone, fitted 2014 to 2025) |
| `sob_*` | NeurIPS 2021 Spotlight or Better: its Orals plus Spotlights, since 2021 had no Best Papers |

In code, a dict of cutoffs keyed by `CUTS` is a `cut_sizes` (`best_papers_cuts`, `overlap_cuts` in `simulate_best_paper`),
`n_accepted` is the size of Accepted or Better, and `fitted_count(fits, series, N)` reads tier_sizes.csv (series in `SERIES_COLUMNS`).
`spotlight_counts(root)` gives each venue-year's Spotlight count: 0 where the venue-year had no Spotlight tier, so its Accepted tier is defined.
`simulate_best_paper` writes `best_papers_in_{cut}`, `best_papers_in2_{cut}`, `best_papers_rank`, `best_papers_rank2` and `z2_best_papers` for the Best Papers; the sweep simulator `simulate_chunk` keeps `winner_rank`, the true rank of the single first paper of the award ordering.

A separate tier's `p2` is the difference of two "or Better" probabilities of the same papers (`p2_spot = p2_spot_or_better - p2_oral_or_better`).
Its `_se` is the upper bound sqrt(se_hi^2 + se_lo^2), since the two indicators correlate positively (`tiers.add_separate`).
Overlaps and placements of separate tiers are counted directly in the simulator.

## Other terms

One Best Papers notion (Rylan, 2026-10-17): the Best Papers are the first three papers of the award ordering
at every size, a constant number. NeurIPS named 1 to 13 main-track Best Papers a year from 2014 to 2025
(median 2.5, mean 3.5) and 1 to 15 across all tracks (median 3, mean 4.2; data/neurips_best_papers.csv);
three sits between. There is no single #1 paper and no top ten anywhere in the paper, figures or code
the paper reads. Tiers, top to bottom: Best Papers, Oral, Spotlight, Accepted, Rejected; each separate.

Always "Best Papers", plural (Rylan, 2026-10-17): the tier, its legend and panel labels, and the outcome "Best Papers
again". Never the singular "Best Paper" as our term: write "one of the Best Papers", "the Best Papers' overlap",
"the probabilities for the Best Papers". The singular stays only in a conference's own award name ("Best Paper"
award) and in cited titles.

Tier and set names are proper nouns (Rylan, 2026-10-17 and 2026-10-18): Best Papers, Oral, Spotlight,
Accepted, Rejected, Oral or Better, Spotlight or Better, Accepted or Better, capitalised everywhere in the text,
captions and figure labels, also as adjectives ("an Oral paper"). "The best papers stand far apart" (the top of
the quality distribution, not the tier) stays lowercase.

| Term | Meaning | Do not say |
|---|---|---|
| tier | one of the five separate outcomes above; a paper has exactly one | "nested tiers"; a bare tier name for an "or Better" set |
| Accepted | the tier: accepted with no award. Accepted or Better: every accepted paper, a fixed proportion of submissions (NeurIPS: N^1.05) | "merely accepted"; "accepted papers" for Accepted or Better |
| award | any tier above Accepted: Spotlight, Oral or Best Papers (together, Spotlight or Better) | "highlight", "distinction"; "award" meaning the Best Papers alone |
| Spotlight, Oral | the two separate tiers between Accepted and the Best Papers (Spotlight count N^0.72; Oral or Better count N^0.59; the Oral tier alone, without the Best Papers, N^0.63 over 2014 to 2025) | "the Spotlight tier" for Spotlight or Better |
| Best Papers | the top award tier: the first three papers of the award ordering at every N, a constant number (N^0; the NeurIPS main-track count fits N^0.27±0.25, 2014-2025); one paper of the tier is "one of the Best Papers" | "Best Paper" (singular) in any form; "the Best Paper" for the #1 paper; "the top paper"; "the award" or "awards" for this tier alone |
| fixed proportion, constant number, between | the three scaling classes of a tier's count in N | "share" |
| award ordering | the ranking on which the award tiers are cut within the accepted papers: the score plus a chair noise η (SD σ_η = 0.59 on the 1-10 axis, fitted on the NeurIPS 2021 pairs' scores); the Best Papers are its first three papers; two reviews' award orderings correlate at ρ_a² < ρ² | "award score", "the chairs' ranking" |
| chair noise | η in the award ordering: the area, senior area and program chairs' own call on a paper's tier, redrawn by a second review with ε | "AC noise", "subjectivity" |
| independent chair calls (k) | a what-if lever in Table tab:levers: k chairs judge each accepted paper independently and their calls are averaged, so the chair noise shrinks to σ_η/√k; k = ∞ is an award that follows the scores alone (`scripts/run_chair_calls.py`, `results/chair_calls.csv`) | |
| a second review | peer review run again on the same papers with new reviewers and area chairs, as in the NeurIPS 2014 and 2021 experiments; the model redraws ε and η, so a paper's two scores correlate at ρ² | "a second committee" (reads as a best-paper committee) |
| a second review gives the paper tier X | the second review puts the paper in tier X (separate); every probability for the Best Papers is the mean over the three | "oral range"; "lands in X" for an "or Better" set |
| Best Papers again | a second review also ranks a paper among the first review's Best Papers among its own three; its probability equals the overlap of the two reviews' Best Papers | "Best Paper again", "confirms the Best Paper", "ranks it first (again)", "top ten (again)" |
| overlap of a tier | the proportion of one review's tier that the other also puts in that tier; for an "or Better" set, name the set | |
| the quality variants that keep the Best Papers reproducible | name them: exponential, lognormal and $t_3$ quality, under which the best papers stand far apart. No tail-class label: the exponential is not heavy-tailed | "the three heavy-tailed variants" |
| the model, the main model | the NeurIPS review process: the integer 1 to 10 score of 2014 to 2024 and the four reviews per paper of 2020 on, the form of the NeurIPS 2021 experiment. Four reviews per paper, each the integer from 1 to 10 nearest to quality plus noise, Gaussian quality and reviewer noise, no shared noise; acceptance by mean score, ties at random; award tiers cut on the award ordering, σ_η = 0.59 (`peerreview.model.MAIN_FORM`, `peerreview.levels.main_model`). Sections 3 and 4 use it; the ICLR test (Section 2.2) scores on ICLR's own form because its data are ICLR reviews, and Section 5 runs the other forms. Its row in Figs 4 and 6 is "Main model" (Gaussian quality and noise on this form) | "the Gaussian model" for the main results; "continuous scores" only for the scale section's form and for the closed form of Section 3 (`tier_scaling.csv`), which labels each level by its reliability |
| shared noise | u_i, an error that all of a paper's reviewers make alike (presentation, a hot or cold topic, the writing); robustness check only (σ_u = 0.5), zero in the main model and absent from its equation and the schematic (Rylan, 2026-10-18) | "AC noise" |
| committee | only the real program committees of the NeurIPS 2014 and 2021 experiments, and real award committees | |

Figure legends: Fig 1c "Best Papers, Oral, Spotlight, Accepted, Rejected" (separate tiers);
Fig 1d-g "Best Papers, Oral or Better, Spotlight or Better, Accepted or Better" (each curve a tier or better; panels by the
first review's set, the same four; y axis "Probability of this tier or better");
Fig 3a "Spotlight or Better" (the NeurIPS 2021 Orals and Spotlights; the experiment had no Best Papers tier);
Fig 3c "Accepted or Better, Top 30, Top 3"; Fig 4 "Best Papers, Oral, Spotlight, Accepted";
Fig 5 "Best Papers again, Accepted, Rejected"; Fig 6 "Best Papers again, Oral, Rejected".
