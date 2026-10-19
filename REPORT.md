# Report: Scaling Laws of Machine Learning Conference Peer Review

This report gives every finding of the study, with the number behind each one. The
paper (`paper/main.pdf`) is the short version. The specification is
`docs/handoff.md`; §8 lists the departures from it. `docs/terminology.md` defines every
tier word.

A number without a range is at the **central** level ($\rho^2 = 0.50$). A range in
parentheses gives the lowest and highest values over the three calibration levels:
pessimistic ($\rho^2 = 0.44$), central and optimistic ($\rho^2 = 0.71$). Each number traces
to a CSV in `results/` or to a sourced claim in `docs/claims.md`.
`uv run python scripts/paper_numbers.py` prints every simulated number the paper quotes.

## 1. Summary

The paper asks one question: as submissions grow, does peer review still give its awards to
the right papers? It answers in the units of the NeurIPS consistency experiments: a second,
independent review of the same papers (the rerun framing, decision 12 in §8). Every paper
gets exactly one of five separate tiers: **Best Papers** (the first three papers of the award
ordering), **Oral**, **Spotlight**, **Accepted** (accepted with no award) and **Rejected**. A
tier together with every tier above it is named in full: Oral or Better, Spotlight or Better,
Accepted or Better (every accepted paper).

Items A to G come from the main model (§3) and are the paper's numbers. Items 1 to 6 come
from the continuous-score model of §4 and §5, the derivation behind them.

A. **Each tier's count follows a power law in submissions $N$.** At NeurIPS, Accepted or
   Better grows as $N^{1.05}$, a fixed proportion. Spotlight grows as $0.34\,N^{0.72}$ and
   Oral or Better as $0.30\,N^{0.59}$; the Oral tier alone, without the Best Papers, grows as
   $0.18\,N^{0.63}$ (2014 to 2025). NeurIPS named 1 to 13 main-track Best Papers a year
   from 2014 to 2025 (median 2.5, mean 3.5); the fitted exponent, $0.27 \pm 0.25$, cannot be
   told from zero. The model therefore has three Best Papers at every $N$
   (`results/tier_sizes.csv`, `data/venues.csv`, `data/neurips_best_papers.csv`).
B. **A second review almost always accepts NeurIPS 2026's Best Papers but almost never makes
   them Best Papers again.** At 30,709 submissions a second review accepts one of the Best
   Papers 85% of the time (77% to 99%). It makes it Spotlight or Better 18% of the time
   (13% to 45%). The chance of Best Papers again is 0.33% (0.19% to 1.7%). Most often, 67%
   of the time (54% to 67%), the second review makes it Accepted. It rejects it 15% of the
   time (1.4% to 23%). From NeurIPS 2014 to 2021 to 2026 the chance of Best Papers again fell
   from 2.9% to 0.85% to 0.33%, and the chance of Accepted rose from 45% to 52% to 67%. From
   1,000 to 100,000 submissions the chance of Best Papers again falls from 4.1% to 0.12%, a
   power law with exponent 0.77 (0.58 to 0.83). Two reviews' top 0.3%, a fixed proportion,
   overlap by 4.2% at 1,000 and 4.3% at 100,000.
C. **Acceptance is a coin toss at every size.** Two reviews' Accepted or Better sets overlap
   by 48% (45% to 61%) at every size from 1,000 to 100,000 submissions. A second review
   accepts 48% of the papers the first accepted, 25% of all submissions and 17% of the papers
   the first rejected (18% and 17% in the 2014 and 2021 experiments).
D. **Orals and Spotlights fall in between.** From 1,000 to 100,000 submissions the Oral tier
   grows from 14 to 247 papers and the Spotlight tier from 48 to 1,305. Over that range an
   Oral keeps its tier 8.2% to 3.7% of the time, and a Spotlight 14.0% to 8.0%. A second
   review accepts an Oral 68% to 78% of the time and a Spotlight 57% to 69%, because the
   award tiers sit ever farther above the acceptance bar (`results/placement.csv`).
E. **Chairs override the scores for about half the awards.** At NeurIPS 2021 only 26 of the
   53 public Oral and Spotlight papers were among their committee's top-scored papers. In 30
   of the 50 award pairs the meta-review gave the higher tier with no stated grounds. Awards
   that follow the scores alone over-predict the committees' agreement: 5.6 shared Spotlight
   or Better papers against 3 observed, and 30% of them rejected by the other review against
   48% ($P = 0.006$). One chair call per paper, $\sigma_\eta = 0.59$ (90% range 0.42 to
   0.76), gives 4.6 shared ($P = 0.32$) and 33% rejected ($P = 0.02$).
F. **More reviewers cannot fix the awards.** With infinitely many reviewers the two reviews
   differ only in the chairs' call. From 1,000 to 100,000 submissions this ceiling on the
   overlap falls from 20% to 3.5% for the Best Papers, from 24% to 20% for the Orals and from
   31% to 24% for the Spotlights. To hold each tier's overlap at its 1,000-submission value,
   the Accepted tier needs 4 reviews per paper at every size, the Orals 9.5 and the
   Spotlights 11.4 at 100,000, and the Best Papers 45 at 31,623 and no number above about
   70,000. At 100,000 submissions 16 reviews and 16 independent chair calls give the Best
   Papers an overlap of 7.6%, against 4.1% at 1,000 with 4 reviews and one call.
G. **No assumption that the data leave open changes the conclusions.** Across quality and
   noise variants refitted to the same acceptance data, the chance of Best Papers again at
   NeurIPS 2026 size is 0.17% to 2.7%. On every review form with five or more points and four
   reviews it is 0.32% to 0.37%. In every variant and on every form it falls as submissions grow. Only
   $t_3$ quality moves where the Best Papers usually land (an Oral, 57%), and the NeurIPS
   2021 award decisions reject it (9.4 shared Spotlight or Better papers against 3,
   $P = 0.014$). On ICLR 2021 to 2025 split halves the model predicts the decisions it was
   not fitted to (§7).

The continuous-score derivation (§4, §5):

