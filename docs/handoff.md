# Handoff: Scaling Laws of ML Conference Peer Review

This file is the specification that this repository implements. Rylan pasted it on
2026-10-02. It is kept verbatim except for two changes. First, the body of §8.1 was missing
from the paste; the reconstruction of §8.1 below is marked as such. Second, on 2026-10-18 the
tier words were made explicit (`docs/terminology.md`). The tiers are separate. A set that holds
a tier and every tier above it is named in full: Oral or Better, Spotlight or Better, Accepted
or Better. No other content changed.

**Purpose of this document.** It specifies a study to be reproduced from scratch in a clean session: the motivation, the probabilistic models, the quantities to compute, the analytical derivations to carry out, the calibration and validation procedures, the simulation protocol, and the empirical facts the study relies on, each with its source and verification status.

**What is deliberately left out.** No simulation results, no fitted parameter values, no derived formulas or asymptotic rates, no figures, and no scientific conclusions. Where a quantity was computed in the earlier work, this document says *what* to compute and *how*, not what came out. The new session should derive, simulate, visualise and interpret everything itself.

---

## 1. Motivation and research questions

Machine-learning conferences have grown by more than an order of magnitude in a decade (submission counts in §10.4) while keeping essentially the same review process: each paper receives a handful of reviews, each review carries an overall score on a short ordinal scale, papers are ranked largely by their mean score, and an area chair (AC) and senior area chair (SAC) layer calibrates and makes the final call. Acceptance rates have stayed in a narrow band, so the number of accepted papers has grown with the number of submissions. The number of best-paper awards has not grown; the number of orals has grown but slower than submissions.

Two field experiments (NeurIPS 2014 and NeurIPS 2021, §10.1) sent the same papers to two independent committees and measured how often they disagreed. Those experiments measure consistency at the accept/reject boundary. They say little about the top of the ranking, which is what awards, orals and spotlights select.

**The question.** How does the quality of a conference's selections change as the number of submissions $N$ grows, holding the review process fixed, and which parameters of the review system determine that quality? The specific objects of interest are:

1. **The top of the ranking.** When a conference picks the $K$ highest-scoring papers for best-paper awards ($K$ of order 1 to 10) or the top $K$ for oral presentations (Oral or Better; $K$ of order 30 to 100 or more), what fraction of them are truly among the best $K$? How does that fraction depend on $N$, on review noise, on the number of reviews per paper, on the score scale, and on the shape of the quality distribution? The working hypothesis to test: as $N$ grows with noise held fixed, noise comes to dominate the extreme upper tail of scores, so the number of truly best papers among the top $K$ by score tends to zero.
2. **The accept/reject boundary.** How many rejected papers deserved acceptance, and how many accepted papers did not, as a share and as a count, and how do these scale with $N$?

**Two selection rules.** Every decision a conference makes is one of two kinds, and they should be analysed separately throughout:

- **Fixed number.** Select the top $K$ by score with $K$ held constant as $N$ grows (best-paper awards; a fixed number of talk slots).
- **Fixed percentile.** Select the top fraction $p$ of submissions (acceptance at a rate of roughly 20 to 40 percent; Oral or Better, or Spotlight or Better, defined as a percentage of submissions, typically 0.3 to 3 percent).

Treat these as the two cases. Do not introduce a third. The Best Papers are a fixed number; Oral or Better and acceptances are a fixed percentile (though the oral *count* at a given venue-year, the size of Oral or Better, can also be analysed as a fixed-number selection of that size).

**Range of $N$.** Analyse $N$ from 1,000 to 1,000,000. Do not plot or tabulate below 1,000 or above 1,000,000.

---

## 2. Deliverables

1. **Metrics first.** Define precisely what "the best papers" and "wrong decisions" mean before modelling (§4).
2. **A faithful generative model** of the review pipeline (§3), calibrated to what NeurIPS, ICML and ICLR actually do (§7, §10).
3. **Analytical solutions where possible** (§6), verified against simulation.
4. **Simulations** with on the order of 10,000 simulated conferences per parameter setting where feasible (§9), showing how each metric scales with $N$ and with the other parameters.
5. **A report** of the findings, and a **LaTeX paper**:
   - Title: *Scaling Laws of ML Conference Peer Review*. Author: Rylan Schaeffer.
   - The abstract must state that the goal was to study how the quality of ML conference peer review changes as conferences grow, and to understand how the parameters of the review system affect that quality.
   - Sections: introduction, methods, results. Length 4 to 6 pages.
   - The main takeaway figure goes at the top of page 2 or the bottom of page 1. Every page after that carries one large figure communicating one insight.
   - Every caption starts with ONE bold sentence stating the number-one takeaway of the figure; the rest of the caption then rewinds to explain what is plotted, what the results are, and why they matter.
   - The introduction presents the motivation, then the axes of consideration (number of submissions, noise model, reviewers per paper, scoring function and its discretisation, quality distribution, acceptance rate), then the headline conclusions stacked in order of importance.
   - Style: concrete, plain, logical. Each sentence must justify its existence. No filler.
6. **A list of the empirical claims used**, with sources, so they can be checked.

---

## 3. Probabilistic models

All models live on a latent 1 to 10 quality axis to match the historical NeurIPS and ICLR scales.

### 3.1 Base model (Gaussian signal plus noise)

A conference receives $N$ papers. Paper $i$ has a true quality $q_i$ and receives $R$ reviews. Review $j$ of paper $i$ is

$$s_{ij} = q_i + u_i + \varepsilon_{ij},$$

with

