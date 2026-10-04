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
- **Fixed-number selection** of size $K$ picks $\mathrm{Top}_K(\bar s)$ with $K$ constant
  in $N$ (best-paper awards, a fixed number of talk slots).
- **Fixed-percentile selection** at fraction $p$ picks $\mathrm{Top}_{\mathrm{round}(pN)}(\bar s)$
  (acceptance at rate $\alpha$; oral or spotlight tiers defined as a share of submissions).
- $A = \mathrm{round}(\alpha N)$ is the number of accepted papers.

## Top of the ranking

| Metric | Definition | CSV column |
|---|---|---|
| Precision | $\lvert\mathrm{Top}_K(\bar s)\cap\mathrm{Top}_K(q)\rvert/K$. Because the quota is fixed, $1-$ precision is also the share of deserving papers left out. | `prec_K{K}`, `prec_p{pct}pct` |
| Containment in the true top $M$ | share of $\mathrm{Top}_K(\bar s)$ inside $\mathrm{Top}_M(q)$ for $M = 2K$, $10K$, the top 1 %, the top 5 % and the top $\alpha$ fraction | `c2x_`, `c10x_`, `c1pct_`, `c5pct_`, `cA_` |
| Mean true percentile | mean of the population CDF $F(q)$ over $\mathrm{Top}_K(\bar s)$ | `pctl_` |
| Best paper | $P(\arg\max_i q_i \in \mathrm{Top}_K(\bar s))$ for $K = 1, 5, 10, 30$ | `best_in_K{K}` |
| Rank of the winner | true rank (1 = best) of $\arg\max_i \bar s_i$; quantiles pooled over all simulated conferences | `winner_rank_q50` etc. |
| Two-committee overlap | $\lvert\mathrm{Top}_K(\bar s^{(1)})\cap\mathrm{Top}_K(\bar s^{(2)})\rvert/K$, observable without knowing $q$ | `ovl_` |
| Rejected by a second committee | share of $\mathrm{Top}_K(\bar s^{(1)})$ that committee 2 rejects at acceptance rate $\alpha$ | `rej2_` |
| The Best Paper under a second review | rank of $\arg\max_i \bar s^{(1)}_i$ by committee 2's scores $\bar s^{(2)}$; $P(\text{rank} \le M)$ for $M = 1$ (top-scored again), 10, the oral count and $A$; one minus the last is "rejected by a second committee". The paper's headline framing: it is in the units of the NeurIPS consistency experiments. In the Gaussian model it equals the true-rank integral with $\rho$ replaced by $\rho^2$. | `p2_best`, `p2_top10`, `p2_oral`, `p2_accept`, `p2_reject`, `winner_rank2_median` (`winner_in2_*` in the simulator) |

## The accept/reject boundary

| Metric | Definition | CSV column |
|---|---|---|
| Swap fraction | share of accepted papers not in $\mathrm{Top}_A(q)$; equals the share of deserving papers rejected | `swap_acc{alpha}` |
| Wrong accepts (count) | swap fraction $\times A$; equals the count of deserving papers rejected | derived |
| Two-committee disagreement | $P(\text{rejected by 2}\mid\text{accepted by 1})$, "the share of accepted papers that a rerun would reject" | `dis_acc{alpha}` |
| Inconsistent decisions | share of all papers accepted by exactly one committee | `incons_acc{alpha}` |

When both committees accept $A = \alpha N$ papers, the two boundary statistics are tied
exactly: inconsistent share $= 2\alpha \times$ disagreement (each paper accepted by 1 and
rejected by 2 is matched by one paper accepted by 2 and rejected by 1).

## Two committees

A second committee sees the same papers (same $q_i$) and redraws all reviewer errors
$\varepsilon_{ij}$ and the shared noise $u_i$, because the field experiments used disjoint
area chairs and reviewers.

## Sizes reported

$K \in \{1, 5, 10, 30, 100\}$ and each venue-year's oral count; $p \in \{0.3, 0.5, 1, 5, 20\}$ %;
$\alpha \in \{0.10, 0.15, \ldots, 0.40\}$, with 0.20 to 0.25 as the central case.