1. **Constant-number selections degrade as conferences grow; fixed-percentile selections
   do not.** Top-30 precision is 35% at $N = 10^3$, 21% at $10^4$, 13% at $10^5$ and 8.3% at
   $10^6$ (5.5% to 22% at $10^6$). The precision of a top-0.5% set is 24% from $N = 10^4$ on
   (23% at $10^3$, where the set holds five papers). At every $N$, the precision of a top-5%
   set is 40%, of a top-20% set 57%, and of the accept decision at 25% 61%.
2. **The decay is a power law with no floor.** Fixed-$K$ precision behaves as
   $C_K N^{-(1-\rho)/(1+\rho)} (4\pi \log N)^{-\rho/(1+\rho)}$. The exponent is 0.17
   (0.20 pessimistic, 0.08 optimistic). Over $10^3 \le N \le 10^6$ the observed decay of
   top-30 precision is 1.2 to 1.5 times steeper than the exponent at our three levels.
3. **The selected papers are very good, not the best.** The top 30 by score sit at the
   96th true percentile on average at $N = 10^4$ and the 99.3rd at $10^6$. Of them, 41% and
   83% lie in the true top 1%.
4. **Only reliability matters, and it is expensive.** With Gaussian quality and noise the
   noise parameters act only through $\rho^2$. At $N = 20{,}000$, top-30 precision rises from
   18% at $R = 3$ reviews per paper to 41% at $R = 10$ and 69% at $R = 50$. Shared noise
   ($\sigma_u = 0.5$) caps the reliability at 0.85 and holds the values to 34% and 46%.
5. **The tails decide the top.** Power-law ($t_3$) quality makes top-30 precision rise with
   $N$ (58% to 95%). Exponential quality gives a plateau (57% to 57%). Bounded quality or
   heavy-tailed noise make it collapse toward chance. Coarse score scales with random
   tie-breaking turn the top into a lottery at large $N$ (1.6% to 2.6% at $10^6$, against
   8.5% for continuous scores).
6. **The accept/reject boundary is robust and $N$-free.** At 25% acceptance, 39% of the
   papers a review accepts are not in the true top 25%, in every variant (38.4% to 39.6%).
   The number of such papers grows with $N$: at NeurIPS about 160 in 2014 and about 3,050
   in 2026.

## 2. Definitions

**Tiers** (`docs/terminology.md`, `src/peerreview/tiers.py`). Each paper has exactly one
tier; no tier contains another.

| Tier | Meaning | Code key |
|---|---|---|
| Best Papers | the first three papers of the award ordering | `best` |
| Oral | an Oral that is not one of the Best Papers | `oral` |
| Spotlight | a Spotlight, nothing higher | `spot` |
| Accepted | accepted with no award | `accept` |
| Rejected | rejected | `reject` |

Oral or Better (`oral_or_better`) holds the Orals and the Best Papers. Spotlight or Better
(`spot_or_better`) adds the Spotlights. Accepted or Better (`accept_or_better`) holds every
accepted paper. An **award** is any tier above Accepted.

**A second review** reviews the same papers again with new reviewers and chairs. The
**overlap** of a tier is the proportion of one review's tier that the other review also puts
in that tier. **Best Papers again** is the overlap of the two reviews' Best Papers. A
**placement** is the probability that a paper of one tier in the first review gets a given
tier in the second. Every probability for the Best Papers is the mean over the three papers.

`docs/metrics.md` defines the metrics of the continuous-score derivation. The
**precision** of a selection of size $K$ is
$|\mathrm{Top}_K(\bar s) \cap \mathrm{Top}_K(q)|/K$; with a fixed quota, $1 -$ precision is
also the proportion of deserving papers left out. The **swap fraction** is $1 -$ precision
at the acceptance rate. The **disagreement** is
$P(\text{rejected by 2} \mid \text{accepted by 1})$, and the proportion of papers with
inconsistent decisions is $2\alpha$ times the disagreement.

## 3. Model and calibration

**The main model** (`peerreview.model.MAIN_FORM`, `peerreview.levels.main_model`). Each of
$N$ papers has a true quality $q_i \sim \mathcal N(5, 1.2^2)$. Each of its $R = 4$ reviewers
reports the integer from 1 to 10 nearest to $q_i + \varepsilon_{ij}$. The score $\bar s_i$
is the mean of the four reviews. The papers with the top 25% of scores (at a named venue,
its own acceptance rate) are accepted, ties broken at random. Among the papers a review accepts, the award tiers are cut
on the award ordering $\bar s_i + \eta_i$, with the chairs' call
$\eta_i \sim \mathcal N(0, \sigma_\eta^2)$ and $\sigma_\eta = 0.59$
(`results/award_noise.json`). Two counts cut the tiers: $M_{\rm oob}$, the size of Oral or Better
(NeurIPS's Oral count, which includes its Best Papers; series `oral_or_better` in
`results/tier_sizes.csv`, column `M_oral_or_better` in `results/tier_scaling.csv`), and
$M_{\rm spot}$, which counts Spotlights only:

| Award-ordering ranks | Tier |
|---|---|
| 1 to 3 | Best Papers |
| 4 to $M_{\rm oob}$ | Oral |
| $M_{\rm oob} + 1$ to $M_{\rm oob} + M_{\rm spot}$ | Spotlight |
| the rest of the papers the review accepts | Accepted |
| the others | Rejected |

On the $N$ grid both counts follow the NeurIPS fits of item A; at a named venue they are its
own counts. A second review keeps each $q_i$ and redraws every $\varepsilon$ and $\eta$.

**The continuous-score model** of §4 and §5 is $s_{ij} = q_i + u_i + \varepsilon_{ij}$ with
shared noise $u$ (zero unless stated) and reviewer noise $\varepsilon$. The score is the mean
of $R$ unrounded reviews, and the model has no award step. The reliability is
$\rho^2 = \sigma_q^2 / (\sigma_q^2 + \sigma_u^2 + \sigma_\varepsilon^2/R)$, and two
independent reviews' scores correlate at $\rho^2$.

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

