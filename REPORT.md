# Report: Scaling Laws of Machine Learning Conference Peer Review

This report gives every finding of the study, with the number behind each one. The
paper (`paper/main.pdf`) is the short version. The specification is
`docs/handoff.md`; departures from it are listed in §8.

All numbers are at the **central** reliability $\rho^2 = 0.50$ unless a range is given.
Ranges run from the pessimistic level ($\rho^2 = 0.44$) to the optimistic level
($\rho^2 = 0.71$). Each number traces to a CSV in `results/` or to a sourced claim in
`docs/claims.md`.

## 1. Summary

The paper asks one question: as submissions grow, does review still give its awards to the
right papers? Items A and B answer it; items 1 to 8 give the supporting results.

A. **A Best Paper is almost always a good paper but rarely the best one.** The model's Best
   Paper (the top-scored paper) at NeurIPS 2026 size is truly the best with probability
   6.6%, in the true top 10 with 25%, oral-worthy with 63%, merely accept-worthy with 37%,
   and should have been rejected with 0.09%. From NeurIPS 2014 to 2026 the first chance
   fell from 12.1% to 6.6% (§6).
B. **How sure: the quality tail decides P(best); careless raves decide P(reject).** Across
   variants refitted to the same acceptance data, P(best) at NeurIPS 2026 size runs from
   1.3% (bounded quality) to 92% ($t_3$ quality). The NeurIPS 2021 top-tier overlap rejects
   the heavy-tailed quality variants ($P \le 0.04$). Under the rest, P(best) is 1.3% to
   6.7%, P(merely accept-worthy) 37% to 65%, and P(should have been rejected) 0.09% to
   5.4%; the top value comes from 5% careless "rave" reviews (§6).

1. **Fixed-number selections degrade as conferences grow; fixed-percentile selections
   do not.** Top-10 precision is 27% at $N = 10^3$, 16% at $10^4$, 10% at $10^5$ and 6% at
   $10^6$ (exact theory; range at $10^6$: 4% to 19%). The precision of a top-0.5% set is
   24% from $N = 10^4$ on (23% at $10^3$, where the set holds five papers); at every $N$,
   that of a top-5% set is 40%, of a top-20% set 57%, and of a 25% accept set 61%.
2. **The decay is a power law with no floor.** Fixed-$K$ precision behaves as
   $C_K N^{-(1-\rho)/(1+\rho)} (4\pi \log N)^{-\rho/(1+\rho)}$. The exponent is 0.17
   (0.20 pessimistic, 0.08 optimistic). Over $10^3 \le N \le 10^6$ the observed decay is
   about 1.2 to 1.4 times steeper than the exponent at our three levels.
3. **The best paper is rarely recognised at scale.** It is in the top 10 by score 49% of
   the time at $N = 10^3$ and 13% at $10^6$; it wins outright 14% and 3% of the time. The
   top-scored paper's median true rank is 11 at $10^3$, 32 at $10^4$, 94 at $10^5$ and
   281 at $10^6$ (exact theory; the simulations give 48%, 13%, 13%, 3% and 11, 31, 94, 288).
4. **The selected papers are very good, not the best.** The top 10 by score sit at the
   97th true percentile on average at $N = 10^4$ and the 99.5th at $10^6$; 53% and 88% of
   them lie in the true top 1%.
5. **Only reliability matters, and it is expensive.** In the Gaussian model the noise
   parameters act only through $\rho^2$. Holding top-10 precision at its $N = 10^3$ value
   needs 5.6, 8.3 and 11.1 reviews per paper at $N = 10^4$, $10^5$, $10^6$ (6.9, 13.4 and
   26.1 with shared noise $\sigma_u = 0.5$).
6. **The tails decide the top.** Power-law ($t_3$) quality makes top-10 precision rise with
   $N$ (66% to 96%); exponential quality gives a plateau (57% to 55%); bounded quality or
   heavy-tailed noise make it collapse toward chance. Coarse score scales with random
   tie-breaking turn the top into a lottery at large $N$ (0.6% to 1.2% at $10^6$ against 6%
   continuous).
7. **The accept/reject boundary is robust and $N$-free.** At 25% acceptance, 39% of
   accepted papers are not in the true top 25%, in every variant (38.4% to 39.6%). The
   number of such papers grows with $N$: NeurIPS about 160 in 2014 and about 3,050 in
   2026.
