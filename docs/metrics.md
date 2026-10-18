# Metrics

This file defines "the best papers" and "a wrong decision" before any model is fitted
(handoff §4, deliverable 1). Column names in the result CSVs follow
`src/peerreview/simulate.py`.

## Objects

- $N$ submissions. Paper $i$ has a true quality $q_i$ and a score $\bar s_i$ (the mean of
  its reviews). Ranks are by value, largest first; ties in $\bar s$ are broken uniformly
  at random.
- $\mathrm{Top}_K(x)$: the $K$ papers with the largest $x$.
- **The best $K$ papers** are $\mathrm{Top}_K(q)$. A paper is **deserving** of a
  selection of size $K$ if it is in $\mathrm{Top}_K(q)$.
- **Constant-number selection** of size $K$ picks $\mathrm{Top}_K(\bar s)$ with $K$ constant
  in $N$ (best-paper awards, a constant number of talk slots).
- **Fixed-percentile selection** at fraction $p$ picks $\mathrm{Top}_{\mathrm{round}(pN)}(\bar s)$
  (acceptance at rate $\alpha$; along the $N$ axis, Oral or Better and Spotlight counts from the fitted power laws of `results/tier_sizes.csv`). Tiers are separate: Best Papers, Oral, Spotlight, Accepted (no award), Rejected; a tier with every tier above it is "X or Better" (`docs/terminology.md`).
- $A = \mathrm{round}(\alpha N)$ is the number of accepted papers, the size of Accepted or Better.

## Top of the ranking

| Metric | Definition | CSV column |
|---|---|---|
| Precision | $\lvert\mathrm{Top}_K(\bar s)\cap\mathrm{Top}_K(q)\rvert/K$. Because the quota is fixed, $1-$ precision is also the share of deserving papers left out. | `prec_K{K}`, `prec_p{pct}pct` |
| Containment in the true top $M$ | share of $\mathrm{Top}_K(\bar s)$ inside $\mathrm{Top}_M(q)$ for $M = 2K$, $10K$, the top 1 %, the top 5 % and the top $\alpha$ fraction | `c2x_`, `c10x_`, `c1pct_`, `c5pct_`, `cA_` |
| Mean true percentile | mean of the population CDF $F(q)$ over $\mathrm{Top}_K(\bar s)$ | `pctl_` |
| Highest-quality paper selected (not the Best Papers; not in the paper) | $P(\arg\max_i q_i \in \mathrm{Top}_K(\bar s))$ for $K = 1, 5, 10, 30$ | `best_in_K{K}` |
| True rank of the Best Papers | true rank (1 = best) of each of the first three papers of the award ordering $t$; quantiles pooled over the three and over all simulated conferences | `winner_rank_q50` etc. (`n_best=3`) |
| Two-review overlap | $\lvert\mathrm{Top}_K(\bar s^{(1)})\cap\mathrm{Top}_K(\bar s^{(2)})\rvert/K$, observable without knowing $q$ | `ovl_` |
| Rejected by a second review | share of $\mathrm{Top}_K(\bar s^{(1)})$ that the second review rejects at acceptance rate $\alpha$ | `rej2_` |
| Tier sizes as conferences grow | count of papers at $N$ submissions: Accepted or Better $=0.25N$ (the grid's share); the Oral or Better count (NeurIPS's Orals, which include its Best Papers) and the Spotlight count fitted as $aN^\gamma$ to NeurIPS 2014--2026 in log-log (`results/tier_sizes.csv`, rows `accept_or_better`, `oral_or_better`, `spot`, `best`); the Best Papers fixed at three. `p2_best` and `p2_{oral,spot,accept}_or_better` are the shares of the Best Papers that a second review ranks within each "or Better" set so sized (the mean over the three; `p2_best` is also the Best Papers' overlap), and `p2_{oral,spot,accept,reject}` the separate tiers, their differences; `ovl_{oral,spot,accept}_or_better` the two reviews' overlap of each set (exact below 30 papers, closed-form fixed-percentile formula above) | `results/tier_scaling.csv` |
| The Best Papers under a second review | rank of each of the first three papers of $t^{(1)}$ (the Best Papers) by the second review's award ordering $t^{(2)}$, where $t_i=\bar s_i+\eta_i$ over the accepted papers ($\eta_i\sim N(0,\sigma_\eta^2)$, the chair noise; acceptance by $\bar s$); $P(\text{rank} \le M)$, the mean over the three, for $M = 3$ (Best Papers again, equal to the Best Papers' overlap) and the sizes of Oral or Better, Spotlight or Better and Accepted or Better (`p2_*_or_better`). The separate tiers are their differences: `p2_oral`, `p2_spot`, `p2_accept` (accepted with no award) and `p2_reject` $= 1 -$ `p2_accept_or_better`; the five separate tiers sum to 1 (`peerreview.tiers.add_separate`; the `_se` of a separate tier is the upper bound $\sqrt{se_{hi}^2+se_{lo}^2}$). The paper's headline framing: it is in the units of the NeurIPS consistency experiments. In the Gaussian model it equals the true-rank integral with $\rho$ replaced by $\rho^2$. | `p2_best`, `p2_oral`, `p2_spot`, `p2_accept`, `p2_reject`, `p2_*_or_better`, `winner_rank2_median` (pooled over the three; `winner_in2_*` in the simulator, `n_best=3`) | Simulated on the main form (`results/best_paper.csv`, `scripts/run_best_paper.py`): 10,000 replays per venue-year, 10,000 per grid point up to 10K submissions and 5,000 above, with 20,000 to 50,000 for `p2_best` (`run_best_paper_hirep.py`, column `reps_best`). The grid rows also carry `overlap_best`, `overlap_{oral,spot,accept}_or_better` and `overlap_top0p3pct` (the proportion of one review's set that the other also ranks in it; the separate tiers' overlaps and every placement are in `results/placement.csv`; the top 0.3% is a fixed proportion as large as the Best Papers at 1,000 submissions) and `z2_winner`, `z2_cut` (the second review's mean score for the first review's Best Papers, and its own third-best score, in SD units of its scores).

## The accept/reject boundary

| Metric | Definition | CSV column |
|---|---|---|
| Swap fraction | share of accepted papers not in $\mathrm{Top}_A(q)$; equals the share of deserving papers rejected | `swap_acc{alpha}` |
| Wrong accepts (count) | swap fraction $\times A$; equals the count of deserving papers rejected | derived |
| Two-review disagreement | $P(\text{rejected by 2}\mid\text{accepted by 1})$, "the share of accepted papers that a rerun would reject" | `dis_acc{alpha}` |
| Inconsistent decisions | share of all papers accepted by exactly one review | `incons_acc{alpha}` |

When both reviews accept $A = \alpha N$ papers, the two boundary statistics are tied
exactly: inconsistent share $= 2\alpha \times$ disagreement (each paper accepted by 1 and
rejected by 2 is matched by one paper accepted by 2 and rejected by 1).

## A second review

A second review sees the same papers (same $q_i$) and redraws all reviewer errors
$\varepsilon_{ij}$ and the chairs' call $\eta_i$ (and the shared noise $u_i$ in the one robustness check
that has it), because the field experiments used disjoint area chairs and reviewers.

## Sizes reported

$K \in \{1, 5, 10, 30, 100\}$ and each venue-year's oral count; $p \in \{0.3, 0.5, 1, 5, 20\}$ %;
$\alpha \in \{0.10, 0.15, \ldots, 0.40\}$, with 0.20 to 0.25 as the central case.