**Calibration of each form and variant** (`results/calibration_variants.csv`). Each level
sets a target: the disagreement that continuous scores give at the level's reliability and
NeurIPS 2021's 26.2% acceptance rate. For each form and variant, bisection on
$\sigma_\varepsilon$ meets that target (5,000 papers, 2,000 conference pairs, common random
numbers, tolerance $5 \times 10^{-4}$); the Gaussian shared-noise variants are solved in
closed form. On the integer 1-10 form $\sigma_\varepsilon$ is 2.69, 2.35 and 1.50 at the
pessimistic, central and optimistic levels. 157 of the 158 fits converged; the ICLR 2020
four-point form at the optimistic level has no root in the bracket. On coarse scales the
disagreement is not monotone in $\sigma_\varepsilon$: near-noiseless reviewers put many
papers on the same score, and random tie-breaking then dominates. The five-point scale at
the optimistic level has two roots; the fit takes the one above the minimum. The chairs'
call adds variance to the award ordering only, so two reviews' award orderings correlate at
$\rho_a^2 = 0.45$, against $\rho^2 = 0.50$ for scores.

## 4. Analytical results

`docs/derivations.md` gives the full derivations. Two analysts derived §6 independently;
a reconciler settled every difference by quadrature, exact small-$N$ computation and
simulation. Two adversarial verifiers re-derived the asymptotic law and compared every
function with the simulator. All items are for continuous scores.

| Item | Result |
|---|---|
| Reliability | $\rho^2$ as above; two reviews correlate at $\rho^2$; ceiling $\sigma_q^2/(\sigma_q^2+\sigma_u^2)$ as $R \to \infty$ (0.85 at $\sigma_u = 0.5$). |
| Fixed percentile | $\mathrm{prec}(p) = P_2(z_p, z_p; \rho)/p$, free of $N$; the finite-$N$ deficit is $O(1/K)$ relative. |
| Disagreement | $1 - P_2(z_\alpha, z_\alpha; \rho^2)/\alpha$; inconsistent proportion $= 2\alpha \times$ disagreement; unique inverse. |
| Constant number | exact 2-D integral at finite $N$; $\mathrm{prec}_{N,K} \sim \frac{(1+\rho)^2}{K\sqrt{1-\rho^2}} \big[\frac{\Gamma(K+1/(1+\rho))}{\Gamma(K)}\big]^2 N^{-(1-\rho)/(1+\rho)} (4\pi\log N)^{-\rho/(1+\rho)}$, relative correction $O(\log\log N/\log N)$; checked to $N = 10^{300}$. |
| Mechanism | top scores and the true top-$K$ bar both sit near $\sqrt{2\log N}$; the top scores' quality is $\mathcal N(\rho b_N, 1-\rho^2)$; the gap in SD units grows as $\sqrt{(1-\rho)/(1+\rho)}\sqrt{2\log N}$. |
| Containment | for fixed $K$ and fixed $p$, the proportion of $\mathrm{Top}_K(\bar s)$ in the true top $p$ tends to 1. |
| Two-review top-$K$ overlap | equals fixed-$K$ precision at correlation $\rho^2$; rate $N^{-(1-\rho^2)/(1+\rho^2)}$. |
| Award ordering | for tiers above the acceptance bar, two reviews' award orderings correlate at $\rho_a^2 = \sigma_q^2/(\sigma_q^2+\sigma_\varepsilon^2/R+\sigma_\eta^2)$, 0.45 at the central level. |
| Best Papers | Best Papers again is the two-review overlap of a constant number, $K = 3$, at correlation $\rho_a^2$; rate $N^{-(1-\rho_a^2)/(1+\rho_a^2)}$ up to logarithmic factors, 0.38 at $\rho_a^2 = 0.45$ (0.41 fitted from $10^3$ to $10^5$). The exponent is positive for every $\rho_a^2 < 1$, so the decline has no floor. On the integer 1-10 form the fitted exponent is 0.77, because ever more papers share the top score. |
| Tails | Gaussian/Gaussian decays; exponential/Gaussian plateaus; $t_3$/Gaussian rises to 1; $t_3$/$t_3$ plateaus; bounded/Gaussian and any heavier-noise case collapse. Fixed-percentile precision is $N$-free for every shape. |
| Acceptance rate | wrong accepts per paper $\alpha \cdot \mathrm{swap}(\alpha)$ is zero at $\alpha = 0$ and concave, so its ratio to $\alpha$, the swap fraction, falls as $\alpha$ rises. |
| Discretisation | no closed form (lattice law, ties, bounded top); fixed percentile stays $N$-free; fixed $K$ becomes a lottery in the top tie class, $\mathrm{prec} \approx K/(N\pi_{\rm top})$. |

## 5. Simulation results

Sweeps (a) to (h) of the handoff are in `results/sweep_{a..h}.csv` (one row per
configuration, with seed, replicate count and wall time). They use the continuous-score
model with $R = 3$ ($R = 4$ in sweep e), no award step and no tiers. 10,000 conferences per
setting up to $N = 2 \times 10^4$; above that a budget of $2 \times 10^8$ paper draws, down to
200 at $N = 10^6$ (a budget of $10^9$ draws, 10,000 up to $N = 10^5$ and at least 2,000
conferences for the main sweep g). Analytic and simulated values agree within Monte Carlo
error (`results/verify_analytic.csv`).

**Main sweep** (`sweep_g.csv`, central, precision):

| $N$ | top 5 | top 30 | top 100 | top 0.5% | top 5% | top 20% | accept 25% |
|---|---|---|---|---|---|---|---|
| 1,000 | 22.7% | 35.3% | 47.5% | 22.7% | 39.9% | 57.2% | 60.8% |
| 10,000 | 13.9% | 21.0% | 27.6% | 23.5% | 40.1% | 57.2% | 60.8% |
| 100,000 | 9.0% | 13.0% | 16.7% | 23.6% | 40.1% | 57.2% | 60.8% |
| 1,000,000 | 5.4% | 8.3% | 10.5% | 23.7% | 40.1% | 57.2% | 60.9% |

**Two reviews** (`sweep_g.csv`, central). The top-5 sets of two reviews overlap by 9.8%,
4.1%, 1.8% and 0.8% at $N = 10^3, 10^4, 10^5, 10^6$; the top-30 sets by 19.9%, 8.3%, 3.6%
and 1.5%.