8. **The real top tier is noisier than the model.** In the NeurIPS 2021 experiment the
   other committee rejected 54% of each committee's spotlights; the calibrated Gaussian
   model predicts 31% ($P(\ge 54\%) = 0.002$). A possible cause is judgement beyond scores,
   which the model leaves out. ICLR review halves match the model at the accept level.

## 2. Definitions

`docs/metrics.md` defines every metric. In brief: the **precision** of a selection of
size $K$ is $|\mathrm{Top}_K(\bar s) \cap \mathrm{Top}_K(q)|/K$; with a fixed quota,
$1 -$ precision is also the share of deserving papers left out. The **swap fraction** is
$1 -$ precision at the acceptance rate. The **disagreement** is
$P(\text{rejected by 2} \mid \text{accepted by 1})$, and the share of papers with
inconsistent decisions is $2\alpha$ times the disagreement.

## 3. Model and calibration

The model is $s_{ij} = q_i + u_i + \varepsilon_{ij}$ with $q \sim \mathcal N(5, 1.2^2)$,
shared noise $u$ and reviewer noise $\varepsilon$; the score is the mean of $R$ reviews
(snapped to a scale in the discrete variants), ties broken at random. The reliability is
$\rho^2 = \sigma_q^2 / (\sigma_q^2 + \sigma_u^2 + \sigma_\varepsilon^2/R)$, and two
independent committees' scores correlate at $\rho^2$.

**Reliability estimates** (`results/calibration_reliability.csv`):

| Source | Method | $\rho^2$ |
|---|---|---|
| NeurIPS 2021, 764 decided papers, 26.2% acceptance | inverse of two-committee inconsistency | **0.504** (central) |
| NeurIPS 2021, all 882 papers, 22.7% (as quoted) | same; counts 118 double withdrawals as agreement | 0.557 |
| NeurIPS 2014 raw table, 26.2% acceptance | same | 0.527 |
| NeurIPS 2014 quoted, 22.5% target acceptance (realised 24.7%) | same | **0.436** (pessimistic) |
| NeurIPS 2014 committee score correlation | direct | 0.550 |
| NeurIPS 2021 committee score correlation (initial, final) | direct | 0.575, 0.586 |
| ICLR inter-review correlation 0.40, $R = 3.7$ | Spearman-Brown (reviewer level only) | **0.712** (optimistic) |
| NeurIPS 2014 variance components, $R = 3$ to 4 | Spearman-Brown (reviewer level only) | 0.72 to 0.80 |

The estimates that include the area chair (the inconsistency inversions) sit at 0.44 to
0.56. The score correlations sit at 0.55 to 0.59. The reviewer-level estimates sit at
0.67 to 0.80 and are upper bounds, because they omit everything the reviewers of one
paper share. The 95% interval of the NeurIPS 2021 estimate is 0.39 to 0.61.

**Per-variant recalibration** (`results/calibration_variants.csv`). Every discrete-scale,
non-Gaussian-quality and $t_3$-noise variant (the Gaussian shared-noise variants are solved in closed form) is refitted by bisection on
$\sigma_\varepsilon$ so that its simulated disagreement at 26.2% acceptance equals the
Gaussian model's at each level (5,000 papers, 2,000 conference pairs, common random
numbers, tolerance $5 \times 10^{-4}$). All 60 fits converged. On coarse scales the
disagreement is not monotone in $\sigma_\varepsilon$: near-noiseless reviewers put many
papers on the same score, and random tie-breaking then dominates. The five-point scale at
the optimistic level has two roots; the fit takes the one above the minimum.

## 4. Analytical results

`docs/derivations.md` gives the full derivations. Two analysts derived §6 independently;
a reconciler settled every difference by quadrature, exact small-$N$ computation and
simulation. Two adversarial verifiers re-derived the asymptotic law and compared every
function with the simulator.