- $q_i \sim \mathcal{N}(\mu_q, \sigma_q^2)$ independently across papers. Defaults: $\mu_q = 5$, $\sigma_q = 1.2$. (Rationale for $\sigma_q$: the between-paper standard deviation of mean ratings at ICLR is about 1.25 to 1.33 on the 10-point scale and the between-paper component of individual scores is about 1.0 to 1.2; see §10.2. Treat $\sigma_q$ as a scale choice and check which results depend on it.)
- $\varepsilon_{ij} \sim \mathcal{N}(0, \sigma_\varepsilon^2)$ independently across reviewers and papers: a reviewer's idiosyncratic error.
- $u_i \sim \mathcal{N}(0, \sigma_u^2)$ independently across papers: noise shared by everyone who handles paper $i$ (the AC's judgement, presentation quality, topical fashion, anything all reviewers see alike). It does not average out with more reviewers. The base model sets $\sigma_u = 0$; the shared-noise variant uses $\sigma_u = 0.5$ (so that $\sigma_u^2/\sigma_q^2 \approx 0.17$).

The paper's **score** is the mean of its $R$ reviews, $\bar s_i = R^{-1}\sum_j s_{ij}$. Papers are ranked by score. Ties are broken uniformly at random (relevant only when scores are discretised).

**Reliability.** Define $\rho$ as the correlation between a paper's score $\bar s_i$ and its true quality $q_i$, and $\rho^2$ as the reliability of the score. Express $\rho^2$ in terms of $\sigma_q, \sigma_\varepsilon, R, \sigma_u$, and determine which metrics in §4 depend on the noise parameters only through $\rho^2$ (so that reviewer noise, reviewer count and shared noise can be reported on a common axis) and which do not.

**Two independent committees.** To reproduce the field experiments, simulate a second committee that sees the same papers (same $q_i$) but redraws both $u_i$ and all $\varepsilon_{ij}$, then applies the same decision rule. Whether $u_i$ should be redrawn for the second committee is a modelling choice to state explicitly (the experiments used disjoint ACs and reviewers, so the earlier work redrew it).

### 3.2 Discretised scores

Reviewers do not submit continuous numbers. In the discretised variants each latent review $s_{ij}$ is snapped to the nearest point of a score scale **before** averaging; the paper's score is the mean of the snapped reviews; ties are broken at random. Scales to study, each placed on the latent 1 to 10 axis:

| Scale | Points on the latent axis | Used by |
|---|---|---|
| continuous | none (reference) | the idealised model |
| integer 1 to 10 | 1, 2, ..., 10 | NeurIPS through 2024; ICML 2023 to 2024; ICLR 2017 to 2019 and 2021 |
| six-point | 6 equally spaced points from 1 to 10 (stand-in for the 1 to 6 scale) | NeurIPS 2025 to 2026; ICML 2026 |
| ICLR six-point | 1, 3, 5, 6, 8, 10 | ICLR 2022 to 2025 |
| five-point | 5 equally spaced points from 1 to 10 (stand-in for the 1 to 5 scale) | ICML 2025 |

Report the effect of each scale separately, for both selection rules, as a function of $N$. Use $R = 4$ for the discretisation study (current practice is four assigned reviewers with at least three required). Because snapping changes the effective noise, **recalibrate** $\sigma_\varepsilon$ separately for each scale to the same empirical target (§7.3) before comparing scales, so that every variant is equally consistent with the data. State clearly that random tie-breaking is one extreme (an AC who resolves ties with no information) and continuous scores are the other (an AC who resolves ties with full information). Placing a coarse scale on the 1 to 10 latent axis is itself a choice; note the alternative (model the latent axis on the scale's own range) and check whether it matters.

### 3.3 Alternative quality distributions (tail shape)

Keep the mean and standard deviation of $q$ fixed at $\mu_q, \sigma_q$ and vary the shape:

- **Gaussian** (base).
- **Bounded:** symmetric Beta$(a,a)$ stretched to $[1,10]$ with $a$ chosen so the standard deviation equals $\sigma_q$ (SD of $9\,\mathrm{Beta}(a,a)$ is $4.5/\sqrt{2a+1}$), then shifted so the mean is $\mu_q$.
- **Exponential right tail:** $q = \mu_q - \sigma_q + \sigma_q E$, $E \sim \mathrm{Exp}(1)$.
- **Heavy tail:** $q = \mu_q + \sigma_q\, T_3/\sqrt{3}$, $T_3 \sim$ Student-$t$ with 3 degrees of freedom.
- Optionally **lognormal** with matched mean and SD.

### 3.4 Alternative noise distribution

Replace Gaussian reviewer error by Student-$t_3$ rescaled to the same standard deviation, $\varepsilon = \sigma_\varepsilon T_3/\sqrt{3}$.

### 3.5 Combined variants for validation

For the Spotlight or Better validation (§8.1) compare at least these six variants, each separately calibrated (§7.3): Gaussian quality with Gaussian noise; Gaussian quality with Gaussian noise plus shared noise; Gaussian quality with $t_3$ noise; bounded quality with Gaussian noise; bounded quality with $t_3$ noise; exponential-tail quality with Gaussian noise.

### 3.6 What the model omits (state these as limitations)

One-dimensional quality; exchangeable reviewers (no reviewer leniency offsets, no reviewer-paper matching); the AC appears only as shared noise; no rebuttal or discussion dynamics; no strategic behaviour; no desk rejections or withdrawals; decisions by mean score alone, whereas real venues add AC/SAC calibration (§10.5).

---

## 4. Selection rules and metrics

Let $A = \mathrm{round}(\alpha N)$ be the number of accepted papers at acceptance rate $\alpha$. Let $\mathrm{Top}_K(x)$ denote the set of the $K$ papers with the largest values of $x$.

**Fixed-number selection** at size $K$: the selected set is $\mathrm{Top}_K(\bar s)$. **Fixed-percentile selection** at fraction $p$: the selected set is $\mathrm{Top}_{\mathrm{round}(pN)}(\bar s)$. Acceptance is the fixed-percentile rule with $p = \alpha$.

Metrics for the top of the ranking (Question 1):

1. **Precision** of the selected set: the share of selected papers whose true quality rank is within the size of the set, $|\mathrm{Top}_K(\bar s)\cap\mathrm{Top}_K(q)|/K$ (and the same with $K = \mathrm{round}(pN)$). This is the headline metric. Note that with a fixed quota, every undeserving paper selected displaces exactly one deserving paper, so $1 - \text{precision}$ is also the share of deserving papers left out.
2. **Looser containment:** the share of $\mathrm{Top}_K(\bar s)$ that lies in the true top $M$ for $M = 2K, 10K$, and in the true top 1 percent, top 5 percent and top $\alpha$ fraction. This measures whether the selected papers are at least "very good" when they are not "the best".
3. **Best paper:** the probability that the single truly best submission is in $\mathrm{Top}_K(\bar s)$, for $K = 1, 5, 10, 30$.
4. **Rank of the winner:** the median (and distribution of the) true rank of the top-scored paper, and the mean true percentile of the top-$K$ set.
5. **Two-committee overlap:** $|\mathrm{Top}_K(\bar s^{(1)})\cap\mathrm{Top}_K(\bar s^{(2)})|/K$ for two independent committees. This is observable in field data and does not require knowing $q$.

Metrics for the accept/reject boundary (Question 2):

6. **Swap fraction:** the share of accepted papers not in $\mathrm{Top}_A(q)$, which equals the share of deserving papers that were rejected. The **count** of wrong accepts is the swap fraction times $A$.
7. **Two-committee disagreement:** $P(\text{rejected by committee 2}\mid\text{accepted by committee 1})$, the quantity the NeurIPS experiments report as "the fraction of accepted papers that would be rejected on a rerun". Also the **share of all papers with inconsistent decisions** (accepted by exactly one committee), which the experiments also report. Derive the relation between the two at acceptance rate $\alpha$ (both committees accept $\alpha N$ papers).

Sizes to report: $K \in \{5, 10, 30\}$ and, where the question is Oral or Better, $K$ around 100 and $K$ equal to each venue-year's actual oral count; $p \in \{0.3\%, 0.5\%, 1\%, 5\%\}$ for Oral or Better and Spotlight or Better and $\alpha \in \{0.10, 0.15, 0.20, 0.25, 0.30, 0.35, 0.40\}$ for acceptance, with 20 to 25 percent as the central case.

---

## 5. Axes of consideration (parameter grid)

| Axis | Values |
|---|---|
| Submissions $N$ | log-spaced 1,000; 2,000; 5,000; 10,000; 20,000; 50,000; 100,000; 200,000; 500,000; 1,000,000 |
| Reviewer error $\sigma_\varepsilon$ | a coarse grid {1.0, 1.5, 2.0, 2.5} and a fine grid of 14 points from 0.25 to 3.5, plus the calibrated value(s) from §7 |
| Reviews per paper $R$ | 1, 2, 3, 4, 5, 6, 8, 10, 15, 20, 50 (central cases $R = 3$ and $R = 4$) |
| Shared noise $\sigma_u$ | 0 and 0.5 |
| Score scale | the five rows of §3.2 |
| Quality distribution | the shapes of §3.3 |
| Noise distribution | Gaussian, $t_3$ |
| Acceptance rate $\alpha$ | 0.10 to 0.40 in steps of 0.05 |
| Selection sizes | $K$ and $p$ as in §4 |
| Real venue-years | each (venue, year) in §10.4: its $N$, $\alpha$, oral count |

Sweeps to run at minimum: (a) $N$ at several $\sigma_\varepsilon$ with $R = 3$, two committees; (b) $R$ with and without shared noise at $N = 2{,}000$ and $20{,}000$; (c) fine $\sigma_\varepsilon$ grid at $N \in \{10^3, 10^4, 10^5\}$; (d) quality tails over $N$; (e) score scales over $N$ at $R = 4$ with per-scale recalibration; (f) acceptance rate at $N = 10^4$; (g) the main sweep at the calibrated reliability over $N$ for $K \in \{5, 10, 30\}$ and $p \in \{0.5\%, 5\%, 20\%\}$; (h) a high-replication sweep of the best-paper probability over $N$.

---

## 6. Analytical calculations to carry out

Work in standardised units: $Q^\ast = (q-\mu_q)/\sigma_q$ and $S^\ast$ the standardised score, so that in the Gaussian model $(Q^\ast, S^\ast)$ is bivariate normal with correlation $\rho$. Useful tools: the bivariate normal orthant probability $P_2(a,b;r) = P(X>a, Y>b)$ for a standard bivariate normal pair with correlation $r$ (scipy's `multivariate_normal.cdf` or Owen's $T$); the theory of order statistics and their **concomitants** (David & Nagaraja, *Order Statistics*, 2003, ch. 6; Yeo & David 1984; Nagaraja & David 1994); the large-$N$ behaviour of Gaussian maxima; the **optimizer's curse** / winner's curse literature (Smith & Winkler 2006; Denrell & Liu 2012); **tail independence** of the bivariate normal (Ledford & Tawn 1996). Derive, do not look up:

1. **Reliability.** $\rho^2$ as a function of $(\sigma_q, \sigma_\varepsilon, R, \sigma_u)$; the correlation between two independent committees' scores of the same paper; the upper bound on $\rho^2$ as $R\to\infty$ when $\sigma_u > 0$.
2. **Fixed-percentile precision.** A closed form for the precision of the top-$p$ set as a function of $p$ and $\rho$, using $P_2$ and $z_p = \Phi^{-1}(1-p)$. Determine whether and how it depends on $N$ (exactly, and in the finite-$N$ simulation where $\mathrm{round}(pN)$ is an integer). Same for the swap fraction at acceptance rate $\alpha$.
3. **Two-committee disagreement.** $P(\text{rej}_2\mid\text{acc}_1)$ and the share of papers with inconsistent decisions as functions of $\alpha$ and $\rho$; the conversion between the two; the inverse map from an observed disagreement at a known $\alpha$ to $\rho$ (used for calibration, §7.1).
4. **Fixed-number precision at finite $N$.** An expression for the precision of $\mathrm{Top}_K(\bar s)$ at finite $N$ (for example by conditioning on the $K$-th largest score, or by writing it as the fixed-percentile formula at $p = K/N$ and quantifying the finite-$K$ correction), and a vectorised numerical evaluation. Then the **large-$N$ behaviour** at fixed $K$: does the precision tend to a positive limit or to zero? If to zero, at what rate, and how does the rate depend on $\rho$? Give the leading-order law and the size of the next correction, and compare the **local log-log slope** over $N = 10^3$ to $10^6$ with the asymptotic slope, since the two may differ materially in the range of interest.
5. **The mechanism.** Give an intuitive, quantitative account of why the fixed-number and fixed-percentile rules behave as they do, in terms of the expected quality of a paper conditional on an extreme score versus the quality needed to be truly in the top $K$ (both as functions of $N$), and the conditional spread of quality given score.
6. **Containment in a fixed top percentile.** For fixed $K$ and fixed $p$ (say 1 percent), the large-$N$ limit of the share of $\mathrm{Top}_K(\bar s)$ that lies in the true top $p$.
7. **Best-paper probability.** $P(\text{the best paper is in }\mathrm{Top}_K(\bar s))$ as a function of $N$, $K$, $\rho$. A semi-analytic route: condition on the best paper's standardised quality $m$ (density $N\phi(m)\Phi(m)^{N-1}$) and its score, compute the expected number $\lambda$ of other papers that out-score it, and approximate the count of such papers as Poisson($\lambda$) for large $N$. Check against exact small-$N$ computation and against simulation.
8. **Rank of the winner.** The distribution of the true rank of the top-scored paper and its median, as functions of $N$ and $\rho$.
9. **Two-committee top-$K$ overlap** as a function of $N$, $K$, $\rho$ (a bivariate normal with correlation $\rho^2$ at the $K/N$ quantile).
10. **Tails.** How the large-$N$ behaviour of fixed-number precision depends on the upper tail of the quality distribution relative to the tail of the noise: Gaussian versus exponential versus regularly varying (Student-$t$) versus bounded support. Which combinations give decay to zero, a positive plateau, or an increase toward one, and why (tail dependence of the (quality, score) pair). Also whether fixed-percentile precision depends on $N$ for non-Gaussian shapes.
11. **Acceptance rate.** How the swap fraction and the two-committee disagreement depend on $\alpha$ at fixed $\rho$, and why.
12. **Discretisation.** Explain why closed forms are not available once scores are snapped (ties, non-Gaussian score distribution) and what can be said qualitatively; rely on simulation for numbers.
13. **Verification.** Compare every analytical quantity with simulation across the grid, and report the agreement (relative error for fixed-$K$ quantities; absolute error for the $N$-free quantities). Independently re-derive the asymptotic law before trusting it; the earlier work found that an initial prefactor was wrong.

---

## 7. Calibration procedure

Calibrate the noise so that the model reproduces what the field experiments measured, then carry a central value and a plausible range through every result as sensitivity bands.

### 7.1 From two-committee disagreement (primary)

Given an experiment's acceptance rate $\alpha$ and its disagreement (either $P(\text{rej}_2\mid\text{acc}_1)$ or the share of papers with inconsistent decisions), invert the relation from §6.3 to obtain $\rho^2$, then obtain $\sigma_\varepsilon$ for the chosen $R$ (and $\sigma_u$) from §6.1. Do this for:

- NeurIPS 2014, using the raw $2\times 2$ table at the committees' own acceptance rate (about 26 percent), and separately using the often-quoted version that applies the 25.9 percent inconsistency rate to the conference-wide 22.5 percent acceptance rate (the two give different answers; report both and say which you adopt and why).
- NeurIPS 2021, using 23.0 percent inconsistent decisions at a 22.7 percent average acceptance rate.
- NeurIPS 2014's published correlation between the two committees' mean calibrated scores (§10.1), which maps to $\rho^2$ through §6.1 directly.

### 7.2 From inter-review correlation (secondary)

Given the correlation $r$ between two reviews of the same paper and the number of reviews per paper $R$, the reliability of the mean score follows from the Spearman–Brown formula. Apply it to the ICLR dataset's $r = 0.40$ at $R = 3.7$ and to $R = 3$ and $4$, and to the NeurIPS 2014 variance components (§10.2). State what this estimate includes and omits relative to the experiments (it measures reviewer-level agreement only and knows nothing about the AC stage or any shared component), and treat it accordingly when combining estimates.

### 7.3 Per-variant recalibration

Every non-Gaussian variant (§3.2 to §3.5) must be recalibrated on its own, by bisection on $\sigma_\varepsilon$, so that the simulated two-committee disagreement at the experiment's acceptance rate equals the empirical target used for the base model. Compare variants only after recalibration. Specify the acceptance rate and the target disagreement used, the simulated $N$ (a few thousand is enough), the number of replicates, and the tolerance.

### 7.4 Sensitivity

Carry at least three reliabilities through all results: a pessimistic, a central and an optimistic value spanning the range implied by §7.1 and §7.2. Also run secondary sweeps at the coarse $\sigma_\varepsilon$ grid of §5 so that readers can locate any reliability they prefer.

---

## 8. Validation (out-of-sample tests)

The calibration uses only the accept-level disagreement. Test the model on data it was not fitted to, and report the comparison honestly in both directions.

### 8.1 NeurIPS 2021 Spotlight or Better consistency

> **Reconstruction.** The body of this section was missing from the pasted handoff. The
> text below is inferred from §3.5 and §10.1 and should be replaced if the original
> is available.

The NeurIPS 2021 experiment reports two facts about its awards that the calibration does
not use (§10.1). It had no Best Papers tier, so its Orals and Spotlights together are its
Spotlight or Better set. Of one committee's Spotlight recommendations, the other committee
rejected 13 of 25 and 13 of 23; and if only orals and spotlights had been accepted, the two
committees would have accepted 29 and 25 papers and agreed on 3. For each of the six
variants of §3.5, calibrated separately (§7.3) to the NeurIPS 2021 accept-level
disagreement, simulate the experiment: two committees score the same papers; each
accepts at the experiment's acceptance rate and places its top-scored papers in a
Spotlight or Better set of the observed size (29 and 25 of 882; of these, 25 and 23 are
Spotlights). Report (i) the model's distribution of the overlap count of the two Spotlight
or Better sets, with the probability of observing 3 or fewer; (ii) the model's
$P(\text{rejected by committee 2}\mid\text{Spotlight of committee 1})$ against 13/25 and 13/23. Simulate both a stand-alone
pool of 882 papers and the experiment as a random 882-paper subsample of a 9,122-paper
conference whose tiers are set conference-wide.

### 8.2 ICLR split-half replay

Public ICLR reviews allow a direct experiment at the level of individual papers. Data: the `papercopilot/paperlists` repository on GitHub, files `iclr/iclr{year}.json` for 2017 to 2025 (reachable at `https://raw.githubusercontent.com/papercopilot/paperlists/main/iclr/iclr2024.json` and similar). Each record carries a per-review score list (field `rating` through 2021, `recommendation` from 2022), a decision/status, a track, and a citation count. Procedure:

1. Keep main-track papers with a final decision (oral, spotlight, poster, reject) and at least four reviews.
2. For each of 200 random splits, divide each paper's reviews into two halves of two (drop any extra), compute each half's mean, and re-make decisions in each half at the observed acceptance rate of the decided set (top $A$ by half-mean, ties random).
3. Record the share of papers with inconsistent decisions, the precision of half 1's accepted set with respect to half 2's, the overlap of the two halves' top-10 and top-30 sets, and the correlation between the two half-means.
4. Build the matching model: two committees of $R = 2$ reviews on that year's actual score scale (§10.3; integer 1 to 10 for 2021, 1/3/5/6/8/10 for 2022 to 2025), with random tie-breaking, with $\sigma_\varepsilon$ chosen so that the model's correlation between the two committees' means equals the observed one. Compare the model's accept-level precision and top-10/top-30 overlaps with the observed values, year by year.

Caveats to state: the two halves share the AC and the rebuttal, each half has only two reviews, and the decided set with four or more reviews is a subset of submissions.

### 8.3 Variance decomposition of public reviews

From the same dumps compute, per year, the between-paper and within-paper standard deviations of individual scores and the intraclass correlation ICC(1) (equivalently the correlation between two random reviews of the same paper), the mean and SD of paper-average scores, and the empirical decision threshold (the mean score at which the acceptance probability crosses one half). Use these to check $\sigma_q$ and to supply the §7.2 calibration from first-hand data.

### 8.4 Historical application

Evaluate the calibrated model at each venue-year's $N$, acceptance rate and oral count (§10.4): fixed-number precision at $K = 5, 10, 30$; precision at that year's oral count (Oral or Better); the swap fraction and the count of wrong accepts; the two-committee disagreement. Present as a time series per venue with sensitivity bands. Keep ICLR 2026's two possible acceptance denominators separate (§10.4).

---

## 9. Simulation protocol

- **Vectorised numpy.** Simulate many conferences at once as a (replicates × $N$) array. Use `argpartition` for top-$K$ sets and a ranking routine for true ranks. For the pure Gaussian, undiscretised model do not draw the $R$ individual reviews: $\bar s_i = q_i + u_i + \mathcal{N}(0, \sigma_\varepsilon^2/R)$ is exact. Draw individual reviews only when scores are snapped to a scale or noise is non-Gaussian.
- **Replicates.** Target 10,000 simulated conferences per setting for $N \le 10^4$; at larger $N$ let the count fall under a fixed budget of random draws (the earlier work used a budget of $2\times 10^8$ draws per setting, clipped to between 200 and 10,000 replicates, in chunks of about $2\times 10^7$ draws). Report standard errors. For metrics that are probabilities of rare events at large $N$ (the best-paper probability in particular), a few hundred replicates give standard errors of 2 to 3 points, which produce visible kinks in curves; use several thousand replicates there. The best-paper probability needs only the best paper's score rank, which costs $O(N)$ per conference without sorting, so thousands of replicates are affordable even at $N = 10^6$.
- **Two committees** share $q$ (and the quality draw only), and redraw $u$ and $\varepsilon$ independently.
- **Ties.** Break ties by adding a negligible uniform jitter before ranking (and strip it before computing any correlation of scores).
- **Medians** (true rank of the winner) must be pooled over all simulated conferences, not averaged over chunks.
- **Seeds.** One distinct seed per configuration; record it in the output.
- **Outputs.** One CSV row per configuration with all parameters, all metrics, replicate count, and wall time.
- **Compute.** The full set of sweeps ran in well under an hour on 4 CPU cores with multiprocessing.

---

## 10. Empirical claims relied on

Status key: **V** = verified by the author against the primary source on 2 October 2026; **P** = read from a primary page or paper but not independently re-verified; **S** = secondary source; **U** = unverified or conflicting. Several items were first collected by web search from search-engine extracts because the sandbox could not fetch arxiv.org, openreview.net or the conference blogs; the **V** items were then checked by the author.

### 10.1 Two-committee consistency experiments

| Claim | Status | Source |
|---|---|---|
| NeurIPS 2014: 166 papers (about 10 percent of submissions) were reviewed independently by two committees. Raw $2\times2$ table: 22 accepted by both, 22 accepted by committee A only, 21 by committee B only, 101 rejected by both. So 43/166 = 25.9 percent received inconsistent decisions; each committee accepted 44/166 and 43/166 (about 26 percent); of one committee's accepts, 50 percent and 51 percent were rejected by the other. | V | Lawrence, "The NIPS experiment" (inverseprobability.com, 16 Dec 2014); Cortes & Lawrence, "Inconsistency in Conference Peer Review: Revisiting the 2014 NeurIPS Experiment", arXiv:2109.09774 |
| The often-quoted "57 percent of accepted papers would be rejected on a rerun" comes from applying the 25.9 percent inconsistency rate to the conference-wide 22.5 percent acceptance rate rather than to the committees' own rate. | V | same |
| NeurIPS 2014: published Pearson correlation between the two committees' mean calibrated scores is 0.55 ± 0.065 (0.544 in the accompanying notebook). | V | Cortes & Lawrence 2021; Lawrence's 2021 slides (inverseprobability.com/slides/2021-06-16-the-neurips-experiment.slides.html) |
| NeurIPS 2014: fitted variance components of individual scores: paper 1.28, reviewer offset 0.24, subjective 1.27 (so the reviewer-offset component is 8.6 percent of the total fitted variance, and after removing offsets about half of the remaining variance is subjective). | V | Cortes & Lawrence 2021 |
| NeurIPS 2014: no significant correlation between review scores and later citations among accepted papers; 0.22 ± 0.038 among rejected papers. | V | Cortes & Lawrence 2021 |
| NeurIPS 2021: 882 duplicated papers; 203 (23.0 percent) received inconsistent accept/reject recommendations at an average acceptance rate of 22.7 percent; random decisions would give 35.1 percent. | V | Beygelzimer, Dauphin, Liang & Wortman Vaughan, "Has the Machine Learning Review Process Become More Arbitrary as the Field Has Grown? The NeurIPS 2021 Consistency Experiment", arXiv:2306.03262; NeurIPS blog, 8 Dec 2021 |
| NeurIPS 2021: of one committee's spotlight recommendations, the other committee rejected 13 of 25 and 13 of 23. If only orals and spotlights had been accepted, the two committees would have accepted 29 and 25 papers and agreed on 3. | V | arXiv:2306.03262 |
| NeurIPS 2021 did **not** report a numerical correlation between the committees' mean scores, nor the disagreement broken down by score band. | V (absence) | arXiv:2306.03262 |
| NeurIPS 2021 main track: 9,122 submissions, 25.7 percent accepted. | P | NeurIPS 2021 fact sheet (neurips.cc/media/Press/NeurIPS_2021-Fact_Sheet.pdf) |
| Low inter-reviewer agreement is general across fields (grant and journal review). | S | Cole, Cole & Simon, *Science* 1981; Bornmann, Mutz & Daniel, *PLoS ONE* 2010 |

### 10.2 Inter-review agreement and score dispersion

| Claim | Status | Source |
|---|---|---|
| ICLR 2017 to 2024 (berenslab ICLR dataset): correlation between two reviews of the same paper 0.40 over 244,226 review pairs; 3.7 reviews per paper on average. | V | https://github.com/berenslab/iclr-dataset (24,445 papers 2017 to 2024; 93 percent of reviewed papers had 3 or 4 reviews) and its accompanying write-up |
| Paper-average rating statistics (Paper Copilot scrapes of OpenReview): mean paper-average rating 5.18 (ICLR 2022), 5.13 with SD 1.33 (2023), about 5.11 (2024), 5.12 with SD 1.25 (2025); ICLR 2025 accepted papers averaged 6.43 (SD 0.68; poster 6.23, spotlight 7.35, oral 7.79) and rejected 4.77 (SD 0.92); the acceptance threshold in mean score sat near 5.11 (2024) and 5.12 (2025); the average score moved from 4.78 before to 5.14 after the discussion period in 2025. | S | papercopilot.com/statistics/iclr-statistics/ (per-year pages) |
| Our own decomposition of the paperlists dumps (recompute it): ICC(1) of individual scores 0.58 (2017), 0.41 (2018), 0.46 (2019), 0.39 (2020); within-paper SD 1.03 to 1.19 and between-paper SD 1.00 to 1.20 on the 10-point scale. | own computation | `papercopilot/paperlists` JSON dumps |
| Rebuttals: across ICLR 2024 and 2025, 75 to 81 percent of individual review scores were unchanged after rebuttal, 17 to 23 percent increased, about 1 percent decreased (modal transition 5 → 6); papers whose scores improved were accepted 56 to 58 percent of the time versus 8 to 12 percent for papers with unchanged scores. | V (75 to 81 percent unchanged) / S (rest) | Paper Copilot; secondary analyses of OpenReview |
| No published estimate of reviewer leniency (fixed-effect) variance exists for ICLR or ICML; OpenReview anonymised reviewer IDs are per paper, so leniency cannot be estimated from the public dumps. The only such estimate is the NeurIPS 2014 one above. | P (absence) | — |

### 10.3 Reviews per paper and score scales

| Claim | Status | Source |
|---|---|---|
| NeurIPS 2024 and 2025 guidelines require every paper to end with at least three quality reviews before the author response; ACs aim for four qualified reviewers. The claim that four are always assigned is **not** substantiated for NeurIPS. | V (at least three) / U (four assigned) | neurips.cc/Conferences/2025/SAC-Guidelines; NeurIPS 2024 AC guidelines |
| ICML 2025 and 2026 AC instructions: four reviewers assigned, at least three required. ICML 2024: three auto-assigned plus one AC-chosen. | P | icml.cc/Conferences/2025/ReviewerInstructions; icml.cc/Conferences/2026/PeerReviewFAQ; ICML 2024 PC blog |
| Realised reviews per paper: ICLR 2026 about 4.1 (76,139 reviews / 18,746 reviewed submissions); ICML 2026 about 3.3. | V (ICLR counts) / S (ICML) | blog.iclr.cc/2026/03/31/a-retrospective-on-the-iclr-2026-review-process/ |
| NeurIPS overall score: integer 1 to 10 through 2024 (10 award quality, 9 very strong accept, 8 strong accept, 7 accept, 6 weak accept, 5 borderline accept, 4 borderline reject, 3 reject, 2 strong reject, 1 very strong reject), with 1 to 4 sub-scores and 1 to 5 confidence; six-point 1 to 6 from 2025 (6 strong accept "top 2 to 3 percent", 5 accept, 4 borderline accept, 3 borderline reject, 2 reject, 1 strong reject). | V | neurips.cc/Conferences/2024/ReviewerGuidelines; neurips.cc/Conferences/2025/ReviewerGuidelines |
| ICML overall score: 1 to 10 in 2023 to 2024; five-point 1 to 5 in 2025 (5 strong accept ... 1 reject; no confidence score); six-point 1 to 6 in 2026 with a 1 to 5 confidence score reintroduced. | V (2025, 2026) / P (2023 to 2024) | icml.cc/Conferences/2025/ReviewerInstructions; icml.cc/Conferences/2026/PeerReviewFAQ |
| ICLR overall rating: integer 1 to 10 in 2017 to 2019 and 2021 (all ten values occur in the 2021 dump: 14/167/905/2,289/2,685/2,832/1,999/495/112/10 reviews for 1 to 10); four-point 1/3/6/8 in 2020; {1,3,5,6,8,10} in 2022 to 2025 (the 2022 and 2023 dumps contain exactly those six values: 2022 310/3,223/3,771/3,714/2,089/54; 2023 465/4,711/5,126/5,326/2,846/101; 2024 to 2025 per the reviewer guide: 1 strong reject, 3 reject, 5 marginally below threshold, 6 marginally above, 8 accept, 10 strong accept). | V (dumps checked 2 Oct 2026; 2025 guide) | `papercopilot/paperlists` dumps; iclr.cc/Conferences/2025/ReviewerGuide |
| ICLR 2026 reportedly moved to {0,2,4,6,8,10} (0/2/4 reject, 6/8/10 accept, no borderline point). | U | iclr.cc/Conferences/2026/ReviewerGuide (not independently verified) |

### 10.4 Submissions, acceptance rates, orals and awards by venue-year

Main-track figures. "orals" is the count of oral presentations; "awards" counts best-paper-type awards (outstanding paper, best paper, test of time excluded) and is blank where not sourced. Use acceptance rate × $N$ for the accepted count unless a count is given.

| Venue | Year | Submissions $N$ | Acceptance rate | Orals | Awards | Status / notes |
|---|---|---|---|---|---|---|
| NeurIPS | 2014 | 1,678 | 24.7% | 20 | | V (orals from Lawrence's notebook; 62 spotlights) |
| NeurIPS | 2015 | 1,838 | 21.9% | | | S |
| NeurIPS | 2016 | 2,403 | 23.6% | | 1 | S |
| NeurIPS | 2017 | 3,240 | 20.9% | 40 | 3 | S |
| NeurIPS | 2018 | 4,856 | 20.8% | 30 | 4 | S |
| NeurIPS | 2019 | 6,743 | 21.2% | 36 | 2 | S |
| NeurIPS | 2020 | 9,454 | 20.1% | 105 | 3 | S |
| NeurIPS | 2021 | 9,122 | 25.7% | 55 | 6 | P (fact sheet) |
| NeurIPS | 2022 | 10,411 | 25.6% | | 13 | P (fact sheet) |
| NeurIPS | 2023 | 12,343 | 26.1% | 67 | 2 | P/S (3,218 accepted; 67 orals, 378 spotlights) |
| NeurIPS | 2024 | 15,671 | 25.8% | 61 | 2 | P for N and rate (fact sheet: 4,037 accepted); **U** for 61 orals |
| NeurIPS | 2025 | 21,575 | 24.5% | 87 | 4 | V (5,290 accepted = 24.52%; 87 orals per fact sheet and oral-event page; an earlier figure of 77 was wrong) |
| NeurIPS | 2026 | 30,709 | 25.7% | 112 | | V by several 2026 reports (7,900 accepted = 7,496 posters + 292 spotlights + 112 orals); no fact sheet yet |
| ICML | 2014 | 1,238 | 25.0% | | | S |
| ICML | 2015 | 1,037 | 26.0% | | | S |
| ICML | 2016 | 1,320 | 24.4% | | | S |
| ICML | 2017 | 1,676 | 25.9% | | | S |
| ICML | 2018 | 2,473 | 25.1% | | | S |
| ICML | 2019 | 3,424 | 22.6% | | | S |
| ICML | 2020 | 4,990 | 21.8% | | 2 | S |
| ICML | 2021 | 5,513 | 21.5% | 166 | 1 | S |
| ICML | 2022 | 5,630 | 21.9% | 118 | 10 | S |
| ICML | 2023 | 6,538 | 27.9% | 158 | 6 | S |
| ICML | 2024 | 9,473 | 27.5% | 144 | 10 | P (fact sheet) |
| ICML | 2025 | 12,107 | 26.9% | 120 | 6 | V (3,260 accepted) |
| ICML | 2026 | 23,918 | 26.6% | 159 | 2 | V (6,352 accepted; 168 orals = 159 main track + 9 position track) |
| ICLR | 2017 | 507 | 39.1% | 15 | 3 | S |
| ICLR | 2018 | 981 | 32.0% | 23 | 3 | S |
| ICLR | 2019 | 1,591 | 31.4% | 24 | 2 | S |
| ICLR | 2020 | 2,594 | 26.5% | 48 | 2 | S |
| ICLR | 2021 | 2,997 | 28.7% | 53 | 8 | S |
| ICLR | 2022 | 3,328 | 32.9% | 54 | 7 | S |
| ICLR | 2023 | 4,938 | 31.8% | 91 | 4 | S |
| ICLR | 2024 | 7,262 | 31.1% | 86 | 5 | P (press release; 7,262 to 7,304 depending on source) |
| ICLR | 2025 | 11,603 | 31.9% | 213 | 3 | V (fact sheet: 11,603 submissions, 3,704 accepted, 213 orals, 380 spotlights; OpenReview shows 11,672 entries, 11,565 reviewed) |
| ICLR | 2026 | 19,525 | 27.4% of valid / 38.9% of decided | 224 | 2 | V for 19,525 valid, 779 desk-rejected, 5,042 withdrawn, 13,763 decided, 5,355 accepted, 76,139 reviews; **U** for 224 orals. Keep the two denominators separate. |

Sources: NeurIPS fact sheets (media.neurips.cc/Conferences/NeurIPS20xx/...Fact_Sheet.pdf for 2021 to 2025) and the NeurIPS 2025 PC blog (blog.neurips.cc/2025/09/30/...); ICML fact sheets (media.icml.cc/Conferences/ICML2024/ICML2024_Fact_Sheet.pdf, ICML2025_Fact_Sheet.pdf) and the ICML 2026 awards post (blog.icml.cc/2026/07/05/...); ICLR fact sheets and press releases (media.iclr.cc/Conferences/ICLR2025/ICLR2025_Fact_Sheet.pdf, ICLR2024_Press_Release.pdf) and the ICLR 2026 retrospective (blog.iclr.cc/2026/03/31/...); Paper Copilot statistics pages and csconfstats for the older secondary rows.

### 10.5 How decisions are actually made (process facts that motivate model choices)

| Claim | Status | Source |
|---|---|---|
| No venue decides by mean score alone: ACs write a meta-review with a recommendation, SACs calibrate across ACs, PCs finalise; orals and spotlights are decided jointly by SACs and PCs (NeurIPS) or by AC/SAC/PC calibration separate from the accept recommendation (ICLR). | P | NeurIPS and ICLR reviewer/AC guidelines; NeurIPS 2025 PC blog |
| NeurIPS 2025 PCs report that ACs overrode reviewers in both directions, and that volume forced SAC-level ranking that rejected some AC-recommended papers (secondary reports: roughly 400 papers). | P (override) / S (400) | blog.neurips.cc/2025/09/30/... |
| NeurIPS 2025 committee: 20,518 reviewers, 1,663 ACs, 199 SACs (about 13 papers per AC). | P | same |
| Desk rejections and withdrawals: ICLR desk-rejected 53 (2024), 148 (2025), 779 (2026) papers; ICLR withdrawals were 22 percent (2024), 25.6 percent (2025), 25.8 percent (2026); ICML 2026 desk-rejected 497 papers for LLM-review violations by their reciprocal reviewers. | P/S | ICLR retrospectives; ICML 2026 PC communications |
| Oral share of submissions has fallen at NeurIPS from about 1.2 percent (2014) to about 0.4 percent (2025 to 2026). | derived from 10.4 | — |

### 10.6 Background literature (methods and context, not data)

Shah, "An overview of challenges, experiments, and computational solutions in peer review" (2022 survey); Brezis & Birukou, "Arbitrariness in the peer review process" (2020); Fang & Casadevall, "Research funding: the case for a modified lottery" (2016); Gross & Bergstrom, "Contest models highlight inherent inefficiencies of scientific funding competitions" (2019); Smith & Winkler, "The optimizer's curse" (2006); Denrell & Liu, "Top performers are not the most impressive when extreme performance indicates unreliability" (2012); David & Nagaraja, *Order Statistics* (2003); Yeo & David, "Selection through an associated characteristic, with applications to the random effects model" (1984); Nagaraja & David, "Distribution of the maximum of concomitants of selected order statistics" (1994); Ledford & Tawn, "Statistics for near independence in multivariate extreme values" (1996); Cole, Cole & Simon, "Chance and consensus in peer review" (1981); Bornmann, Mutz & Daniel, "A reliability-generalization study of journal peer reviews" (2010).

### 10.7 Known gaps

- No numerical correlation between the two 2021 committees' mean scores, and no 2021 disagreement by score band, is published.
- NeurIPS 2024's oral count (61) and ICLR 2026's oral count (224) and rating scale are unverified.
- Krippendorff-alpha style agreement values attributed to secondary analyses of ICLR 2017 to 2020 were read from search extracts and not checked.
- The exact relation between the "77 orals" that appeared in one extract and the fact sheet's 87 for NeurIPS 2025 was resolved in favour of 87.

---

## 11. Practical notes for the reproducing session

- The earlier sandbox could reach pypi.org and github.com (including `raw.githubusercontent.com`) but not arxiv.org, openreview.net, papercopilot.com or the conference sites; plan data access accordingly, and ask the user to fetch any primary page that is blocked.
- Python stack used: numpy, scipy, pandas, matplotlib. LaTeX: a TinyTeX installation from its GitHub release works without CTAN access; `times`/`helvet` fonts, `natbib`, `hyperref`, `booktabs`, `graphicx`; use pymupdf to check page count and per-page figure placement.
- The ICLR dumps are large (15 to 30 MB per year); parse once and cache.
- Keep every number that enters the paper traceable to a CSV row or a sourced claim.