**Reviewer noise and reviewer count** (`sweep_c.csv`, `sweep_b.csv`). At $N = 10^4$ and
$R = 3$, top-30 precision runs from 85% ($\sigma_\varepsilon = 0.25$) to 8.5%
($\sigma_\varepsilon = 3.5$). At $N = 20{,}000$, raising $R$ from 3 to 10 lifts top-30
precision from 18% to 41% without shared noise and to 34% with it. At $R = 50$ the values
are 69% and 46%. The swap fraction at 25% acceptance falls from 39% to 25% (29% with shared
noise) over the same change.

**Quality and noise tails** (`sweep_d.csv`, top-30 precision, $N = 10^3 \to 10^6$, $R = 3$):

| Quality | Gaussian noise | $t_3$ noise |
|---|---|---|
| heavy tail ($t_3$) | 58% → 95% | 50% → 69% |
| exponential tail | 57% → 57% | 49% → 0% |
| lognormal | 45% → 36% | 37% → 0% |
| Gaussian | 35% → 8% | 28% → 0% |
| bounded (Beta) | 31% → 1.5% | 25% → 0% |

Top-1% precision is $N$-free in every row (Gaussian 27.6%, bounded 21.3%, exponential
57.8%, lognormal 41.3%, $t_3$ 67.6% with Gaussian noise). The swap fraction at 25%
acceptance is 38.4% to 39.6% in every cell.

**Score scales** (`sweep_e.csv`, $R = 4$, each recalibrated):

| Scale | top 30, $N=10^4$ | top 30, $N=10^6$ | top 1% | swap at 25% |
|---|---|---|---|---|
| continuous | 21.0% | 8.5% | 27.6% | 39.1% |
| integer 1-10 | 18.5% | 2.6% | 26.0% | 39.1% |
| ICLR {1,3,5,6,8,10} | 17.9% | 1.8% | 25.6% | 39.0% |
| six-point | 18.1% | 1.9% | 25.5% | 39.0% |
| five-point | 19.0% | 1.6% | 26.8% | 39.1% |

Placing the six- and five-point scales on their own range (1 to 6, 1 to 5) with the
latent distribution mapped affinely gives the same numbers within Monte Carlo error, as
it must. Shifting the latent mean by half a scale step changes fixed-$K$ precision at
$N = 10^5$ by up to a factor of three (five-point top 30: 2.9% against 8.2%) and leaves the
swap fraction at 39%. Random tie-breaking is one extreme (a chair with no information);
continuous scores are the other (a chair with full information).

**Acceptance rate** (`sweep_f.csv`, $N = 10^4$): swap fraction 52.4%, 42.8%, 39.2%,
35.9%, 30.1% at $\alpha$ = 10%, 20%, 25%, 30%, 40%; disagreement 67.4%, 51.7% and 40.1% at
10%, 25%, 40%.

## 6. Historical application and the tiers under a second review

**The Best Papers under a second review** (`results/best_paper.csv`, venue rows, `p2_*`
columns; `scripts/run_best_paper.py`; paper Fig. 1c). Main model, 50,000 replays for each
of these three years. NeurIPS's Oral or Better counts (its main-track Orals, Best Papers
included) are 20, 55 and 112, and its Spotlight counts 62, 260 and 292.

| A second review gives one of the Best Papers ... | NeurIPS 2014 ($N$ = 1,678) | NeurIPS 2021 ($N$ = 9,122) | NeurIPS 2026 ($N$ = 30,709) |
|---|---|---|---|
| Best Papers | 2.9% (2.1 to 8.3) | 0.85% (0.55 to 3.5) | 0.33% (0.19 to 1.7) |
| Oral | 10.2% (7.7 to 21.0) | 8.9% (6.3 to 23.2) | 7.0% (4.8 to 21.2) |
| Spotlight | 20.2% (17.1 to 29.5) | 21.3% (17.1 to 34.0) | 10.8% (8.3 to 21.8) |
| Accepted | 44.5% (36.5 to 44.5) | 51.7% (37.3 to 51.7) | 66.5% (53.8 to 66.5) |
| Rejected | 22.2% (4.6 to 29.9) | 17.3% (2.1 to 25.3) | 15.4% (1.4 to 23.4) |
| Spotlight or Better | 33.3% (26.8 to 58.9) | 31.1% (24.0 to 60.6) | 18.1% (13.3 to 44.7) |
| Accepted or Better | 77.8% (70.1 to 95.4) | 82.7% (74.7 to 97.9) | 84.6% (76.6 to 98.6) |
| median rank | 167 (57 to 223) | 748 (195 to 1,063) | 2,289 (523 to 3,342) |

At ICML and ICLR 2026 (23,918 and 19,525 submissions, Oral or Better counts 159 and 224),
the chance of Best Papers again is 0.40% and 0.48%. A second review makes one of the Best
Papers an Oral 10.7% and 15.6% of the time, accepts it 85.0% and 85.4% of the time and
rejects it 15.0% and 14.6% of the time. At ICML it makes it Spotlight or Better 25.2% of the
time.

**The tiers along the submissions axis** (`results/best_paper.csv` grid rows,
`results/placement.csv`; paper Fig. 1d-g). Acceptance is 25% of $N$; the Oral or Better and
Spotlight counts follow item A. Central level:

| | $N$ = 1,000 | $N$ = 10,000 | $N$ = 100,000 |
|---|---|---|---|
| Oral tier, papers | 14 | 62 | 247 |
| Spotlight tier, papers | 48 | 251 | 1,305 |
| Accepted tier, papers | 185 | 2,184 | 23,445 |
| a second review gives one of the Best Papers: Best Papers | 4.1% | 0.83% | 0.12% |
| ... Oral | 11.6% | 9.6% | 5.9% |
| ... Spotlight | 21.9% | 19.3% | 15.7% |
| ... Accepted | 39.0% | 52.7% | 63.6% |
| ... Rejected | 23.4% | 17.6% | 14.7% |
| ... median rank | 107 | 820 | 6,722 |
| overlap: Oral | 8.2% | 6.2% | 3.7% |
| overlap: Spotlight | 14.0% | 10.7% | 8.0% |
| overlap: Accepted | 31.0% | 38.7% | 43.1% |
| overlap: Accepted or Better | 48.3% | 48.4% | 48.4% |