| Item | Result |
|---|---|
| Reliability | $\rho^2$ as above; two committees correlate at $\rho^2$; ceiling $\sigma_q^2/(\sigma_q^2+\sigma_u^2)$ as $R \to \infty$ (0.85 at $\sigma_u = 0.5$). |
| Fixed percentile | $\mathrm{prec}(p) = P_2(z_p, z_p; \rho)/p$, free of $N$; the finite-$N$ deficit is $O(1/K)$ relative. |
| Disagreement | $1 - P_2(z_\alpha, z_\alpha; \rho^2)/\alpha$; inconsistent share $= 2\alpha \times$ disagreement; unique inverse. |
| Fixed number | exact 2-D integral at finite $N$; $\mathrm{prec}_{N,K} \sim \frac{(1+\rho)^2}{K\sqrt{1-\rho^2}} \big[\frac{\Gamma(K+1/(1+\rho))}{\Gamma(K)}\big]^2 N^{-(1-\rho)/(1+\rho)} (4\pi\log N)^{-\rho/(1+\rho)}$, relative correction $O(\log\log N/\log N)$; checked to $N = 10^{300}$. |
| Mechanism | top scores and the true top-$K$ bar both sit near $\sqrt{2\log N}$; the top scores' quality is $\mathcal N(\rho b_N, 1-\rho^2)$; the gap in SD units grows as $\sqrt{(1-\rho)/(1+\rho)}\sqrt{2\log N}$. |
| Containment | for fixed $K$ and fixed $p$, the share of $\mathrm{Top}_K(\bar s)$ in the true top $p$ tends to 1. |
| Best paper | same rate $N^{-(1-\rho)/(1+\rho)}$; $P(\text{best wins}) = \mathrm{prec}_{N,1}$. |
| Winner's rank | $P(\text{rank} \le r) = P(\text{best} \in \mathrm{Top}_r)$; median $\approx \frac{e^{-\gamma\rho^2}}{\rho}(N/\sqrt{4\pi\log N})^{1-\rho^2}$. |
| Two-committee top-$K$ overlap | equals fixed-$K$ precision at correlation $\rho^2$; rate $N^{-(1-\rho^2)/(1+\rho^2)}$. |
| Tails | Gaussian/Gaussian decays; exponential/Gaussian plateaus; $t_3$/Gaussian rises to 1; $t_3$/$t_3$ plateaus; bounded/Gaussian and any heavier-noise case collapse. Fixed-percentile precision is $N$-free for every shape. |
| Acceptance rate | wrong accepts per paper $\alpha \cdot \mathrm{swap}(\alpha)$ is zero at $\alpha = 0$ and concave, so its ratio to $\alpha$, the swap fraction, falls as $\alpha$ rises. |
| Discretisation | no closed form (lattice law, ties, bounded top); fixed percentile stays $N$-free; fixed $K$ becomes a lottery in the top tie class, $\mathrm{prec} \approx K/(N\pi_{\rm top})$. |

## 5. Simulation results

Sweeps (a) to (h) of the handoff are in `results/sweep_{a..h}.csv` (one row per
configuration, with seed, replicate count and wall time). 10,000 conferences per setting
up to $N = 2 \times 10^4$; above that a budget of $2 \times 10^8$ paper draws, down to 200 at $N = 10^6$ (a budget of $10^9$ draws, 10,000 up to $N = 10^5$ and at least 2,000
conferences for the main sweep g); 10,000 conferences at every $N$ for the best-paper sweep
h. Analytic and simulated values agree within Monte Carlo error
(`results/verify_analytic.csv`).

**Main sweep** (`sweep_g.csv`, central):

| $N$ | top 5 | top 10 | top 30 | top 100 | top 0.5% | top 5% | top 20% | accept 25% |
|---|---|---|---|---|---|---|---|---|
| 1,000 | 22.7% | 27.1% | 35.3% | 47.5% | 22.7% | 39.9% | 57.2% | 60.8% |
| 10,000 | 13.9% | 16.5% | 21.0% | 27.6% | 23.5% | 40.1% | 57.2% | 60.8% |
| 100,000 | 9.0% | 10.4% | 13.0% | 16.7% | 23.6% | 40.1% | 57.2% | 60.8% |
| 1,000,000 | 5.4% | 6.4% | 8.3% | 10.5% | 23.7% | 40.1% | 57.2% | 60.9% |

**Best paper** (`sweep_h.csv`, central): in the top 10 by score 47.8%, 31.1%, 20.2%, 13.2%
at $N = 10^3, 10^4, 10^5, 10^6$; wins outright 13.4%, 8.5%, 5.1%, 3.1%. Two-committee
top-10 overlap (`sweep_g.csv`): 13.0%, 5.4%, 2.3%, 1.0%.

**Reviewer noise and reviewer count** (`sweep_c.csv`, `sweep_b.csv`). At $N = 10^4$, top-10
precision runs from 83% ($\sigma_\varepsilon = 0.25$) to 6% ($\sigma_\varepsilon = 3.5$) at
$R = 3$. At $N = 20{,}000$, raising $R$ from 3 to 10 lifts top-10 precision from 14% to 36%
without shared noise and to 29% with it; at $R = 50$ the values are 66% and 42%. The swap
fraction at 25% acceptance falls from 39% to 25% (29% with shared noise) over the same
change. Reviews needed to hold top-10 precision: `analytic_R_needed.csv`.

**Quality and noise tails** (`sweep_d.csv`, top-10 precision, $N = 10^3 \to 10^6$, $R = 3$):

| Quality | Gaussian noise | $t_3$ noise |
|---|---|---|
| heavy tail ($t_3$) | 66% → 96% | 52% → 69% |
| exponential tail | 57% → 55% | 42% → 0% |
| lognormal | 40% → 36% | 26% → 0% |
| Gaussian | 27% → 7% | 15% → 0% |
| bounded (Beta) | 21% → 0.7% | 11% → 0% |

Top-1% precision is $N$-free in every row (Gaussian 27.6%, bounded 21.3%, exponential
57.8%, lognormal 41.3%, $t_3$ 67.6% with Gaussian noise). The swap fraction at 25%
acceptance is 38.4% to 39.6% in every cell.

**Score scales** (`sweep_e.csv`, $R = 4$, each recalibrated):

| Scale | top 10, $N=10^4$ | top 10, $N=10^6$ | top 1% | swap at 25% |
|---|---|---|---|---|
| continuous | 16.4% | 6.8% | 27.6% | 39.1% |
| integer 1-10 | 13.3% | 1.2% | 26.0% | 39.1% |
| ICLR {1,3,5,6,8,10} | 12.0% | 0.9% | 25.6% | 39.0% |
| six-point | 12.7% | 0.8% | 25.5% | 39.0% |
| five-point | 12.5% | 0.6% | 26.8% | 39.1% |

Placing the six- and five-point scales on their own range (1 to 6, 1 to 5) with the
latent distribution mapped affinely gives the same numbers within Monte Carlo error, as
it must. Shifting the latent mean by half a scale step changes fixed-$K$ precision at
$N = 10^5$ by up to a factor of three (five-point: 1.1% against 3.6%) and leaves the swap
fraction at 39%. Random tie-breaking is one extreme (a chair with no information);
continuous scores are the other (a chair with full information).

**Acceptance rate** (`sweep_f.csv`, $N = 10^4$): swap fraction 52.4%, 42.8%, 39.2%,
35.9%, 30.1% at $\alpha$ = 10%, 20%, 25%, 30%, 40%; disagreement 67.4%, 51.7% and 40.1% at
10%, 25%, 40%.

## 6. Historical application

`results/history.csv`: the central model at each venue-year's submissions, acceptance
rate and main-track oral count (values from `data/venues.csv`, `*_used` columns).

| Venue-year | $N$ | top-10 precision | oral-set precision | wrong accepts | disagreement |
|---|---|---|---|---|---|
| NeurIPS 2014 | 1,678 | 24.4% | 28.6% (20 orals) | 163 | 52.0% |
| NeurIPS 2020 | 9,467 | 16.5% | 28.2% (105) | 812 | 56.1% |
| NeurIPS 2025 | 21,575 | 13.8% | 21.9% (77) | 2,088 | 52.1% |
| NeurIPS 2026 | 30,709 | 13.0% | 22.1% (112) | 3,052 | 51.1% |
| ICML 2026 | 23,918 | 13.6% | 25.2% (159) | 2,421 | 50.3% |
| ICLR 2026 (valid) | 19,525 | 14.4% | 28.4% (224) | 2,008 | 49.7% |

`results/history.csv` gives every year: (a) top-10 precision, (b) precision of the
real oral set, (c) the probability that the best paper is in the top 10 by score. Lines are
central; the band (NeurIPS only) spans the pessimistic and optimistic levels. At NeurIPS the
top-scored paper's median true rank rises from 15 (2014) to 55 (2026), and the best paper is
among the ten top-scored papers with probability 44% (2014) and 25% (2026).

**What the Best Paper deserved** (`results/best_paper.csv`, `scripts/make_best_paper.py`).
The model's Best Paper is the top-scored paper. Exact probabilities (containment_fixed_K
with K = 1) that it is truly in each tier, central level (pessimistic to optimistic):