The chance of Best Papers again falls as a power law with exponent 0.77 from $10^3$ to
$10^5$ (0.83 pessimistic, 0.58 optimistic). The Accepted or Better overlap is 44.7%
(pessimistic) and 60.8% (optimistic) at every size. A second review accepts an Oral 67.9%
of the time at 1,000 submissions and 77.7% at 100,000, a Spotlight 57.2% and 68.7%, and an
Accepted paper 44.1% and 47.0%.

**Why the Best Papers fall back.** The first three papers of the award ordering are both
good and lucky. A second review keeps the quality but redraws the luck, so they regress
toward the mean. The second review scores the first review's Best Papers 1.32 SD above its
mean at 1,000 submissions and 1.58 SD at 100,000. The last of its own Best Papers sits 2.46
and 2.96 SD above its mean (`z2_best_papers`, `z2_cut`). Three papers are the top 0.3% of 1,000
submissions but the top 0.003% of 100,000. Two reviews' top 0.3%, a fixed proportion,
overlap by 4.2% at 1,000 and 4.3% at 100,000.

**More reviewers and more chair calls** (`results/R_needed_tiers_curve.csv`,
`results/chair_calls.csv`; paper Fig. 4, Table 1). With infinitely many reviewers the
overlap falls from 1,000 to 100,000 submissions: Best Papers 20.3% to 3.5%, Oral 24.2% to
20.0%, Spotlight 30.5% to 23.8%; Accepted rises from 83.3% to 95.5%. The reviews per paper
that hold each tier's overlap at its value for 1,000 submissions and four reviews:

| Tier (target) | $N$ = 10,000 | $N$ = 31,623 | $N$ = 100,000 |
|---|---|---|---|
| Accepted (31.0%) | 4.0 | 4.0 | 4.0 |
| Spotlight (14.0%) | 7.1 | 9.0 | 11.4 |
| Oral (8.2%) | 5.8 | 7.3 | 9.5 |
| Best Papers (4.1%) | 15.6 | 44.8 | none above 69,666 |

Overlap of two reviews' Best Papers at 100,000 submissions, with $R$ reviews per paper and
the average of $k$ independent chair calls ($k = 1$ is the main model; $k = \infty$ gives
awards by score alone):

| $R$ | $k = 1$ | $k = 2$ | $k = 4$ | $k = 16$ | $k = \infty$ |
|---|---|---|---|---|---|
| 4 | 0.1% | 0.2% | 0.2% | 0.3% | 0.3% |
| 16 | 1.2% | 2.5% | 4.2% | 7.6% | 9.7% |

**How sure: the Best Papers under every variant** (`results/best_paper_robustness.csv`,
`scripts/run_best_paper_robustness.py`, paper Fig. 5; the 2021 column from
`results/validation_neurips2021.csv`). Each variant is refitted to the central NeurIPS 2021
disagreement and simulated with two independent reviews at NeurIPS 2014 size (200,000
conferences) and 2026 size (40,000). Careless reviews ignore the paper: a "rave" review gives
10, a "random" review a uniform score on the 1-10 scale (`ReviewModel.careless`,
`careless_kind`). The 2021 column replays the NeurIPS 2021 award decisions (4,000 replays;
3 shared Spotlight or Better papers observed). At 2026 size (2014 in brackets):

| Variant | Best Papers again | Oral | Accepted | Rejected | median rank | 2021 shared: mean, $P(\le 3)$ |
|---|---|---|---|---|---|---|
| main model | 0.35% (2.9%) | 7.1% | 66.1% | 15.4% (22.1%) | 2,262 | 4.6, 0.32 |
| bounded quality | 0.17% (1.8%) | 4.0% | 67.5% | 20.6% (26.6%) | 3,253 | 4.0, 0.43 |
| exponential quality | 0.78% (9.4%) | 20.4% | 48.2% | 2.5% (4.9%) | 417 | 9.4, 0.014 |
| lognormal quality | 0.78% (6.3%) | 14.9% | 58.1% | 7.6% (13.0%) | 904 | 6.3, 0.11 |
| $t_3$ quality | 2.7% (28.0%) | 56.9% | 11.2% | 0.17% (1.4%) | 84 | 9.4, 0.014 |
| $t_3$ noise | 0.51% (3.5%) | 8.6% | 63.5% | 15.4% (22.0%) | 2,048 | 4.7, 0.31 |
| shared noise ($\sigma_u = 0.5$) | 0.34% (3.0%) | 7.0% | 66.1% | 15.3% (21.8%) | 2,242 | 4.7, 0.32 |
| 1% rave reviews | 0.36% (3.0%) | 7.1% | 66.3% | 15.3% (22.1%) | 2,251 | 4.6, 0.33 |
| 5% rave reviews | 0.36% (3.0%) | 7.2% | 64.6% | 16.7% (22.7%) | 2,307 | 4.6, 0.32 |
| 5% random reviews | 0.45% (3.2%) | 7.8% | 65.7% | 14.4% (21.4%) | 2,121 | 4.6, 0.31 |

Every variant gives Best Papers again less often at 2026 size than at 2014 size. Changes to
the noise change no number by more than the calibration levels already do, because each
variant is refitted to the same disagreement. Only the shape of quality moves where the Best
Papers land. Under lognormal quality they are still most often Accepted. Under exponential
quality they are Accepted less than half the time and rarely rejected. Under $t_3$ quality a
second review usually makes them Orals, yet only 2.7% are Best Papers again. Exponential and
$t_3$ quality predict 9.4 shared NeurIPS 2021 Spotlight or Better papers against 3 observed
($P = 0.014$), so the 2021 award decisions reject them.

**How sure: the review form** (`results/scale_impact.csv`, `scripts/run_scale_impact.py`,
paper Fig. 6). Each form is recalibrated to the central disagreement. At 2026 size (2014 in
brackets):