| Tier | NeurIPS 2014 ($N$ = 1,678) | NeurIPS 2026 ($N$ = 30,709) |
|---|---|---|
| the true best | 12.1% (9.2 to 25.4) | 6.6% (4.6 to 17.7) |
| the true top 10 | 44.0% (36.0 to 71.6) | 25.2% (18.5 to 54.2) |
| the true top oral count (20; 112) | 57.7% (48.8 to 84.1) | 62.8% (51.9 to 91.2) |
| the true top 10% | 93.5% (88.9 to 99.6) | 98.8% (96.9 to 100.0) |
| the true accepted set (24.7%; 25.7%) | 99.0% (97.7 to 100.0) | 99.91% (99.63 to 100.00) |
| should have been rejected | 1.0% (2.3 to 0.01) | 0.09% (0.37 to 0.00) |
| a second committee would reject it | 12.3% (19.2 to 1.0) | 5.2% (10.4 to 0.1) |

The chance that the Best Paper deserved rejection falls with $N$ (1.4% at $10^3$, 0.01% at
$10^6$, 25% acceptance), because the top score of a larger pool is more extreme and its
quality sits further above the fixed-percentile acceptance bar. The chance that it is the
true best falls at the same time. A direct simulation at the central level (200,000
conferences at $N$ = 1,678; 40,000 at 30,709) agrees within sampling error: 12.15% best,
99.00% accept-worthy at 1,678; 6.47% best, 62.5% oral-worthy, 99.89% accept-worthy at 30,709.

**How sure: the Best Paper under every variant** (`results/best_paper_robustness.csv`,
`scripts/run_best_paper_robustness.py`, paper Fig. 5). Each variant is refitted to the
central NeurIPS 2021 disagreement (`results/calibration_variants.csv`) and simulated at
NeurIPS 2014 size (200,000 conferences) and 2026 size (40,000). Careless reviewers ignore
the paper: a "rave" review gives 10, a "random" review a uniform score on the 1-10 scale
(`ReviewModel.careless`, `careless_kind`). Each variant also replays the NeurIPS 2021
top tiers (4,000 replays; observed overlap 3). Values at 2026 size (2014 in brackets):

| Variant | P(best) | P(merely accept-worthy) | P(should be rejected) | 2021 overlap: mean, P(≤3) |
|---|---|---|---|---|
| Gaussian, R = 4 | 6.7% (12.1%) | 37.0% | 0.09% (0.96%) | 5.76, 0.17 |
| bounded quality | 1.3% (5.6%) | 63.6% | 0.35% (1.74%) | 4.98, 0.26 |
| exponential quality | 49.9% (49.8%) | 0.06% | 0% (0%) | 11.70, 0.002 |
| lognormal quality | 29.3% (30.2%) | 4.1% | 0% (0.11%) | 7.95, 0.04 |
| $t_3$ quality | 92.0% (80.2%) | 0% | 0% (0%) | 11.65, 0.001 |
| 1-10 scale | 2.6% (9.5%) | 57.3% | 0.54% (1.75%) | 5.60, 0.18 |
| ICLR scale | 1.5% (8.4%) | 64.9% | 0.94% (1.98%) | 5.53, 0.19 |
| $t_3$ noise, 1-10 | 4.1% (11.9%) | 49.2% | 2.07% (2.93%) | 5.85, 0.17 |
| 1% rave reviews | 2.7% (9.6%) | 56.8% | 0.79% (2.06%) | 5.65, 0.18 |
| 5% rave reviews | 2.8% (10.7%) | 53.1% | 5.41% (4.80%) | 5.73, 0.17 |
| 5% random reviews | 3.3% (10.3%) | 51.6% | 0.38% (1.42%) | 5.76, 0.17 |

Heavy-tailed quality puts the best papers far apart, so review finds them and P(best)
barely changes with size; but it predicts 8 to 12 shared highlights against 3 observed.
Every light-tailed variant predicts 5 to 6. P(should be rejected) falls with size in every
variant except 5% raves: one rave lifts a weak paper's mean far above its merit, and the
top-scored paper is the one most likely to have drawn one.

## 7. Validation

**NeurIPS 2021 top tier** (`results/validation_neurips2021.csv`). Among the 764 decided
papers, the oral-plus-spotlight tiers held 29 and 25 papers and shared 3; the other
committee rejected 26 of the 48 spotlights (54%). Replayed as a 764-paper subsample of a
7,902-paper conference, at the central level:

| Variant | tier overlap (90% range) | $P(\le 3)$ | spotlights rejected | $P(\ge 54\%)$ |
|---|---|---|---|---|
| Gaussian / Gaussian | 5.8 (2 to 10) | 0.17 | 31% | 0.002 |
| Gaussian / Gaussian + shared | 5.8 (2 to 10) | 0.17 | 31% | 0.001 |
| Gaussian / $t_3$ | 4.3 (1 to 8) | 0.36 | 37% | 0.011 |
| bounded / Gaussian | 4.9 (2 to 9) | 0.28 | 33% | 0.004 |
| bounded / $t_3$ | 3.6 (1 to 7) | 0.51 | 39% | 0.019 |
| exponential / Gaussian | 11.6 (7 to 17) | 0.004 | 16% | < 0.001 |

At the pessimistic level the heavy-tailed-noise variants reach 43% to 45% spotlight
rejection ($P \ge$ observed 0.07 to 0.11), but only with unbounded scores. On a 1-10 scale
(`gauss/t3 1-10`, `beta/t3 1-10`, not plotted) they reach 38% and 40%. The optimistic level
fails in every variant. So the top tier is noisier than the calibrated model, possibly
because committees chose highlights partly on judgement beyond scores.

**ICLR split halves** (`results/iclr_splithalf_observed.csv`, `results/validation_iclr.csv`).
Main-track decided papers with at least four reviews, 200 random splits into two halves
of two reviews; the model uses each year's scale, $R = 2$ per half, latent quality at the year's observed mean and between-paper SD (`placement = observed`), and reviewer noise
fitted to the half-mean correlation (0.49 to 0.55 in 2021 to 2025). Without further
fitting the model gives inconsistency 29% to 33% (observed 29% to 32%) and accepted-set
overlap 54% to 63% (observed 55% to 65%). Top-10 and top-30 overlaps are small in both
(3% to 23%). They agree in 2021; the observed values are 50% to 92% of the model's in
2022 to 2024 and 3.5 to 3.9 times the model's in 2025. The observed values have
split-to-split SDs of 4 to 8 points. The halves share the area chair and the rebuttal, so this test
favours consistency.

**ICLR variance decomposition** (`results/iclr_variance.csv`, decided main-track papers; `docs/claims.md` quotes the all-reviewed columns, for example 0.41 in 2018 and 0.18 in 2026). ICC(1) of individual scores
is 0.58 (2017), 0.40 (2018), 0.45 (2019), 0.37 (2020), 0.34 (2021), 0.39 (2022), 0.37 (2023),
0.33 (2024), 0.33 (2025); between-paper SD 0.82 to 1.34 and within-paper SD 1.03 to 1.76 on
each year's scale. The empirical decision threshold (50% point of a logistic fit) is
5.8 to 6.1 on the 1-10 and ICLR six-point scales (5.4 on the 2020 four-point scale). ICLR 2026, on a new {0,2,4,6,8,10} scale, has an ICC of only 0.13; we keep it
out of the main analyses.

## 8. Departures from the handoff and decisions

1. **§8.1 body missing.** The pasted handoff lacked the body of §8.1. It was
   reconstructed from §3.5 and §10.1 (`docs/handoff.md` marks it).
2. **Central calibration.** The handoff names "23.0% at 22.7%" for NeurIPS 2021. Table 1
   of the 2021 report shows that 118 of the 882 papers were withdrawn from both copies
   and never decided. Excluding them gives 26.6% inconsistent at 26.2% acceptance and
   $\rho^2 = 0.504$, which we adopt; the quoted version gives 0.557 and is reported.
3. **A claimed absence was wrong.** The 2021 report does give the committees' score
   correlation (0.575 initial, 0.586 final).
4. **Venue figures.** Where a primary source contradicted a handoff value, the primary
   value is used and the handoff value kept beside it (`data/venues.csv`,
   `scripts/build_venues_used.py`, `docs/claims.md`). Oral counts are main track only
   (NeurIPS 2025: 77, not 87). NeurIPS 2026 has no primary source yet.
5. **The NeurIPS 2014 choice.** The raw table (0.53) is the right inversion; the quoted
   version (0.44), which applies the inconsistency rate to the wrong acceptance rate,
   serves as the pessimistic bound because it is the lowest point estimate in common use.
6. **Venue-years below $N = 1{,}000$** (ICLR 2017 and 2018) are not tabulated. Fig. 1a
   of the paper still plots their submission counts.
7. **Paper title, template and Fig. 1.** At the author's request (2 October 2026) the
   title is "Scaling Laws of Machine Learning Conference Peer Review", the paper uses the
   NeurIPS 2026 style with its `preprint` option (not a submission), and the paper is framed
   around the two jobs of review: accepting good papers (a fixed percentage of submissions)
   and highlighting the best (orals, spotlights and awards). Highlights grow more slowly
   than submissions: oral rates fall at every venue, and awards stay at 1 to 13 a year, close
   to a fixed number. The paper studies the two limits, fixed percentage and fixed number;
   at real oral counts the model's precision lies between them (`results/history.csv`,
   `prec_orals`, central: NeurIPS 28.6% to 22.1%, ICML 35.5% to 25.2%, ICLR 30.1% to 28.4%).
   The question is whether review still separates signal from noise for each job as
   submissions grow. Fig. 1 has two panels: papers submitted, accepted and given orals per
   year (`data/venues.csv`, `N_used`, `N_used` x `acc_rate_used` and `orals_used`; NeurIPS
   submissions grew 26% a year from 2014 to 2025) and the precision of fixed-number against fixed-percentage selections (top 10 and
   top 100 against the top 1% and top 10%, which are the same sets at $N = 10^3$). The fixed-share curves use
   `analytic.precision_pct_finite` (rows `prec_pct_finite` in `results/analytic_curves.csv`).
   The winner-rank panel left Fig. 1; its numbers stay in the text.
8. **Seven pages and stated takeaways.** The author asked (2 October 2026) for the key
   takeaways to be stated and emphasised, and allowed a seventh page. The paper now states
   four takeaways in the abstract and six ranked conclusions in the Introduction. Results
   paragraphs open with a bold takeaway sentence. The seventh page carries the real-venue
   figure (`figures/fig7_history`, then paper Fig. 4; superseded by item 10). Results ends with implications for program
   chairs, marked as untested. Figure rows are 1.72 in high. Awards are written as "13 or
   fewer a year", because a secondary source says ICLR 2020 gave none (`data/venues.csv`).
9. **Bounded heavy-tailed variants.** Two $t_3$ variants on a 1-10 scale were added to the
   calibration and the NeurIPS 2021 validation (appended rows). They show that heavy-tailed
   noise gets close to the 2021 spotlight result only with unbounded scores.
10. **Restructure around one question (3 October 2026).** At the author's request the
    paper asks one question: as submissions grow, can review still tell good papers from
    bad ones and give its awards to the right papers? The answers are error probabilities
    for the Best Paper (truly best, top 10, oral-worthy, merely accept-worthy, should have
    been rejected). Each section and paragraph runs motivation, method, result,
    implication. Sections: Introduction; Methods; model faithfulness (§7 here); how often
    awards go to the right papers (§6); why awards lose accuracy (§4 to §5); how sure we
    are (§6, robustness table); implications. Five figures: `fig1_headline` (submissions;
    true standing of the Best Paper at NeurIPS 2014, 2021, 2026), `fig2_validation`,
    `fig3_venues` (the four tier probabilities for every venue-year), `fig4_mechanism`,
    `fig5_robustness`. On 4 October 2026 Fig. 1 became three panels at the author's request:
    (a) submissions per year; (b) the share of NeurIPS submissions accepted, given spotlights
    and given orals, so the reader sees that acceptance and spotlights are near-fixed shares
    while the oral share falls (1.2% to 0.4%); (c) the Best Paper's true standing. Spotlight
    counts are in `data/spotlights.csv` (docs/claims.md §10.4a). The careless-reviewer variants and the per-variant 2021 overlap test
    were added for this section; the three careless variants are calibrated at the central
    level only. The Limitations paragraph was folded into the opening of the Implications.

## 9. Limitations

One-dimensional quality; exchangeable reviewers (no leniency offsets, no matching); the
area chair only as shared noise; no rebuttal, discussion, strategic behaviour, desk
rejection or withdrawal; decisions by mean score alone. The calibration rests on two
experiments of 166 and 764 decided papers, whose sampling error spans much of the range
between our pessimistic and optimistic levels. The tail of the quality distribution,
which decides the top-of-ranking results, is not identified by accept-level data. The
heavy-tailed-noise results of §5 use unbounded $t_3$ noise; on a 1-10 scale the Best
Paper at NeurIPS 2026 size is the best 4.1% of the time, against 6.7% Gaussian (§6).