| Form | Best Papers again | Oral | Rejected |
|---|---|---|---|
| integer 1-10, 4 reviews (main form) | 0.33% (2.9%) | 7.1% | 15.4% (22.0%) |
| integer 1-10, 3 reviews | 0.28% (3.1%) | 7.1% | 15.4% (21.6%) |
| six-point, 4 reviews | 0.37% (2.9%) | 7.0% | 15.3% (21.7%) |
| six-point, 3 reviews | 0.28% (3.0%) | 7.0% | 15.5% (21.7%) |
| five-point, 4 reviews | 0.33% (3.1%) | 7.4% | 14.9% (21.3%) |
| ICLR 1/3/5/6/8/10, 4 reviews | 0.32% (2.9%) | 6.9% | 15.7% (22.0%) |
| ICLR 0/2/4/6/8/10, 4 reviews | 0.35% (3.0%) | 7.2% | 15.2% (21.7%) |
| ICLR 1/3/6/8, 3 reviews | 0.06% (1.1%) | 2.1% | 29.2% (31.7%) |
| continuous, 4 reviews | 1.5% (4.7%) | 13.9% | 8.5% (18.0%) |

Every form with five or more points gives the main form's numbers almost exactly. Ties
explain the two outliers. The four-point scale's top point, 8, takes every judgement of 7 or
more, so many papers get it from all three reviewers, and the chairs' call alone picks the
Best Papers among them. Continuous scores never tie, so the chairs' call must overcome real
differences in score. From $10^3$ to $10^5$ the integer 1-10, six-point and ICLR
1/3/5/6/8/10 forms give exponents 0.75 to 0.77; continuous scores give 0.41.

**Venue-years in the continuous-score model** (`results/history.csv`). The continuous-score
model at each venue-year's submissions, acceptance rate and Oral or Better count (values
from `data/venues.csv`, `*_used` columns):

| Venue-year | $N$ | top-30 precision | Oral or Better precision (count) | wrong accepts | disagreement |
|---|---|---|---|---|---|
| NeurIPS 2014 | 1,678 | 31.4% | 28.6% (20) | 163 | 52.0% |
| NeurIPS 2020 | 9,467 | 21.2% | 28.2% (105) | 812 | 56.1% |
| NeurIPS 2025 | 21,575 | 17.8% | 21.9% (77) | 2,088 | 52.1% |
| NeurIPS 2026 | 30,709 | 16.5% | 22.1% (112) | 3,052 | 51.1% |
| ICML 2026 | 23,918 | 17.3% | 25.2% (159) | 2,421 | 50.3% |
| ICLR 2026 (valid) | 19,525 | 18.4% | 28.4% (224) | 2,008 | 49.7% |

The CSV also holds top-5 precision (`prec_K5`) and the two-review overlap of the Oral or
Better set (`ovl_oral_or_better`) for every year and level. No figure draws these.

## 7. Validation

**NeurIPS 2021 award decisions** (`results/validation_neurips2021.csv`). Among the 764
decided papers, the two committees' Spotlight or Better sets held 29 and 25 papers and shared
3. The experiment had no Best Papers tier, so its Orals plus Spotlights are its Spotlight or
Better set. Of these 54 award papers, counted from each side, the other committee rejected
26 (48%), all of them Spotlights: 26 of the 48 Spotlights (54%). All six Orals became
Posters. The replay treats the 764 papers as a subsample of a 7,902-paper conference
reviewed twice, at the central level:

| Variant | Spotlight or Better shared (90% range) | $P(\le 3)$ | Spotlight or Better rejected | $P(\ge 48\%)$ | Spotlights rejected | $P(\ge 54\%)$ |
|---|---|---|---|---|---|---|
| main model ($\sigma_\eta = 0.59$) | 4.6 (2 to 8) | 0.32 | 33% | 0.020 | 35% | 0.005 |
| no award step ($\sigma_\eta = 0$) | 5.6 (2 to 10) | 0.18 | 30% | 0.006 | 32% | 0.002 |
| shared noise | 4.7 (2 to 8) | 0.32 | 33% | 0.015 | 35% | 0.004 |
| $t_3$ noise | 4.7 (1 to 9) | 0.31 | 34% | 0.018 | 35% | 0.005 |
| bounded quality | 4.0 (1 to 8) | 0.43 | 35% | 0.034 | 37% | 0.009 |
| bounded quality, $t_3$ noise | 4.1 (1 to 8) | 0.42 | 35% | 0.033 | 37% | 0.008 |
| lognormal quality | 6.3 (3 to 11) | 0.11 | 28% | 0.002 | 30% | 0.001 |
| exponential quality | 9.4 (5 to 14) | 0.014 | 19% | < 0.001 | 21% | < 0.001 |
| $t_3$ quality | 9.4 (5 to 14) | 0.014 | 23% | < 0.001 | 26% | < 0.001 |

The three careless-review variants match the main model (4.6 shared, $P = 0.31$ to 0.33).
At the pessimistic level the main model rejects 40% of the other review's Spotlight or Better
papers ($P = 0.12$) and 41% of its Spotlights ($P = 0.04$). The optimistic level fails in
every variant. In every variant the rejected share stays below the observed 48%, so the
model, if anything, overstates how reproducible awards are.

**The chairs' call** (`scripts/fit_award_noise.py`, `results/award_noise.json`). A
language-model reading of the 50 award pairs' public records found the reasons for each
split (`docs/neurips2021_stage2_results.md`; paper Appendix D). The fit uses a statistic
that sees one committee at a time: how many of its awards lie among its own $K$ top-scored
papers, $K$ being its number of awards. Observed, it is 26.2 of 53 (53 of 53 at
$\sigma_\eta = 0$). Bisection gives $\sigma_\eta = 0.59$; 200 bootstrap resamples of the
pairs give the 90% range 0.42 to 0.76. On the real scores the fitted call predicts 3.6
papers in both award sets (3 observed, 5.9 at $\sigma_\eta = 0$) and 22.4 of the 53 award
copies rejected by the other committee (25 observed, 20.5 at $\sigma_\eta = 0$).

**ICLR split halves** (`results/iclr_splithalf_observed.csv`, `results/validation_iclr.csv`).
Main-track decided papers with at least four reviews, 200 random splits into two halves
of two reviews. A half has no chairs, so the model has no award step here. The model uses
each year's scale, $R = 2$ per half, latent quality at the year's observed mean and
between-paper SD (`placement = observed`), and reviewer noise fitted to the half-mean
correlation (0.49 to 0.55 in 2021 to 2025). Without further fitting the model gives
inconsistency 29% to 33% (observed 29% to 32%) and an Accepted or Better overlap of 54% to
63% (observed 55% to 65%). The top-30 and top-three overlaps hold a handful of papers each
and scatter on both sides of the model: top-30 observed 5% to 23% against 7% to 17% in the
model, top-three observed 1% to 22% against 2% to 6%. Over the splits the observed top-30
overlap has an SD of 3 to 5 points and the top-three overlap 7 to 16 points. The halves
share the area chair and the rebuttal, so this test favours consistency.

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
   `scripts/build_venues_used.py`, `docs/claims.md`). Oral or Better counts are main
   track only (NeurIPS 2025: 77, not 87). NeurIPS 2026 has no primary source yet.
5. **The NeurIPS 2014 choice.** The raw table (0.53) is the right inversion; the quoted
   version (0.44), which applies the inconsistency rate to the wrong acceptance rate,
   serves as the pessimistic bound because it is the lowest point estimate in common use.
6. **Venue-years below $N = 1{,}000$** (ICLR 2017 and 2018) are not tabulated. Fig. 1a
   of the paper still plots their submission counts.
7. **Paper title, template and framing (2 October 2026).** At the author's request the
   title is "Scaling Laws of Machine Learning Conference Peer Review", and the paper uses the
   NeurIPS 2026 style with its `preprint` option (not a submission). The paper is framed
   around the two jobs of review: accepting good papers (a fixed proportion of submissions)
   and giving awards to the best (Spotlights, Orals and Best Papers). Award tiers grow more
   slowly than submissions. At real Oral or Better counts the continuous-score model's
   precision lies between the two limits, fixed proportion and constant number
   (`results/history.csv`, `prec_oral_or_better`, central: NeurIPS 28.6% to 22.1%, ICML
   35.5% to 25.2%, ICLR 30.1% to 28.4%). NeurIPS submissions grew 26% a year from 2014 to
   2025. The abstract's decade growth rates come from `N_used`: NeurIPS 2,403 to 30,709 over
   2016 to 2026 is 29.0% a year, ICML 1,320 to 23,918 is 33.6%, and ICLR 507 to 19,525 over
   2017 to 2026 is 50.0%. Decisions 10 and 14 later changed Fig. 1.
8. **Stated takeaways (2 October 2026).** The author asked for the key takeaways to be
   stated and emphasised. Results paragraphs open with a bold takeaway sentence, and Results
   end with implications for program chairs.
9. **Bounded heavy-tailed variants.** Two $t_3$-noise variants on a 1-10 scale joined the
   calibration and the NeurIPS 2021 replay (rows `gauss/t3` and `beta/t3`). Neither reaches
   the observed rejected share (§7).
10. **Restructure around one question (3 October 2026).** At the author's request the
    paper asks one question: as submissions grow, can review still tell good papers from
    bad ones and give its awards to the right papers? The answers are the probabilities of
    each tier that a second review gives the Best Papers (Best Papers again, Oral,
    Spotlight, Accepted, Rejected; `docs/terminology.md`). Each section and paragraph runs
    motivation, method, result, implication. Spotlight counts are in `data/spotlights.csv`
    (`docs/claims.md` §10.4a). The careless-review variants and the per-variant 2021 replay
    were added for this; the three careless variants are calibrated at the central level
    only. The Limitations paragraph went into the opening of the Implications.
11. **Real venues use their observed counts (4 October 2026).** At a venue-year the Oral or
    Better set has the venue's own main-track count, Best Papers included (`data/venues.csv`,
    `orals_used`; NeurIPS 20 in 2014, 55 in 2021, 112 in 2026), and the Spotlight tier its own
    Spotlight count. The model assumes no rule for these counts. NeurIPS's Oral or Better count grew
    roughly as $N^{0.6}$, between a constant number and a fixed proportion. Decision 13 sizes
    the tiers along the $N$ grid.
12. **Rerun framing throughout (4 October 2026).** At the author's decision the report gives
    every probability for the Best Papers in the units of the NeurIPS consistency
    experiments: the tier that a second, independent review gives them (`p2_*` columns of
    `results/best_paper.csv`). The true-rank framing compares one review with a noiseless
    oracle, which no experiment observes, so the report no longer gives it. The mechanism
    follows suit: two-review overlap replaces precision. The gap is the second review's score
    for the first review's Best Papers against the score of the last of its own Best Papers
    (`z2_best_papers`, `z2_cut`; §6). The reviews needed to hold each tier's overlap are in
    `results/R_needed_tiers_curve.csv` (§6). A second review rejects one of NeurIPS 2026's
    Best Papers 15% of the time (1.4% to 23%).

13. **Tier sizes along the submissions axis follow NeurIPS's own trends (4 October 2026).**
    The grid had no Oral or Spotlight count, so `scripts/make_tier_scaling.py` fits each
    NeurIPS count to a power law in $N$ (log-log least squares, 2014-2026;
    `results/tier_sizes.csv`): Oral or Better $0.30\,N^{0.59}$, Spotlight $0.34\,N^{0.72}$, and
    the Oral tier alone $0.18\,N^{0.63}$ (2014-2025).
    Acceptance stays at 25% of $N$, and the Best Papers are three at every $N$ (decision 18).
    The current curves come from the main model (`results/best_paper.csv` grid rows,
    `results/placement.csv`; §6). `results/tier_scaling.csv` holds the continuous-score closed
    form on the same grid.

14. **Fig. 1 tiers and their fitted trends (10 October 2026).** At the author's request
    Fig. 1 shows (a) submissions, (b) the NeurIPS counts and (c) the tier a second review
    gives the NeurIPS Best Papers (stacked bars). The author's motivation for (b): show how
    to think about the tiers. Is each a constant number, a proportion of submissions, or
    something between? So (b) draws each year's proportion as markers and the fitted power
    law $aN^\gamma$ as a line, labelled with $\gamma$ (`results/tier_sizes.csv`): Accepted or
    Better 1.05, Spotlight 0.72, Oral or Better 0.59. The Best Papers ($\gamma = 0.27$, 1 to
    13 a year) are too few to draw. $\gamma = 1$ is a fixed proportion, $\gamma = 0$ a
    constant number. The $N$ grid keeps $0.25\,N$ for acceptance. On 17 October 2026 Fig. 1
    gained the scaling row (d-g).

15. **One vocabulary (10 October 2026).** At the author's decision (`docs/terminology.md`)
    every tier is named by the decision itself. "Award" is the one umbrella for Spotlight,
    Oral and Best Papers ("highlights" is gone). The model's second run is "a second review",
    never "a second committee", which read as an award committee. The tiers a second review
    gives gained the Spotlight (`p2_spot`, from `data/spotlights.csv`). Decisions 18 and 19
    set the current tier definitions.

16. **One real review form for the main results (10 October 2026).** The author asked that the
    model use real score scales rather than continuous scores, and then that the bulk of the
    paper use one form, the most defensible, with the other scales tested in a later section.
    The main form is integer 1 to 10 scores with four reviews per paper
    (`peerreview.model.MAIN_FORM`): the NeurIPS scale of 2014 to 2024, the most common across
    venues, and the form of the NeurIPS 2021 experiment that calibrates the model. Every
    main-text probability is simulated on it (`scripts/run_best_paper.py`; the analytic table
    remains as `results/best_paper_continuous.csv`). Reviewer noise is recalibrated per form
    and variant (`run_calibration.py --forms-only`). The forms in use are recorded in
    `data/review_forms.csv` and compared in `results/scale_impact.csv`
    (`run_scale_impact.py`). The NeurIPS 2014, 2021 and 2026 rows use 50,000 replays
    (`run_best_paper.py --cited --reps 50000`). `run_best_paper_hirep.py` re-simulates every
    `p2_*` (all cuts and the separate tiers) of the grid rows and of ICML and ICLR 2026 with more
    replays, in chunks of 10,000 (120,000 for the central grid above 10K submissions). Other
    venue-years use 10,000. §6 gives the current
    numbers: on every form with five or more points and four reviews, Best Papers again at
    NeurIPS 2026 size is 0.32% to 0.37%; ICLR 2020's four points with three reviews give
    0.06% and reject the Best Papers 29% of the time; continuous scores give 1.5% and 8.5%.

17. **An award step: awards are a chair's call (14 October 2026).** Without it the model
    over-predicted the NeurIPS 2021 committees' award agreement: 5.6 shared Spotlight or
    Better papers against 3 observed, and 30% of them rejected by the other review against
    48% ($P = 0.006$). A two-stage language-model reading of the 50 award pairs' public
    records (`data/paired_reviews/neurips2021/analysis/`,
    `docs/neurips2021_stage2_results.md`) found that the award tier came from the
    meta-review rather than the scores in most pairs: the higher tier with no stated grounds
    in 30 of 50, stated weaknesses dropped in 33, the area chair's own judgement in 20. The
    model now cuts the award tiers (Best Papers, Oral, Spotlight) on an award ordering, the
    score plus a chair noise $\eta \sim \mathcal N(0, \sigma_\eta^2)$ among the papers a
    review accepts, redrawn by a second review. Acceptance stays by score
    (`peerreview.model.award_order`, `ReviewModel.sigma_award`, `levels.main_model`).
    $\sigma_\eta = 0.59$ on the 1-10 axis, fitted so that the model's awards fall inside each
    committee's score top-$K$ as often as the real ones (26 of 53;
    `scripts/fit_award_noise.py`, `results/award_noise.json`, bootstrap 90% range 0.42 to
    0.76). Held out: 4.6 shared ($P = 0.32$) and 33% rejected ($P = 0.02$). The award
    orderings of two reviews correlate at $\rho_a^2 = 0.45$, against $\rho^2 = 0.50$ for
    scores. Every simulated result was rerun with the step (`scripts/run_all.sh`).

18. **Best Papers are the top three (17 October 2026).** At the author's decision the Best
    Papers are the first three papers of the award ordering at every $N$, a constant number.
    NeurIPS named 1 to 13 main-track Best Papers a year from 2014 to 2025 (median 2.5, mean
    3.5) and 1 to 15 across all tracks (median 3, mean 4.2; `data/neurips_best_papers.csv`);
    three lies between. The name is always plural. No single #1 paper and no top ten remain
    in the paper, the figures or the code the paper reads. The number of Best Papers changes
    the chance of Best Papers again but not its rate: the exponents are 0.78, 0.77 and 0.75
    for two, three and four Best Papers (`results/best_paper_size.csv`).

19. **Separate tiers (18 October 2026).** At the author's decision the tiers are separate,
    like gold, silver and bronze: Best Papers, Oral, Spotlight, Accepted (accepted with no
    award) and Rejected. Each paper has exactly one. A tier together with every tier above it
    is named in full: Oral or Better, Spotlight or Better, Accepted or Better. The code keys
    are `best`, `oral`, `spot`, `accept` and `reject`; a set ends in `_or_better`
    (`src/peerreview/tiers.py`). The simulator counts the overlap and placement of each
    separate tier directly (`results/placement.csv`). From 1,000 to 100,000 submissions an
    Oral keeps its tier 8.2% to 3.7% of the time and a Spotlight 14.0% to 8.0% (§6).

## 9. Limitations

One-dimensional quality; exchangeable reviewers (no leniency offsets, no matching); the
chairs' call as one Gaussian draw per accepted paper, independent of quality; no rebuttal,
discussion, strategic behaviour, desk rejection or withdrawal; acceptance by mean score
alone. The calibration rests on two experiments of 166 and 764 decided papers, whose
sampling error spans much of the range between our pessimistic and optimistic levels. The
chairs' call rests on the 50 award pairs of one experiment. Accept-level data do not
identify the tail of the quality distribution, which decides the results at the top; the
NeurIPS 2021 award decisions reject exponential and $t_3$ quality. The heavy-tailed-noise
results of §5 use unbounded $t_3$ noise. On the main form, $t_3$ noise changes Best Papers
again at NeurIPS 2026 size only from 0.35% to 0.51% (§6).
