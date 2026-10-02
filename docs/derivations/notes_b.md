# Derivations B: the point-process route to handoff §6

Author of these notes: deriver B (independent of any other derivation).
Scope: every item of handoff §6 for the Gaussian model, with most effort on items 4 to 10.
Method: rescale the top of the sample so that the top scores and the top qualities form
Poisson processes; use the Gaussian conditional law of quality given score; derive the
fixed-$K$ laws from that limit; check every formula against an exact finite-$N$ quadrature,
against exact small-$N$ values, and against the repository simulator.

Code (all reusable, none of it in the repository):
`/private/tmp/claude-501/-Users-rylanschaeffer-Documents-Scaling-Laws-of-ML-Conference-Peer-Review/7d0174d6-f884-4f59-93ea-00d3f8717415/scratchpad/deriver_b/`

| file | content |
|---|---|
| `fk.py` | exact finite-$N$ quadrature for $E\lvert\mathrm{Top}_K(S)\cap\mathrm{Top}_M(Q)\rvert$, best paper, winner rank, containment, percentile; every asymptotic formula |
| `tails.py` | non-Gaussian shapes: limit laws, plateaus, $N$-free fixed-percentile values |
| `discrete.py` | discretised scores: large-$N$ fixed-percentile metrics as 1-D integrals, top tie class |
| `check_*.py`, `run_*.py`, `report*.py` | the numerical checks quoted below |
| `sim_gauss.py`, `sim_smallN.py`, `sim_tails.py`, `sim_discrete_b.py`, `sim_discrete_c.py` | runs of the repository simulator |
| `check_ovl_1e6*.py` | follow-up runs on the two-committee overlap at $N=10^6$ (§13.3) |
| `run_simcompare.py`, `run_acc_exact.py`, `report13*.py` | exact value for every simulator metric, and the z-score summary (§13) |
| `check_N1000_*.py`, `t_G_check.py`, `t_owen_region.py`, `t_alt_grid.py` | follow-up on one cell at $N=10^3$, $K=100$ (§13.2) |
| `out/` | every number quoted here (JSON lines, logs) |

Run everything as `uv run --project <repo> python <script>` from that folder
(`check_cells.py` also needs `--with mpmath`, an ephemeral package that the project does not
depend on).

---

## 0. Setting, notation, and the summary of results

Standardised units: $Q=(q-\mu_q)/\sigma_q$, $S$ the standardised score. In the Gaussian model
$(Q,S)$ is standard bivariate normal with correlation $\rho$. $N$ papers are iid.

| symbol | meaning |
|---|---|
| $\tau=\sqrt{1-\rho^2}$ | SD of $Q$ given $S$ (and of $S$ given $Q$) |
| $c = 1/(1+\rho)$ | tail exponent of the joint density on the diagonal |
| $\kappa=(1-\rho)/(1+\rho)$ | decay exponent of fixed-$K$ precision |
| $\phi_2(q,s)$ | joint density; $g(q,s)=\phi_2/(\phi(q)\phi(s))$ the Gaussian copula density |
| $P_2(a,b;r)$ | $P(X>a,Y>b)$ for a standard bivariate normal pair with correlation $r$ |
| $b_N$ | the solution of $N\bar\Phi(b_N)=1$; $b_N^2=2\log N-\log(4\pi\log N)+o(1)$ |
| $a_N=N\phi(b_N)=\phi(b_N)/\bar\Phi(b_N)$ | the hazard rate at $b_N$; $a_N=b_N+1/b_N+O(b_N^{-3})$ |
| $\varepsilon_N=N\phi_2(b_N,b_N)/a_N^2=e^{\rho b_N^2/(1+\rho)}/(N\tau)$ | expected number of papers extreme in both coordinates, per unit area of the rescaled plane |
| $I_n(c)=\Gamma(n+c)/(c\,\Gamma(n))=E[G_n^{\,c}]/c$, $G_n\sim\mathrm{Gamma}(n,1)$ | the basic integral of the point-process limit |
| $R_K(\rho)=\big[\Gamma(K+c)/(\Gamma(K)K^{c})\big]^2$ | finite-$K$ factor |
| $\mathrm{prec}_K(N)$ | $E\lvert\mathrm{Top}_K(S)\cap\mathrm{Top}_K(Q)\rvert/K$ |

Values used in the checks: $\rho\in\{0.5,\ 0.7459,\ 0.9\}$. $\rho=0.7459$ is the value that
`analytic.invert_inconsistent(0.227, 203/882)` gives for NeurIPS 2021 ($r_{12}=\rho^2=0.5563$).

**Summary of the main results** (each is derived and checked below).

1. $\rho^2=\sigma_q^2/(\sigma_q^2+\sigma_u^2+\sigma_\varepsilon^2/R)$; two committees correlate at $\rho^2$; $\rho^2\to\sigma_q^2/(\sigma_q^2+\sigma_u^2)$ as $R\to\infty$. `analytic.py` is correct for items 1 to 3.
2. Fixed-percentile precision $\to P_2(z_p,z_p;\rho)/p$, free of $N$; at finite $N$ the exact value differs by a relative $O(1/K)$ with $K=\mathrm{round}(pN)$.
3. $P(\mathrm{rej}_2\mid\mathrm{acc}_1)=1-P_2(z_\alpha,z_\alpha;\rho^2)/\alpha$; inconsistent share $=2\alpha\times$ that.
4. Fixed-$K$ precision tends to **zero**:
   $$\mathrm{prec}_K(N)\sim C_K(\rho)\,(\log N)^{-\rho/(1+\rho)}\,N^{-(1-\rho)/(1+\rho)},\qquad
   C_K(\rho)=\frac{(1+\rho)^{3/2}}{(1-\rho)^{1/2}}\,(4\pi)^{-\rho/(1+\rho)}\,\frac{1}{K}\Big[\frac{\Gamma(K+\tfrac1{1+\rho})}{\Gamma(K)}\Big]^2 .$$
   In terms of $b_N$: $\mathrm{prec}_K=\varepsilon_N I_K(c)^2/K\,\big(1+\beta_K/b_N^2+\omega_K\varepsilon_N+O(b_N^{-4})\big)$ with explicit $\beta_K,\omega_K$. Relative to the fixed-percentile formula at $p=K/N$ the limit factor is $R_K(\rho)$ (a Jensen gap). Over $N=10^3$ to $10^6$ the secant log-log slope is 9 to 14 % ($\rho=0.5$), 25 to 34 % ($\rho=0.7459$) and 58 to 75 % ($\rho=0.9$) steeper than the asymptotic slope $-(1-\rho)/(1+\rho)$, for $K=1$ to 100.
5. The mechanism: the top score sits at $b_N\approx\sqrt{2\log N}$; the quality of that paper is $N(\rho b_N,\tau^2)$; the true top-$K$ quality is also near $b_N$. The gap $(1-\rho)b_N$ grows while the conditional SD $\tau$ stays fixed.
6. Containment of $\mathrm{Top}_K(S)$ in a fixed true top fraction $p$ tends to **one**; containment in the true top $mK$ ($m$ fixed) tends to zero at the same rate as precision.
7. $P(\text{best paper}\in\mathrm{Top}_K(S))\sim \varepsilon_N\,\Gamma(c)\,I_K(c)$, the same $N^{-(1-\rho)/(1+\rho)}(\log N)^{-\rho/(1+\rho)}$ rate.
8. $P(\text{true rank of the winner}\le r)=P(\text{best paper}\in\mathrm{Top}_r(S))$ exactly (exchangeability); the median grows like $N^{1-\rho^2}(4\pi\log N)^{-(1-\rho^2)/2}e^{-\gamma\rho^2}/\rho$.
9. Two-committee top-$K$ overlap $=\mathrm{prec}_K(N)$ with $\rho$ replaced by $\rho^2$.
10. Fixed-$K$ precision at large $N$: decays to zero (Gaussian/Gaussian, and every case where the noise tail is heavier than the quality tail), reaches a plateau strictly between 0 and 1 (exponential/Gaussian; $t_3$/$t_3$), or rises to one ($t_3$ quality with Gaussian noise). The tail-dependence coefficient $\chi$ of (quality, score) sorts the cases. Fixed-percentile precision is $N$-free for every shape.
11. Swap fraction and disagreement fall as $\alpha$ rises; the count of wrong accepts and the inconsistent share are symmetric under $\alpha\leftrightarrow1-\alpha$.
12. Snapped scores: no closed form, but large-$N$ fixed-percentile metrics reduce to 1-D integrals; fixed-$K$ selection at very large $N$ becomes a lottery inside the top tie class, with $\mathrm{prec}_K\approx K/(N\pi_{\rm top})$ once $N\pi_{\rm top}\gg K$.
13. Verification (§13): no defect found in `model.py`, `simulate.py` or `calibrate.py`. The one unresolved pattern is a small pooled deficit of the simulated two-committee overlap at $N=10^6$ (§13.3); a code replay and fresh runs point to chance.

---

## 1. Reliability (§6.1)

The score of paper $i$ is $\bar s_i=q_i+u_i+\bar\varepsilon_i$ with $\bar\varepsilon_i=R^{-1}\sum_j\varepsilon_{ij}$.
The three terms are independent. So $\mathrm{Var}(\bar s)=\sigma_q^2+\sigma_u^2+\sigma_\varepsilon^2/R$ and
$\mathrm{Cov}(q,\bar s)=\sigma_q^2$. Thus
$$\rho^2=\frac{\sigma_q^2}{\sigma_q^2+\sigma_u^2+\sigma_\varepsilon^2/R}.$$

Two committees with $u$ and $\varepsilon$ redrawn: $\mathrm{Cov}(\bar s^{(1)},\bar s^{(2)})=\sigma_q^2$, so
$r_{12}=\rho^2$. With $u$ shared, $r_{12}=(\sigma_q^2+\sigma_u^2)/(\sigma_q^2+\sigma_u^2+\sigma_\varepsilon^2/R)>\rho^2$.
As $R\to\infty$, $\rho^2\to\sigma_q^2/(\sigma_q^2+\sigma_u^2)$; for $\sigma_q=1.2,\sigma_u=0.5$ the bound is $0.8521$.

Spearman–Brown. Two reviews of one paper correlate at $r=(\sigma_q^2+\sigma_u^2)/(\sigma_q^2+\sigma_u^2+\sigma_\varepsilon^2)$,
because both reviews contain $u$. Then $Rr/(1+(R-1)r)=(\sigma_q^2+\sigma_u^2)/(\sigma_q^2+\sigma_u^2+\sigma_\varepsilon^2/R)$.
This is the shared-$u$ committee correlation, not $\rho^2$. It equals $\rho^2$ only when $\sigma_u=0$.
So an inter-review estimate is an upper bound on $\rho^2$ when a shared component exists.

**Which metrics depend on the noise only through $\rho$.** Standardise $q$, $s^{(1)}$, $s^{(2)}$. In the
Gaussian model with continuous scores, $(Q,S^{(1)},S^{(2)})$ is trivariate normal with
correlations $(\rho,\rho,\rho^2)$ (with $u$ redrawn), and $u+\bar\varepsilon$ is Gaussian for every
$(\sigma_u,\sigma_\varepsilon,R)$. Every metric of §4 is a function of the ranks of these three
vectors (the mean percentile uses $\Phi(Q)$, also a rank function). So every §4 metric depends on
$(\sigma_q,\sigma_\varepsilon,R,\sigma_u)$ only through $\rho^2$. This fails when (a) scores are snapped
(the snapping is non-linear and depends on $\mu_q,\sigma_q,\sigma_\varepsilon,R$ and the scale placement
separately), (b) the reviewer error is $t_3$ (the mean of $R$ $t_3$ errors has an $R$-dependent shape;
its tail constant is $\propto\sigma_\varepsilon^3/R^2$, see §10), and (c) the quality is non-Gaussian
(the metric is then a different function of $\rho$ for each shape). It also fails for the raw
score correlation when $u$ is shared.

**Checks** (`run_items123_11.py`, `out/items123_11.json`). `analytic.spearman_brown(r_1, 4)` equals
`analytic.rho2(2, 4)` when $\sigma_u=0$ (0.590164 both). With $\sigma_u=0.5$ Spearman–Brown gives
0.62825, equal to `committee_corr(share_u=True)` and above $\rho^2=0.53532$. `rho2_limit(1.2, 0.5)`
returns 0.852071. The repository test suite (`tests/test_core.py`) checks the simulator's
`corr_qs` and `corr_s12` against $\rho$ and $\rho^2$. In my Gaussian runs (§13) the simulator's
`corr_qs` agrees with $\rho$ to within its standard error.

---

## 2. Fixed-percentile precision (§6.2)

**Limit.** Let $K=\mathrm{round}(pN)$. The $K$-th largest score $S_{(K)}$ and the $K$-th largest
quality $Q_{(K)}$ both converge in probability to $z_p=\Phi^{-1}(1-p)$ (quantile consistency). So
$1\{S_i\ge S_{(K)}\}1\{Q_i\ge Q_{(K)}\}$ has the same limit average as $1\{S_i>z_p,Q_i>z_p\}$, which by
the law of large numbers is $P_2(z_p,z_p;\rho)$. Divide by $p$:
$$\lim_{N\to\infty}\mathrm{prec}_{pN}=\frac{P_2(z_p,z_p;\rho)}{p}=P(Q>z_p\mid S>z_p).$$
The swap fraction at acceptance rate $\alpha$ is $1-P_2(z_\alpha,z_\alpha;\rho)/\alpha$; with a fixed
quota the count of undeserving accepts equals the count of deserving rejects, so the swap fraction
is also the share of deserving papers that are rejected. Both are free of $N$ in the limit.
`analytic.precision_pct` and `swap_fraction` implement exactly these formulas.

$P_2(a,a;\rho)=\bar\Phi(a)-2T(a,\sqrt{(1-\rho)/(1+\rho)})$, with Owen's $T$, is what `P2_diag` uses.
Proof: Owen's identity $\Phi_2(h,h;\rho)=\Phi(h)-2T(h,\sqrt{(1-\rho)/(1+\rho)})$, with $h=-a$ and $T$ even in $h$.

**Exact finite-$N$ value.** The formula of §4.1 with $M=K=\mathrm{round}(pN)$ is exact. It depends on
$N$. In the extreme regime ($p$ small, $K$ large) the point-process result of §4.5 predicts
$\mathrm{prec}/\mathrm{limit}\approx R_K(\rho)=1-c(1-c)/K+O(K^{-2})$, with $c(1-c)=\rho/(1+\rho)^2$, so the
finite-$N$ correction is a deficit of relative order $1/K=1/(pN)$. Table 2 gives the exact values.
Two separate finite-$N$ effects exist: the rounding ($K/N\ne p$; use $p_{\rm eff}=K/N$ in the formula),
and the $O(1/K)$ effect of random thresholds.

**Table 2** (`run_pct.py`, `out/pct_table.jsonl`): exact finite-$N$ precision at $K=\mathrm{round}(pN)$ against the $N$-free limit. $\kappa=K(\text{exact}/\text{limit}-1)$ settles to a constant, so the relative deficit is $\kappa(p,\rho)/K$. The point-process value $K(R_K-1)\to-c(1-c)=-\rho/(1+\rho)^2$ is the $p\to0$ limit of $\kappa$ (last column; at $p=0.3\%$ $\kappa$ is already within 7 to 16 % of it). Larger $p$ gives a smaller deficit.

| rho | p | N | K = round(pN) | exact | limit P2(z_p,z_p)/p | limit at p_eff = K/N | kappa = K (exact/limit_eff - 1) | R_K - 1 times K |
|---|---|---|---|---|---|---|---|---|
| 0.5 | 0.003 | 1000 | 3 | 0.07625 | 0.08182 | 0.08182 | -0.2042 | -0.2096 |
| 0.5 | 0.003 | 1667 | 5 | 0.07837 | 0.08182 | 0.08181 | -0.2105 | -0.2147 |
| 0.5 | 0.003 | 3333 | 10 | 0.08006 | 0.08182 | 0.08182 | -0.2153 | -0.2185 |
| 0.5 | 0.003 | 6667 | 20 | 0.08092 | 0.08182 | 0.08182 | -0.2177 | -0.2204 |
| 0.5 | 0.003 | 16667 | 50 | 0.08146 | 0.08182 | 0.08182 | -0.2192 | -0.2215 |
| 0.5 | 0.003 | 33333 | 100 | 0.08164 | 0.08182 | 0.08182 | -0.2197 | -0.2219 |
| 0.5 | 0.003 | 66667 | 200 | 0.08173 | 0.08182 | 0.08182 | -0.2199 | -0.2220 |
| 0.5 | 0.01 | 300 | 3 | 0.12128 | 0.12939 | 0.12939 | -0.1880 | -0.2096 |
| 0.5 | 0.01 | 500 | 5 | 0.12437 | 0.12939 | 0.12939 | -0.1941 | -0.2147 |
| 0.5 | 0.01 | 1000 | 10 | 0.12682 | 0.12939 | 0.12939 | -0.1988 | -0.2185 |
| 0.5 | 0.01 | 2000 | 20 | 0.12809 | 0.12939 | 0.12939 | -0.2012 | -0.2204 |
| 0.5 | 0.01 | 5000 | 50 | 0.12887 | 0.12939 | 0.12939 | -0.2026 | -0.2215 |
| 0.5 | 0.01 | 10000 | 100 | 0.12913 | 0.12939 | 0.12939 | -0.2031 | -0.2219 |
| 0.5 | 0.01 | 20000 | 200 | 0.12926 | 0.12939 | 0.12939 | -0.2033 | -0.2220 |
| 0.5 | 0.05 | 60 | 3 | 0.23170 | 0.24379 | 0.24379 | -0.1488 | -0.2096 |
| 0.5 | 0.05 | 100 | 5 | 0.23624 | 0.24379 | 0.24379 | -0.1548 | -0.2147 |
| 0.5 | 0.05 | 200 | 10 | 0.23990 | 0.24379 | 0.24379 | -0.1594 | -0.2185 |
| 0.5 | 0.05 | 400 | 20 | 0.24182 | 0.24379 | 0.24379 | -0.1618 | -0.2204 |
| 0.5 | 0.05 | 1000 | 50 | 0.24299 | 0.24379 | 0.24379 | -0.1632 | -0.2215 |
| 0.5 | 0.05 | 2000 | 100 | 0.24339 | 0.24379 | 0.24379 | -0.1636 | -0.2219 |
| 0.5 | 0.05 | 4000 | 200 | 0.24359 | 0.24379 | 0.24379 | -0.1639 | -0.2220 |
| 0.5 | 0.25 | 12 | 3 | 0.46793 | 0.48110 | 0.48110 | -0.0821 | -0.2096 |
| 0.5 | 0.25 | 20 | 5 | 0.47249 | 0.48110 | 0.48110 | -0.0895 | -0.2147 |
| 0.5 | 0.25 | 40 | 10 | 0.47653 | 0.48110 | 0.48110 | -0.0950 | -0.2185 |
| 0.5 | 0.25 | 80 | 20 | 0.47875 | 0.48110 | 0.48110 | -0.0977 | -0.2204 |
| 0.5 | 0.25 | 200 | 50 | 0.48014 | 0.48110 | 0.48110 | -0.0994 | -0.2215 |
| 0.5 | 0.25 | 400 | 100 | 0.48062 | 0.48110 | 0.48110 | -0.0999 | -0.2219 |
| 0.5 | 0.25 | 800 | 200 | 0.48086 | 0.48110 | 0.48110 | -0.1002 | -0.2220 |
| 0.7459 | 0.003 | 1000 | 3 | 0.22999 | 0.24728 | 0.24728 | -0.2098 | -0.2322 |
| 0.7459 | 0.003 | 1667 | 5 | 0.23652 | 0.24728 | 0.24727 | -0.2174 | -0.2373 |
| 0.7459 | 0.003 | 3333 | 10 | 0.24177 | 0.24728 | 0.24729 | -0.2232 | -0.2411 |
| 0.7459 | 0.003 | 6667 | 20 | 0.24449 | 0.24728 | 0.24728 | -0.2261 | -0.2429 |
| 0.7459 | 0.003 | 16667 | 50 | 0.24616 | 0.24728 | 0.24728 | -0.2278 | -0.2440 |
| 0.7459 | 0.003 | 33333 | 100 | 0.24672 | 0.24728 | 0.24728 | -0.2284 | -0.2443 |
| 0.7459 | 0.003 | 66667 | 200 | 0.24700 | 0.24728 | 0.24728 | -0.2287 | -0.2445 |
| 0.7459 | 0.01 | 300 | 3 | 0.29266 | 0.31262 | 0.31262 | -0.1916 | -0.2322 |
| 0.7459 | 0.01 | 500 | 5 | 0.30015 | 0.31262 | 0.31262 | -0.1994 | -0.2373 |
| 0.7459 | 0.01 | 1000 | 10 | 0.30620 | 0.31262 | 0.31262 | -0.2054 | -0.2411 |
| 0.7459 | 0.01 | 2000 | 20 | 0.30936 | 0.31262 | 0.31262 | -0.2083 | -0.2429 |
| 0.7459 | 0.01 | 5000 | 50 | 0.31131 | 0.31262 | 0.31262 | -0.2101 | -0.2440 |
| 0.7459 | 0.01 | 10000 | 100 | 0.31196 | 0.31262 | 0.31262 | -0.2107 | -0.2443 |
| 0.7459 | 0.01 | 20000 | 200 | 0.31229 | 0.31262 | 0.31262 | -0.2110 | -0.2445 |
| 0.7459 | 0.05 | 60 | 3 | 0.41353 | 0.43601 | 0.43601 | -0.1547 | -0.2322 |
| 0.7459 | 0.05 | 100 | 5 | 0.42177 | 0.43601 | 0.43601 | -0.1634 | -0.2373 |
| 0.7459 | 0.05 | 200 | 10 | 0.42860 | 0.43601 | 0.43601 | -0.1699 | -0.2411 |
| 0.7459 | 0.05 | 400 | 20 | 0.43224 | 0.43601 | 0.43601 | -0.1732 | -0.2429 |
| 0.7459 | 0.05 | 1000 | 50 | 0.43449 | 0.43601 | 0.43601 | -0.1751 | -0.2440 |
| 0.7459 | 0.05 | 2000 | 100 | 0.43525 | 0.43601 | 0.43601 | -0.1758 | -0.2443 |
| 0.7459 | 0.05 | 4000 | 200 | 0.43563 | 0.43601 | 0.43601 | -0.1761 | -0.2445 |
| 0.7459 | 0.25 | 12 | 3 | 0.61386 | 0.63426 | 0.63426 | -0.0965 | -0.2322 |
| 0.7459 | 0.25 | 20 | 5 | 0.62051 | 0.63426 | 0.63426 | -0.1085 | -0.2373 |
| 0.7459 | 0.25 | 40 | 10 | 0.62683 | 0.63426 | 0.63426 | -0.1172 | -0.2411 |
| 0.7459 | 0.25 | 80 | 20 | 0.63041 | 0.63426 | 0.63426 | -0.1215 | -0.2429 |
| 0.7459 | 0.25 | 200 | 50 | 0.63269 | 0.63426 | 0.63426 | -0.1242 | -0.2440 |
| 0.7459 | 0.25 | 400 | 100 | 0.63347 | 0.63426 | 0.63426 | -0.1250 | -0.2443 |
| 0.7459 | 0.25 | 800 | 200 | 0.63387 | 0.63426 | 0.63426 | -0.1255 | -0.2445 |
| 0.9 | 0.003 | 1000 | 3 | 0.45512 | 0.48507 | 0.48507 | -0.1852 | -0.2375 |
| 0.9 | 0.003 | 1667 | 5 | 0.46611 | 0.48507 | 0.48506 | -0.1954 | -0.2424 |
| 0.9 | 0.003 | 3333 | 10 | 0.47523 | 0.48507 | 0.48507 | -0.2030 | -0.2459 |
| 0.9 | 0.003 | 6667 | 20 | 0.48005 | 0.48507 | 0.48507 | -0.2068 | -0.2476 |
| 0.9 | 0.003 | 16667 | 50 | 0.48304 | 0.48507 | 0.48507 | -0.2091 | -0.2486 |
| 0.9 | 0.003 | 33333 | 100 | 0.48405 | 0.48507 | 0.48507 | -0.2098 | -0.2490 |
| 0.9 | 0.003 | 66667 | 200 | 0.48456 | 0.48507 | 0.48507 | -0.2102 | -0.2491 |
| 0.9 | 0.01 | 300 | 3 | 0.51128 | 0.54197 | 0.54197 | -0.1699 | -0.2375 |
| 0.9 | 0.01 | 500 | 5 | 0.52236 | 0.54197 | 0.54197 | -0.1809 | -0.2424 |
| 0.9 | 0.01 | 1000 | 10 | 0.53172 | 0.54197 | 0.54197 | -0.1891 | -0.2459 |
| 0.9 | 0.01 | 2000 | 20 | 0.53674 | 0.54197 | 0.54197 | -0.1932 | -0.2476 |
| 0.9 | 0.01 | 5000 | 50 | 0.53985 | 0.54197 | 0.54197 | -0.1957 | -0.2486 |
| 0.9 | 0.01 | 10000 | 100 | 0.54091 | 0.54197 | 0.54197 | -0.1965 | -0.2490 |
| 0.9 | 0.01 | 20000 | 200 | 0.54144 | 0.54197 | 0.54197 | -0.1969 | -0.2491 |
| 0.9 | 0.05 | 60 | 3 | 0.60740 | 0.63736 | 0.63736 | -0.1410 | -0.2375 |
| 0.9 | 0.05 | 100 | 5 | 0.61770 | 0.63736 | 0.63736 | -0.1542 | -0.2424 |
| 0.9 | 0.05 | 200 | 10 | 0.62691 | 0.63736 | 0.63736 | -0.1639 | -0.2459 |
| 0.9 | 0.05 | 400 | 20 | 0.63198 | 0.63736 | 0.63736 | -0.1687 | -0.2476 |
| 0.9 | 0.05 | 1000 | 50 | 0.63517 | 0.63736 | 0.63736 | -0.1716 | -0.2486 |
| 0.9 | 0.05 | 2000 | 100 | 0.63626 | 0.63736 | 0.63736 | -0.1726 | -0.2490 |
| 0.9 | 0.05 | 4000 | 200 | 0.63680 | 0.63736 | 0.63736 | -0.1730 | -0.2491 |
| 0.9 | 0.25 | 12 | 3 | 0.74820 | 0.77218 | 0.77218 | -0.0932 | -0.2375 |
| 0.9 | 0.25 | 20 | 5 | 0.75477 | 0.77218 | 0.77218 | -0.1127 | -0.2424 |
| 0.9 | 0.25 | 40 | 10 | 0.76238 | 0.77218 | 0.77218 | -0.1270 | -0.2459 |
| 0.9 | 0.25 | 80 | 20 | 0.76701 | 0.77218 | 0.77218 | -0.1339 | -0.2476 |
| 0.9 | 0.25 | 200 | 50 | 0.77005 | 0.77218 | 0.77218 | -0.1380 | -0.2486 |
| 0.9 | 0.25 | 400 | 100 | 0.77111 | 0.77218 | 0.77218 | -0.1394 | -0.2490 |
| 0.9 | 0.25 | 800 | 200 | 0.77164 | 0.77218 | 0.77218 | -0.1401 | -0.2491 |

So, to answer §6.2 directly: the expected precision of the top-$\mathrm{round}(pN)$ set depends on $N$ only through $K=\mathrm{round}(pN)$, as a deficit of about $\kappa/K$ with $\kappa$ between $-0.25$ and $-0.08$ for these $p,\rho$. At $N\ge10^3$ and $p\ge1\%$ the deficit is below 2 % of the value; at $p=0.3\%$ and $N=10^3$ ($K=3$) it is 7 %. The rounding of $pN$ itself has no visible effect (columns 6 and 7 differ in the fifth digit).

**Accuracy of `P2_diag` deep in the tail.** The Owen-$T$ form cancels two numbers of size $\bar\Phi(a)$.
Relative error against a tail-accurate quadrature (my `fk.cells`): below $10^{-11}$ for $a\le9$ at
$\rho=0.7459$, and below $10^{-12}$ for $a\le7$ at $\rho=0.5$; $4.5\times10^{-3}$ at $a=12,\rho=0.5$; meaningless
at $a=15,\rho=0.5$. In the handoff range ($N\le10^6$, so $a\le 4.8$) the error is below $10^{-12}$.
This is a limit of the formula far outside the range, not a bug.

---

## 3. Two-committee disagreement (§6.3)

Committee scores $(S^{(1)},S^{(2)})$ of one paper are standard bivariate normal with correlation
$r_{12}$ ($=\rho^2$ with $u$ redrawn). Each committee accepts $A=\alpha N$ papers. By §2 with $\rho\to r_{12}$:
$$D(\alpha,r_{12})=P(\mathrm{rej}_2\mid\mathrm{acc}_1)=1-\frac{P_2(z_\alpha,z_\alpha;r_{12})}{\alpha}.$$
The papers accepted by exactly one committee number $2(A-\text{overlap})=2A\,D$, so the share of
all papers with inconsistent decisions is
$$I(\alpha,r_{12})=2\alpha D=2\big(\alpha-P_2(z_\alpha,z_\alpha;r_{12})\big).$$
**Inverse map.** $\partial P_2(a,b;r)/\partial r=\phi_2(a,b;r)>0$ (Plackett's identity), so $D$ is strictly
decreasing in $r_{12}$ and the inverse is unique; `invert_disagreement` brackets it on $(-1,1)$.
Then $\rho^2=r_{12}$ (with $u$ redrawn) and $\sigma_\varepsilon$ follows from §1.

**Symmetry.** $P_2(-z,-z;r)=1-2(1-\alpha)+P_2(z,z;r)$ when $\bar\Phi(z)=\alpha$. Hence
$I(1-\alpha)=I(\alpha)$: the inconsistent share is symmetric about $\alpha=1/2$, where it equals
$1/2-\arcsin(r_{12})/\pi$ (Sheppard). Checked: max $\lvert I(\alpha)-I(1-\alpha)\rvert=6\times10^{-16}$ on a grid;
$I(1/2)=0.312221$ both ways at $r_{12}=0.5563$.

Calibration values (only as a check of `analytic.py`):

| experiment | $\alpha$ | inconsistent share | $D$ | $r_{12}=\rho^2$ | $\rho$ |
|---|---|---|---|---|---|
| NeurIPS 2021 | 0.227 | 0.2302 | 0.5070 | 0.5563 | 0.7459 |
| NeurIPS 2014, raw table | 0.2620 | 0.2590 | 0.4943 | 0.5265 | 0.7256 |
| NeurIPS 2014, quoted | 0.225 | 0.2590 | 0.5756 | 0.4362 | 0.6604 |

The repository test `test_inversions_round_trip` checks the inverse; `test_simulator_matches_closed_forms`
checks $D$ against the simulator. My Gaussian runs (§13) check $D$ again at $N$ from $10^3$ to $10^6$.

---

## 4. Fixed-number precision (§6.4)

### 4.1 Exact finite-$N$ formula

Let $M$ be the size of the true set ($M=K$ for precision; $M=2K,10K,\mathrm{round}(0.01N)$ give the
containment metrics of §6). By exchangeability,
$$E\lvert\mathrm{Top}_K(S)\cap\mathrm{Top}_M(Q)\rvert=N\,P(\text{paper 1 has score rank}\le K\text{ and quality rank}\le M).$$
Condition on $(Q_1,S_1)=(q,s)$. The other $N-1$ papers are iid. Let $B$ be the number of them with
$S>s$; $B\sim\mathrm{Bin}(N-1,\bar\Phi(s))$. Given $B=b$, the $b$ papers above in score are iid from the law
of $(Q,S)$ given $S>s$, so each has $Q>q$ with probability
$$\pi_1(q,s)=P(Q>q\mid S>s)=P_2(q,s;\rho)/\bar\Phi(s);$$
the other $N-1-b$ papers have $Q>q$ with probability
$$\pi_0(q,s)=P(Q>q\mid S<s)=\big(\bar\Phi(q)-P_2(q,s;\rho)\big)/\Phi(s).$$
The number $A$ of other papers with higher quality is then $\mathrm{Bin}(b,\pi_1)+\mathrm{Bin}(N-1-b,\pi_0)$, the two
parts independent. Therefore, exactly,
$$\boxed{E\lvert\mathrm{Top}_K(S)\cap\mathrm{Top}_M(Q)\rvert=N\iint\phi_2(q,s;\rho)\sum_{b=0}^{K-1}\mathrm{Bin}(b;N-1,\bar\Phi(s))\;P\big[\mathrm{Bin}(b,\pi_1)+\mathrm{Bin}(N-1-b,\pi_0)\le M-1\big]\,dq\,ds}$$
and $\mathrm{prec}_K(N)$ is this with $M=K$, divided by $K$. (This conditions on the paper's own
pair rather than on the $K$-th largest score; the two are equivalent, and this one needs no
special treatment of the boundary paper.)

**Numerical evaluation** (`fk.overlap_exact`).
- Coordinates $t=\log(N\bar\Phi(q))$, $u=\log(N\bar\Phi(s))$: then $N\phi_2\,dq\,ds=g(q,s)\,e^{t+u}/N\,dt\,du$. The
  integrand turns on where the expected counts $e^t,e^u$ fall below $M$ and $K$, and decays like
  $e^{c(t+u)}$ as $t,u\to-\infty$. Composite Gauss–Legendre: fine panels (width about $2\sqrt K$ in
  $e^u$) over $e^u\in[K-9\sqrt K,\,K+12\sqrt K+40]$, geometric panels down to $e^u=e^{-46}$; the same in $t$
  with $M$. Thresholds come from `scipy.special.ndtri_exp`, so the code works for $N$ up to $10^{300}$.
- The orthant cells $P_2$, $\bar\Phi(q)-P_2$ must be accurate in relative terms far in the tail. The
  code anchors on the larger threshold and integrates its conditional tail
  ($Y=k+w/k$, density $\propto e^{-w-w^2/2k^2}$), and uses Owen's $T$ only when both thresholds are below 2.5.
  Check against 40-digit mpmath at 60 random points with thresholds up to 14 and $\rho$ up to 0.97
  (`check_cells.py`): worst relative error $4\times10^{-11}$ for $P_2$, $4\times10^{-9}$ for $\bar\Phi(q)-P_2$.
- The binomial sum costs $O(M+K^2)$ per node: one log-space binomial table for $b=0$, then the
  recursions $f_{m-1}(j)=f_m(j)(m-j)/(m(1-\pi_0))$, $F_{m-1}(j)=F_m(j)+\pi_0 f_{m-1}(j)$ in $b$ and a convolution
  update for $\mathrm{Bin}(b,\pi_1)$. Only the window $j\in[M-K,M-1]$ is kept. All in log space with
  `log1p`, so $N=10^{100}$ is no harder than $N=10^3$.
- A slow reference implementation (full $K\times M$ binomial tables) agrees with the fast one to
  $3\times10^{-15}$ relative at 8 test points (`t_fast.py`).

**Checks of the exact formula.**

| check | result |
|---|---|
| $\rho=0$: the exact answer is $KM/N$ | relative error $\le2\times10^{-10}$ for $(N,K,M)$ from $(10,3,3)$ to $(10^{50},3,3)$, including $(10^3,10,50)$ |
| $N=2,K=1$: $\tfrac12+\arcsin(\rho)/\pi$ | error $6\times10^{-9}$ ($\rho=0.3$), $4\times10^{-9}$ (0.7459), $4\times10^{-7}$ (0.9) on the default grid; $9\times10^{-11}$, $2\times10^{-10}$, $3\times10^{-9}$ on a 6x finer grid (the slow convergence is the endpoint $e^t\to N$, present only for tiny $N$) |
| $N=3$: identity $\mathrm{prec}_2(3)=(1+\mathrm{prec}_1(3))/2$ ($\lvert\mathrm{Top}_2\cap\mathrm{Top}_2\rvert=1+1\{\text{same bottom paper}\}$, and the bottom pair agrees as often as the top pair) | residual $-5.8\times10^{-8}$, $-1.8\times10^{-8}$, $8.7\times10^{-7}$ at $\rho=0.3,0.7459,0.9$ on the default grid; $-5.8\times10^{-10}$, $-3.0\times10^{-10}$, $3.9\times10^{-9}$ on the finer grid (`check_N3_identity.py`) |
| $N=3$: $\mathrm{prec}_1=3P(Q_1>Q_{2,3},S_1>S_{2,3})$ and $P(\text{best}\in\mathrm{Top}_2)=1-3P(Q_1>Q_{2,3},S_1<S_{2,3})$, 4-dimensional orthant probabilities by scipy's Genz algorithm | differences $\le6.7\times10^{-8}$ at $\rho=0.3,0.7459,0.9$ (`check_smallN.py`, `out/check_smallN.json`) |
| brute-force Monte Carlo (own numpy code, not the repository simulator): $N=3,5,10,50$, $K$ up to 10, precision and best paper, $\rho=0.3,0.7459,0.9$, $10^6$ to $2\times10^7$ replicates | 84 comparisons; largest $\lvert z\rvert=2.17$; 2 of 84 beyond 2 (about 4 expected by chance) |
| grid refinement ($n_{\rm per}=8\to16$, panels $\times2$) | relative change $\le3\times10^{-10}$ at $N=10^6,K=30$; $10^{-16}$ at $N=10^4,K=100$ |
| repository simulator | §13, Table 13a |

### 4.2 The point-process limit

Fix $K$ and $M$ and let $N\to\infty$. Put
$$q=b_N+x/a_N,\qquad s=b_N+y/a_N .$$
**Step 1: each margin becomes a Poisson process.** $\log\bar\Phi(b+\delta)-\log\bar\Phi(b)=-h(b)\delta-h'(b)\delta^2/2-\dots$
with $h=\phi/\bar\Phi$, $h'=h(h-b)$. With $\delta=x/a_N$ and $a_N=h(b_N)$,
$$N\bar\Phi(q)=e^{-x}\Big(1-\frac{x^2}{2b_N^2}+O(b_N^{-4})\Big).$$
So the expected number of papers with quality above level $x$ is $e^{-x}$: the top qualities, in
$x$-units, form a Poisson process with intensity $e^{-x}dx$ (the Gumbel limit). The same holds for
the top scores in $y$-units.

**Step 2: the joint intensity, and why the two processes decouple.** The expected number of papers
with rescaled pair in $dx\,dy$ is $N\phi_2(q,s)\,dq\,ds$. Expand the exponent:
$$q^2-2\rho qs+s^2=2(1-\rho)b^2+2(1-\rho)\frac{b}{a}(x+y)+\frac{x^2-2\rho xy+y^2}{a^2}.$$
Divide by $2\tau^2=2(1-\rho)(1+\rho)$ and use $dq\,ds=dx\,dy/a^2$:
$$N\phi_2(q,s)\,dq\,ds=\varepsilon_N\,e^{-c\frac{b}{a}(x+y)}\,e^{-\frac{x^2-2\rho xy+y^2}{2\tau^2a^2}}\,dx\,dy,\qquad
\varepsilon_N=\frac{N\phi_2(b,b)}{a^2}=\frac{e^{\rho b_N^2/(1+\rho)}}{N\tau}.$$
The last equality uses $a_N=N\phi(b_N)$. Since $e^{b_N^2/2}\approx N/(\sqrt{2\pi}\,b_N)$,
$\varepsilon_N\approx N^{-\kappa}(2\pi b_N^2)^{-\rho/(1+\rho)}/\tau\to0$. So only a vanishing number of papers
are extreme in both quality and score. This is the tail independence of the bivariate normal
(Ledford–Tawn coefficient $\eta=(1+\rho)/2$). The two marginal Poisson processes are asymptotically
independent; the papers that lie in both tops form a thin Poisson process with intensity
$\varepsilon_N e^{-c(x+y)}$.

**Step 3: the conditional-Gaussian reading of the same fact.** Given $S=s$ with $s\approx b_N$,
$Q\sim N(\rho s,\tau^2)$. Its mean sits $(1-\rho)b_N$ below the level $b_N$ that the true top papers
reach, and its SD is $\tau$, fixed. The chance to reach $b_N$ is
$\bar\Phi\big((1-\rho)b_N/\tau\big)=\bar\Phi(\sqrt\kappa\,b_N)\approx e^{-\kappa b_N^2/2}\approx N^{-\kappa}$, the rate above.

**Step 4: counting.** A paper at $(x,y)$ is in $\mathrm{Top}_M(Q)$ if fewer than $M$ other papers lie above
$x$; that count is Poisson($e^{-x}$). It is in $\mathrm{Top}_K(S)$ if the count above $y$, Poisson($e^{-y}$),
is below $K$. The two counts share only the papers above in both coordinates, whose mean is
$O(\varepsilon_N)$, so they are independent to leading order. Hence
$$E\lvert\mathrm{Top}_K(S)\cap\mathrm{Top}_M(Q)\rvert=\varepsilon_N\int\!\!\int e^{-c(x+y)}\,F_M(e^{-x})\,F_K(e^{-y})\,dx\,dy\;(1+o(1)),\qquad F_n(\lambda)=P(\mathrm{Pois}(\lambda)\le n-1).$$
**Step 5: the integral.** Put $\lambda=e^{-x}$ and use $F_n(\lambda)=P(G_n>\lambda)$ for $G_n\sim\mathrm{Gamma}(n,1)$:
$$\int e^{-cx}F_n(e^{-x})\,dx=\int_0^\infty\lambda^{c-1}P(G_n>\lambda)\,d\lambda=\frac{E[G_n^{\,c}]}{c}=\frac{\Gamma(n+c)}{c\,\Gamma(n)}=I_n(c).$$
(Equivalently $\sum_{j=0}^{n-1}\Gamma(j+c)/j!=\Gamma(n+c)/(c\,\Gamma(n))$.) So
$$\boxed{E\lvert\mathrm{Top}_K(S)\cap\mathrm{Top}_M(Q)\rvert\sim\varepsilon_N\,I_K(c)\,I_M(c),\qquad
\mathrm{prec}_K(N)\sim\frac{\varepsilon_N\,I_K(c)^2}{K}=\frac{e^{\rho b_N^2/(1+\rho)}}{N\sqrt{1-\rho^2}}\,\frac{(1+\rho)^2}{K}\Big[\frac{\Gamma(K+c)}{\Gamma(K)}\Big]^2.}$$

### 4.3 The leading law in $N$, with its prefactor

From $N\bar\Phi(b_N)=1$ and $\bar\Phi(b)=\phi(b)b^{-1}(1-b^{-2}+\dots)$:
$b_N^2=2L-\log(2\pi b_N^2)-2/b_N^2+\dots$ with $L=\log N$. So
$e^{\rho b_N^2/(1+\rho)}/N=N^{-\kappa}(2\pi b_N^2)^{-\rho/(1+\rho)}(1+O(b_N^{-2}))$ and $2\pi b_N^2\sim4\pi L$. Hence
$$\boxed{\mathrm{prec}_K(N)\sim C_K(\rho)\,(\log N)^{-\frac{\rho}{1+\rho}}\,N^{-\frac{1-\rho}{1+\rho}},\qquad
C_K(\rho)=\frac{(1+\rho)^{3/2}}{(1-\rho)^{1/2}}\,(4\pi)^{-\frac{\rho}{1+\rho}}\,\frac1K\Big[\frac{\Gamma(K+\frac1{1+\rho})}{\Gamma(K)}\Big]^2.}$$
- **Limit:** zero for every $\rho<1$ and every fixed $K$.
- **Rate:** the power $N^{-(1-\rho)/(1+\rho)}$ times the slowly varying $(\log N)^{-\rho/(1+\rho)}$. The
  exponent falls from 1 at $\rho=0$ (pure chance, $\mathrm{prec}=K/N$) to 0 as $\rho\to1$.
- **Sanity checks of the constant:** $\rho\to0$ gives $C_K\to K$ and $\mathrm{prec}\to K/N$, exact for random
  selection. $K=1$ gives $C_1=(1+\rho)^{3/2}(1-\rho)^{-1/2}(4\pi)^{-\rho/(1+\rho)}\Gamma(1+c)^2$, which equals the
  best-paper constant of §7 at $K=1$, as it must (for $K=1$ the two events coincide).
- For large $K$, $[\Gamma(K+c)/\Gamma(K)]^2/K\approx K^{2c-1}$, so $C_K$ grows like $K^{(1-\rho)/(1+\rho)}$ and
  $\mathrm{prec}_K\approx \mathrm{const}\times(K/N)^{(1-\rho)/(1+\rho)}(\log N)^{-\rho/(1+\rho)}$.

Constants:

| $\rho$ | $\kappa$ | $\rho/(1+\rho)$ | $C_1$ | $C_5$ | $C_{10}$ | $C_{30}$ | $C_{100}$ |
|---|---|---|---|---|---|---|---|
| 0.5 | 0.3333 | 0.3333 | 0.9107 | 1.8288 | 2.3550 | 3.4468 | 5.1755 |
| 0.7459 | 0.1455 | 0.4272 | 1.2314 | 1.8686 | 2.1177 | 2.5255 | 3.0264 |
| 0.9 | 0.0526 | 0.4737 | 1.9663 | 2.5862 | 2.7496 | 2.9620 | 3.1742 |

### 4.4 The next corrections

There are two, of different kinds.

**(a) The $1/b_N^2$ (that is, $1/\log N$) correction.** Keep the next terms of Step 1 and Step 2:
$c\,b/a=c(1-b^{-2}+\dots)$; the quadratic term $-(x^2-2\rho xy+y^2)/(2\tau^2a^2)$; and
$F_n\big(e^{-x}(1-x^2/2b^2)\big)=F_n(e^{-x})+e^{-x}\frac{x^2}{2b^2}\pi_{n-1}(e^{-x})$ with $\pi_{n-1}$ the Poisson pmf.
The moments that appear are derivatives of $I_n(c)$ in $c$:
$\int x\,e^{-cx}F_n=-I_n D_n$, $\int x^2e^{-cx}F_n=I_n(D_n^2+P_n+c^{-2})$, with $D_n=\psi(n+c)-1/c$ and
$P_n=\psi'(n+c)$; and $\int x^2e^{-(1+c)x}\pi_{n-1}(e^{-x})\,dx=\frac{\Gamma(n+c)}{\Gamma(n)}(\psi(n+c)^2+P_n)$. Collecting:
$$E\lvert\mathrm{Top}_K(S)\cap\mathrm{Top}_M(Q)\rvert=\varepsilon_N I_KI_M\Big[1+\frac{\beta_{K,M}}{b_N^2}+\omega_{K,M}\varepsilon_N+\dots\Big],$$
$$\beta_{K,M}=-c(D_K+D_M)-\frac{D_K^2+D_M^2-2\rho D_KD_M+P_K+P_M+2/c^2}{2\tau^2}+\frac c2\big(\psi(K+c)^2+\psi(M+c)^2+P_K+P_M\big).$$
For $M=K$ the $(\log K)^2$ terms cancel and
$$\beta_K=\frac{2\rho}{1+\rho}\psi(K+c)-\frac{\rho(3-\rho)}{1-\rho}-\frac{\rho\,\psi'(K+c)}{1-\rho^2}.$$
$\beta_K=0$ at $\rho=0$, as it must. The term $-\rho(3-\rho)/(1-\rho)$ dominates and diverges as $\rho\to1$: the true
expansion parameter is $1/(\kappa b_N^2)=(1+\rho)/\big((1-\rho)\,2\log N\big)$, the inverse squared gap in
conditional-SD units. It is 0.30 at $\rho=0.7459,N=10^6$ and 0.84 at $\rho=0.9,N=10^6$, so the
asymptotic series is only moderately accurate in the handoff range.

**(b) The overlap correction, relative size $O(\varepsilon_N)=O(N^{-\kappa}\,\mathrm{polylog})$.** The papers above in
both coordinates (mean $\mu_{11}=\varepsilon_Ne^{-c(x+y)}/c^2$) enter both counts. To first order in $\mu_{11}$,
$P(A\le M-1,B\le K-1)=F_MF_K+\mu_{11}\pi_{M-1}\pi_{K-1}$ (the terms in $F$ cancel). Integrating,
$$\omega_{K,M}=(1+\rho)^2\frac{\Gamma(K+2c-1)\,\Gamma(M+2c-1)}{\Gamma(K)\,\Gamma(M)\,I_K(c)\,I_M(c)}>0.$$
This correction is positive (sharing makes both events likelier together). At $\rho=0$ it is
$O(1/N)$ and cancels against the binomial-versus-Poisson terms; for $\rho>0$ it dominates them.

**Size in terms of $\log N$.** Writing $b_N$ in terms of $L=\log N$,
$$\frac{\mathrm{prec}_K}{C_K L^{-\rho/(1+\rho)}N^{-\kappa}}=1+\frac{\rho}{1+\rho}\,\frac{\log(4\pi L)}{2L}+\frac{\beta_K-2\rho/(1+\rho)}{2L}+O\Big(\frac{(\log L)^2}{L^2}\Big)+\omega_K\varepsilon_N .$$
So the first correction to the pure law is of relative order $\log\log N/\log N$, and the
second-order coefficients are large (fitted $\gamma_K$ in Table 4b: about 34 at $\rho=0.5$, 190 at
$\rho=0.7459$, 1400 at $\rho=0.9$, for $K=1$).

**Numerical verification at very large $N$.** The exact quadrature works at any $N$, so I test the
asymptotics at $N$ up to $10^{300}$ (Table 4a and 4b, from `run_prec_table.py`).
- `exact/lead(b)` $\to1$: at $N=10^{300}$ it is 0.9979 ($\rho=0.5,K=1$), 0.9943 ($\rho=0.7459$), 0.9838 ($\rho=0.9$).
  `exact/pure` $\to1$ too (0.9996, 0.9964, 0.9862 at $10^{300}$). So the leading law and its prefactor are right.
- The coefficient $\beta_K$: I form $b_N^2(\text{indep}/\text{lead}-1)$, where "indep" is the point-process
  integral of Step 4 with the full Gaussian exponent (no linearisation) but without the overlap
  cell. A three-term fit $\beta+\gamma/b^2+\delta/b^4$ on $N=10^{100},10^{200},10^{300}$ returns $\beta$ to 3 or 4
  digits (Table 4b): for example $-8.005$ against the formula's $-8.006$ ($\rho=0.7459,K=1$), $-23.151$
  against $-23.169$ ($\rho=0.9,K=1$), $0.565$ against $0.565$ ($\rho=0.5,K=100$).
- The coefficient $\omega_K$: `exact/indep - 1` against $\omega_K\varepsilon_N$ (Table 4a):
  $2.391\times10^{-2}$ against $2.574\times10^{-2}$ at $N=10^6$, $2.375\times10^{-3}$ against $2.510\times10^{-3}$ at $10^{12}$,
  $3.91\times10^{-6}$ against $4.01\times10^{-6}$ at $10^{30}$ ($\rho=0.7459,K=1$). The ratio tends to 1 at the
  expected $1/b^2$ rate.

**Table 4a** (`out/prec_table_*.jsonl`). exact = finite-$N$ quadrature of §4.1; pure = $C_K(\log N)^{-\rho/(1+\rho)}N^{-\kappa}$; lead(b) = $\varepsilon_NI_K^2/K$; indep = Step-4 integral with the full Gaussian exponent and independent Poisson counts; pct = $P_2(z_{K/N},z_{K/N};\rho)/(K/N)$ computed tail-accurately (it underflows at $10^{300}$, shown nan).

| rho | K | N | exact | exact/pure | exact/lead(b) | exact/(R_K pct(K/N)) | exact/indep - 1 | omega eps_N |
|---|---|---|---|---|---|---|---|---|
| 0.5 | 1 | 1e+03 | 0.044297 | 0.9263 | 0.8673 | 1.0018 | 2.611e-02 | 2.726e-02 |
| 0.5 | 1 | 1e+04 | 0.018845 | 0.9345 | 0.8854 | 0.9919 | 1.089e-02 | 1.136e-02 |
| 0.5 | 1 | 1e+05 | 0.0081925 | 0.9428 | 0.9005 | 0.9891 | 4.666e-03 | 4.855e-03 |
| 0.5 | 1 | 1e+06 | 0.0036065 | 0.9502 | 0.9127 | 0.9887 | 2.033e-03 | 2.109e-03 |
| 0.5 | 1 | 1e+12 | 2.936e-05 | 0.9746 | 0.9516 | 0.9929 | 1.613e-05 | 1.646e-05 |
| 0.5 | 1 | 1e+30 | 2.1996e-11 | 0.9910 | 0.9795 | 0.9970 | 1.188e-11 | 1.198e-11 |
| 0.5 | 1 | 1e+100 | 6.8831e-35 | 0.9980 | 0.9937 | 0.9991 | 2.953e-14 | 3.696e-35 |
| 0.5 | 1 | 1e+300 | 1.0298e-101 | 0.9996 | 0.9979 | nan | 1.887e-14 | 5.507e-102 |
| 0.5 | 5 | 1e+03 | 0.095198 | 0.9914 | 0.9281 | 1.0021 | 1.020e-02 | 9.517e-03 |
| 0.5 | 5 | 1e+04 | 0.04012 | 0.9907 | 0.9387 | 0.9983 | 4.200e-03 | 3.966e-03 |
| 0.5 | 5 | 1e+05 | 0.017305 | 0.9917 | 0.9471 | 0.9971 | 1.774e-03 | 1.695e-03 |
| 0.5 | 5 | 1e+06 | 0.0075688 | 0.9930 | 0.9538 | 0.9969 | 7.641e-04 | 7.363e-04 |
| 0.5 | 5 | 1e+12 | 6.0383e-05 | 0.9982 | 0.9745 | 0.9981 | 5.848e-06 | 5.749e-06 |
| 0.5 | 5 | 1e+30 | 4.4611e-11 | 1.0009 | 0.9892 | 0.9992 | 4.204e-12 | 4.184e-12 |
| 0.5 | 5 | 1e+100 | 1.3864e-34 | 1.0010 | 0.9967 | 0.9998 | 6.817e-14 | 1.291e-35 |
| 0.5 | 5 | 1e+300 | 2.0701e-101 | 1.0006 | 0.9989 | nan | 4.086e-14 | 1.923e-102 |
| 0.5 | 10 | 1e+03 | 0.12682 | 1.0256 | 0.9602 | 1.0020 | 6.723e-03 | 6.000e-03 |
| 0.5 | 10 | 1e+04 | 0.053043 | 1.0172 | 0.9638 | 0.9994 | 2.748e-03 | 2.500e-03 |
| 0.5 | 10 | 1e+05 | 0.022769 | 1.0133 | 0.9678 | 0.9986 | 1.153e-03 | 1.069e-03 |
| 0.5 | 10 | 1e+06 | 0.0099256 | 1.0113 | 0.9714 | 0.9984 | 4.939e-04 | 4.642e-04 |
| 0.5 | 10 | 1e+12 | 7.8479e-05 | 1.0075 | 0.9836 | 0.9990 | 3.729e-06 | 3.624e-06 |
| 0.5 | 10 | 1e+30 | 5.7659e-11 | 1.0046 | 0.9929 | 0.9996 | 2.656e-12 | 2.638e-12 |
| 0.5 | 10 | 1e+100 | 1.7872e-34 | 1.0022 | 0.9978 | 0.9999 | 1.754e-14 | 8.137e-36 |
| 0.5 | 10 | 1e+300 | 2.6666e-101 | 1.0010 | 0.9993 | nan | 3.262e-13 | 1.212e-102 |
| 0.5 | 30 | 1e+03 | 0.19754 | 1.0915 | 1.0219 | 1.0015 | 3.470e-03 | 2.885e-03 |
| 0.5 | 30 | 1e+04 | 0.081221 | 1.0642 | 1.0083 | 1.0001 | 1.403e-03 | 1.202e-03 |
| 0.5 | 30 | 1e+05 | 0.034535 | 1.0501 | 1.0029 | 0.9996 | 5.817e-04 | 5.139e-04 |
| 0.5 | 30 | 1e+06 | 0.014962 | 1.0416 | 1.0005 | 0.9995 | 2.469e-04 | 2.232e-04 |
| 0.5 | 30 | 1e+12 | 0.00011653 | 1.0221 | 0.9979 | 0.9996 | 1.824e-06 | 1.743e-06 |
| 0.5 | 30 | 1e+30 | 8.4869e-11 | 1.0103 | 0.9986 | 0.9999 | 5.949e-13 | 1.268e-12 |
| 0.5 | 30 | 1e+100 | 2.6202e-34 | 1.0038 | 0.9995 | 1.0000 | 1.160e-12 | 3.913e-36 |
| 0.5 | 30 | 1e+300 | 3.9051e-101 | 1.0015 | 0.9998 | nan | -5.651e-13 | 5.829e-103 |
| 0.5 | 100 | 1e+03 | 0.32357 | 1.1907 | 1.1147 | 1.0008 | 1.688e-03 | 1.293e-03 |
| 0.5 | 100 | 1e+04 | 0.12913 | 1.1268 | 1.0676 | 1.0002 | 6.740e-04 | 5.388e-04 |
| 0.5 | 100 | 1e+05 | 0.054135 | 1.0963 | 1.0470 | 0.9999 | 2.759e-04 | 2.303e-04 |
| 0.5 | 100 | 1e+06 | 0.023256 | 1.0782 | 1.0357 | 0.9998 | 1.158e-04 | 1.000e-04 |
| 0.5 | 100 | 1e+12 | 0.00017778 | 1.0385 | 1.0139 | 0.9999 | 8.328e-07 | 7.810e-07 |
| 0.5 | 100 | 1e+30 | 1.2822e-10 | 1.0165 | 1.0047 | 1.0000 | -3.043e-12 | 5.684e-13 |
| 0.5 | 100 | 1e+100 | 3.9414e-34 | 1.0056 | 1.0013 | 1.0000 | 1.880e-11 | 1.753e-36 |
| 0.5 | 100 | 1e+300 | 5.8672e-101 | 1.0021 | 1.0004 | nan | 4.254e-11 | 2.612e-103 |
| 0.7459 | 1 | 1e+03 | 0.16354 | 0.8288 | 0.7616 | 1.0250 | 9.156e-02 | 9.773e-02 |
| 0.7459 | 1 | 1e+04 | 0.10547 | 0.8450 | 0.7886 | 1.0040 | 5.665e-02 | 6.087e-02 |
| 0.7459 | 1 | 1e+05 | 0.069652 | 0.8582 | 0.8091 | 0.9926 | 3.638e-02 | 3.918e-02 |
| 0.7459 | 1 | 1e+06 | 0.046696 | 0.8696 | 0.8258 | 0.9863 | 2.391e-02 | 2.574e-02 |
| 0.7459 | 1 | 1e+12 | 0.0048937 | 0.9152 | 0.8875 | 0.9814 | 2.375e-03 | 2.510e-03 |
| 0.7459 | 1 | 1e+30 | 8.3479e-06 | 0.9621 | 0.9478 | 0.9907 | 3.908e-06 | 4.009e-06 |
| 0.7459 | 1 | 1e+100 | 3.3278e-16 | 0.9887 | 0.9832 | 0.9971 | 2.554e-14 | 1.541e-16 |
| 0.7459 | 1 | 1e+300 | 1.635e-45 | 0.9964 | 0.9943 | nan | 1.665e-14 | 7.485e-46 |
| 0.7459 | 5 | 1e+03 | 0.26134 | 0.8728 | 0.8021 | 1.0056 | 2.557e-02 | 2.297e-02 |
| 0.7459 | 5 | 1e+04 | 0.16865 | 0.8904 | 0.8310 | 1.0004 | 1.541e-02 | 1.431e-02 |
| 0.7459 | 5 | 1e+05 | 0.11129 | 0.9037 | 0.8520 | 0.9977 | 9.731e-03 | 9.209e-03 |
| 0.7459 | 5 | 1e+06 | 0.074482 | 0.9141 | 0.8681 | 0.9962 | 6.315e-03 | 6.049e-03 |
| 0.7459 | 5 | 1e+12 | 0.0076973 | 0.9487 | 0.9200 | 0.9953 | 6.003e-04 | 5.899e-04 |
| 0.7459 | 5 | 1e+30 | 1.2878e-05 | 0.9781 | 0.9635 | 0.9978 | 9.483e-07 | 9.422e-07 |
| 0.7459 | 5 | 1e+100 | 5.076e-16 | 0.9938 | 0.9883 | 0.9993 | 5.884e-14 | 3.621e-17 |
| 0.7459 | 5 | 1e+300 | 2.4854e-45 | 0.9982 | 0.9960 | nan | 3.619e-14 | 1.759e-46 |
| 0.7459 | 10 | 1e+03 | 0.3062 | 0.9023 | 0.8292 | 1.0037 | 1.507e-02 | 1.256e-02 |
| 0.7459 | 10 | 1e+04 | 0.19637 | 0.9148 | 0.8538 | 1.0006 | 8.896e-03 | 7.824e-03 |
| 0.7459 | 10 | 1e+05 | 0.12908 | 0.9249 | 0.8719 | 0.9990 | 5.551e-03 | 5.036e-03 |
| 0.7459 | 10 | 1e+06 | 0.08615 | 0.9329 | 0.8860 | 0.9981 | 3.575e-03 | 3.308e-03 |
| 0.7459 | 10 | 1e+12 | 0.0088285 | 0.9601 | 0.9311 | 0.9976 | 3.339e-04 | 3.225e-04 |
| 0.7459 | 10 | 1e+30 | 1.467e-05 | 0.9831 | 0.9686 | 0.9989 | 5.220e-07 | 5.152e-07 |
| 0.7459 | 10 | 1e+100 | 5.7617e-16 | 0.9954 | 0.9899 | 0.9997 | 1.910e-14 | 1.980e-17 |
| 0.7459 | 10 | 1e+300 | 2.8182e-45 | 0.9987 | 0.9966 | nan | 2.818e-13 | 9.620e-47 |
| 0.7459 | 30 | 1e+03 | 0.38866 | 0.9604 | 0.8826 | 1.0019 | 6.674e-03 | 4.875e-03 |
| 0.7459 | 30 | 1e+04 | 0.24541 | 0.9587 | 0.8947 | 1.0006 | 3.771e-03 | 3.036e-03 |
| 0.7459 | 30 | 1e+05 | 0.15993 | 0.9608 | 0.9058 | 0.9998 | 2.300e-03 | 1.954e-03 |
| 0.7459 | 30 | 1e+06 | 0.10613 | 0.9637 | 0.9152 | 0.9995 | 1.462e-03 | 1.284e-03 |
| 0.7459 | 30 | 1e+12 | 0.010715 | 0.9771 | 0.9476 | 0.9992 | 1.326e-04 | 1.252e-04 |
| 0.7459 | 30 | 1e+30 | 1.7624e-05 | 0.9904 | 0.9757 | 0.9996 | 2.043e-07 | 1.999e-07 |
| 0.7459 | 30 | 1e+100 | 6.8869e-16 | 0.9976 | 0.9921 | 0.9999 | 1.007e-12 | 7.684e-18 |
| 0.7459 | 30 | 1e+300 | 3.3635e-45 | 0.9995 | 0.9973 | nan | -4.764e-13 | 3.733e-47 |
| 0.7459 | 100 | 1e+03 | 0.50779 | 1.0471 | 0.9623 | 1.0009 | 2.876e-03 | 1.738e-03 |
| 0.7459 | 100 | 1e+04 | 0.31196 | 1.0169 | 0.9490 | 1.0003 | 1.504e-03 | 1.082e-03 |
| 0.7459 | 100 | 1e+05 | 0.20061 | 1.0058 | 0.9482 | 1.0000 | 8.870e-04 | 6.966e-04 |
| 0.7459 | 100 | 1e+06 | 0.13206 | 1.0007 | 0.9503 | 0.9999 | 5.532e-04 | 4.576e-04 |
| 0.7459 | 100 | 1e+12 | 0.013084 | 0.9956 | 0.9655 | 0.9997 | 4.843e-05 | 4.462e-05 |
| 0.7459 | 100 | 1e+30 | 2.1281e-05 | 0.9979 | 0.9831 | 0.9999 | 7.345e-08 | 7.127e-08 |
| 0.7459 | 100 | 1e+100 | 8.2718e-16 | 0.9999 | 0.9944 | 1.0000 | 1.673e-11 | 2.739e-18 |
| 0.7459 | 100 | 1e+300 | 4.0337e-45 | 1.0003 | 0.9981 | nan | 3.764e-11 | 1.331e-47 |
| 0.9 | 1 | 1e+03 | 0.3746 | 0.6845 | 0.6233 | 1.0796 | 2.261e-01 | 2.538e-01 |
| 0.9 | 1 | 1e+04 | 0.30229 | 0.7146 | 0.6619 | 1.0533 | 1.733e-01 | 1.929e-01 |
| 0.9 | 1 | 1e+05 | 0.24833 | 0.7366 | 0.6900 | 1.0350 | 1.371e-01 | 1.520e-01 |
| 0.9 | 1 | 1e+06 | 0.20649 | 0.7537 | 0.7118 | 1.0215 | 1.108e-01 | 1.225e-01 |
| 0.9 | 1 | 1e+12 | 0.077667 | 0.8146 | 0.7873 | 0.9856 | 3.800e-02 | 4.166e-02 |
| 0.9 | 1 | 1e+30 | 0.0062119 | 0.8908 | 0.8761 | 0.9779 | 2.813e-03 | 2.994e-03 |
| 0.9 | 1 | 1e+100 | 7.8348e-07 | 0.9605 | 0.9545 | 0.9914 | 3.389e-07 | 3.466e-07 |
| 0.9 | 1 | 1e+300 | 1.423e-17 | 0.9862 | 0.9838 | 0.9970 | 1.532e-14 | 6.108e-18 |
| 0.9 | 5 | 1e+03 | 0.48875 | 0.6790 | 0.6183 | 1.0111 | 5.282e-02 | 4.787e-02 |
| 0.9 | 5 | 1e+04 | 0.398 | 0.7153 | 0.6626 | 1.0065 | 3.892e-02 | 3.638e-02 |
| 0.9 | 5 | 1e+05 | 0.32937 | 0.7428 | 0.6958 | 1.0033 | 3.014e-02 | 2.867e-02 |
| 0.9 | 5 | 1e+06 | 0.27546 | 0.7645 | 0.7219 | 1.0010 | 2.402e-02 | 2.311e-02 |
| 0.9 | 5 | 1e+12 | 0.10523 | 0.8392 | 0.8111 | 0.9951 | 7.960e-03 | 7.858e-03 |
| 0.9 | 5 | 1e+30 | 0.0083886 | 0.9146 | 0.8996 | 0.9948 | 5.661e-04 | 5.648e-04 |
| 0.9 | 5 | 1e+100 | 1.0406e-06 | 0.9699 | 0.9639 | 0.9981 | 6.542e-08 | 6.538e-08 |
| 0.9 | 5 | 1e+300 | 1.878e-17 | 0.9896 | 0.9872 | 0.9993 | 3.419e-14 | 1.152e-18 |
| 0.9 | 10 | 1e+03 | 0.53172 | 0.6948 | 0.6327 | 1.0058 | 2.953e-02 | 2.434e-02 |
| 0.9 | 10 | 1e+04 | 0.43127 | 0.7291 | 0.6753 | 1.0034 | 2.116e-02 | 1.850e-02 |
| 0.9 | 10 | 1e+05 | 0.3561 | 0.7553 | 0.7075 | 1.0017 | 1.614e-02 | 1.458e-02 |
| 0.9 | 10 | 1e+06 | 0.29738 | 0.7763 | 0.7331 | 1.0005 | 1.275e-02 | 1.175e-02 |
| 0.9 | 10 | 1e+12 | 0.11315 | 0.8487 | 0.8203 | 0.9975 | 4.139e-03 | 3.996e-03 |
| 0.9 | 10 | 1e+30 | 0.0089781 | 0.9207 | 0.9056 | 0.9973 | 2.907e-04 | 2.872e-04 |
| 0.9 | 10 | 1e+100 | 1.1089e-06 | 0.9721 | 0.9662 | 0.9990 | 3.336e-08 | 3.325e-08 |
| 0.9 | 10 | 1e+300 | 1.9983e-17 | 0.9904 | 0.9880 | 0.9997 | 2.593e-13 | 5.859e-19 |
| 0.9 | 30 | 1e+03 | 0.60045 | 0.7284 | 0.6633 | 1.0023 | 1.213e-02 | 8.485e-03 |
| 0.9 | 30 | 1e+04 | 0.48171 | 0.7559 | 0.7002 | 1.0013 | 8.190e-03 | 6.448e-03 |
| 0.9 | 30 | 1e+05 | 0.39536 | 0.7784 | 0.7292 | 1.0007 | 6.075e-03 | 5.082e-03 |
| 0.9 | 30 | 1e+06 | 0.32887 | 0.7969 | 0.7526 | 1.0003 | 4.722e-03 | 4.096e-03 |
| 0.9 | 30 | 1e+12 | 0.12389 | 0.8626 | 0.8337 | 0.9992 | 1.483e-03 | 1.393e-03 |
| 0.9 | 30 | 1e+30 | 0.0097522 | 0.9284 | 0.9131 | 0.9991 | 1.025e-04 | 1.001e-04 |
| 0.9 | 30 | 1e+100 | 1.1979e-06 | 0.9749 | 0.9688 | 0.9997 | 1.167e-08 | 1.159e-08 |
| 0.9 | 30 | 1e+300 | 2.1547e-17 | 0.9913 | 0.9889 | 0.9999 | -4.324e-13 | 2.042e-19 |
| 0.9 | 100 | 1e+03 | 0.68755 | 0.7783 | 0.7087 | 1.0009 | 4.903e-03 | 2.699e-03 |
| 0.9 | 100 | 1e+04 | 0.54091 | 0.7921 | 0.7337 | 1.0005 | 2.970e-03 | 2.051e-03 |
| 0.9 | 100 | 1e+05 | 0.4397 | 0.8079 | 0.7568 | 1.0003 | 2.114e-03 | 1.617e-03 |
| 0.9 | 100 | 1e+06 | 0.36361 | 0.8222 | 0.7764 | 1.0001 | 1.607e-03 | 1.303e-03 |
| 0.9 | 100 | 1e+12 | 0.13506 | 0.8775 | 0.8481 | 0.9998 | 4.851e-04 | 4.431e-04 |
| 0.9 | 100 | 1e+30 | 0.010534 | 0.9357 | 0.9203 | 0.9997 | 3.292e-05 | 3.185e-05 |
| 0.9 | 100 | 1e+100 | 1.287e-06 | 0.9774 | 0.9714 | 0.9999 | 3.738e-09 | 3.687e-09 |
| 0.9 | 100 | 1e+300 | 2.3111e-17 | 0.9922 | 0.9898 | 1.0000 | 3.514e-11 | 6.497e-20 |

**Table 4b.** $b_N^2(\text{indep}/\text{lead}-1)$ at six values of $N$, the three-point fit of $\beta+\gamma/b^2+\delta/b^4$ on $N=10^{100},10^{200},10^{300}$, and $\beta_K$ from the formula.

| rho | K | N=1e6 | 1e12 | 1e30 | 1e100 | 1e200 | 1e300 | fit beta | formula beta | fit gamma (b^-4 coeff) |
|---|---|---|---|---|---|---|---|---|---|---|
| 0.5 | 1 | -2.014 | -2.398 | -2.690 | -2.849 | -2.885 | -2.897 | -2.921 | -2.921 | 34.1 |
| 0.5 | 5 | -1.059 | -1.261 | -1.413 | -1.495 | -1.514 | -1.520 | -1.533 | -1.533 | 17.6 |
| 0.5 | 10 | -0.657 | -0.811 | -0.927 | -0.990 | -1.005 | -1.009 | -1.019 | -1.019 | 13.5 |
| 0.5 | 30 | 0.005 | -0.106 | -0.187 | -0.231 | -0.241 | -0.244 | -0.251 | -0.251 | 9.3 |
| 0.5 | 100 | 0.803 | 0.689 | 0.617 | 0.581 | 0.573 | 0.570 | 0.565 | 0.565 | 7.4 |
| 0.7459 | 1 | -4.371 | -5.670 | -6.861 | -7.619 | -7.806 | -7.872 | -8.005 | -8.006 | 187.4 |
| 0.7459 | 5 | -3.104 | -3.987 | -4.791 | -5.299 | -5.425 | -5.469 | -5.558 | -5.558 | 125.3 |
| 0.7459 | 10 | -2.648 | -3.425 | -4.133 | -4.581 | -4.692 | -4.731 | -4.809 | -4.810 | 110.5 |
| 0.7459 | 30 | -1.946 | -2.601 | -3.196 | -3.573 | -3.666 | -3.698 | -3.764 | -3.764 | 92.7 |
| 0.7459 | 100 | -1.135 | -1.709 | -2.218 | -2.536 | -2.615 | -2.642 | -2.698 | -2.698 | 78.2 |
| 0.9 | 1 | -8.116 | -11.951 | -16.600 | -20.572 | -21.767 | -22.208 | -23.151 | -23.169 | 1357.9 |
| 0.9 | 5 | -6.665 | -9.666 | -13.264 | -16.318 | -17.234 | -17.572 | -18.294 | -18.308 | 1039.6 |
| 0.9 | 10 | -6.240 | -9.061 | -12.444 | -15.316 | -16.177 | -16.495 | -17.175 | -17.188 | 977.7 |
| 0.9 | 30 | -5.671 | -8.290 | -11.431 | -14.097 | -14.897 | -15.192 | -15.823 | -15.835 | 907.6 |
| 0.9 | 100 | -5.080 | -7.536 | -10.472 | -12.962 | -13.709 | -13.984 | -14.573 | -14.584 | 847.3 |

### 4.5 Cross-check with the fixed-percentile formula, and the finite-$K$ factor

As $z\to\infty$, $P_2(z,z;\rho)\sim\phi_2(z,z)(1+\rho)^2/z^2$ (the gradient of the exponent at $(z,z)$ is
$z/(1+\rho)$ in each coordinate). Put $z=z_{K/N}$, so $N\bar\Phi(z)=K$, $z=b_N+x_K/a_N$ with $e^{-x_K}\approx K$, and
$\phi_2(z,z)\approx\phi_2(b,b)K^{2c}$. Then
$$\mathrm{precision\_pct}(K/N)\sim\frac{\varepsilon_N}{K}\Big(\frac{K^c}{c}\Big)^2.$$
This is Step 4 with each Poisson count replaced by its mean, i.e. $F_K(e^{-y})$ replaced by
$1\{e^{-y}<K\}$: $\int e^{-cy}1\{e^{-y}<K\}dy=K^c/c$. So the fixed-percentile formula at $p=K/N$ is the
fixed-$K$ answer with deterministic thresholds, and
$$\boxed{\lim_{N\to\infty}\frac{\mathrm{prec}_K(N)}{\mathrm{precision\_pct}(K/N,\rho)}=R_K(\rho)=\Big[\frac{E[G_K^{\,c}]}{(EG_K)^c}\Big]^2=\Big[\frac{\Gamma(K+c)}{\Gamma(K)\,K^{c}}\Big]^2<1.}$$
$R_K<1$ by Jensen's inequality ($v\mapsto v^c$ is concave and the $K$-th arrival $G_K$ of the Poisson
process is random). Expansion: $R_K=1-c(1-c)/K+O(K^{-2})=1-\rho/\big((1+\rho)^2K\big)+\dots$.

| $\rho$ | $R_1$ | $R_5$ | $R_{10}$ | $R_{30}$ | $R_{100}$ |
|---|---|---|---|---|---|
| 0.5 | 0.8149 | 0.9571 | 0.9782 | 0.9926 | 0.9978 |
| 0.7459 | 0.7934 | 0.9525 | 0.9759 | 0.9919 | 0.9976 |
| 0.9 | 0.7874 | 0.9515 | 0.9754 | 0.9917 | 0.9975 |

So for best-paper-sized selections ($K\le5$) the fixed-percentile formula overstates precision by
5 to 21 %; for $K\ge30$ by under 1 %.

**The best practical approximation in the handoff range** is the product
$R_K(\rho)\times P_2(z_{K/N},z_{K/N};\rho)/(K/N)$. Its error against the exact value (Table 4a, column
`exact/(R_K pct(K/N))`), over $K\in\{1,5,10,30,100\}$ and $N\in[10^3,10^6]$, is at most 1.1 % at $\rho=0.5$,
2.5 % at $\rho=0.7459$ and 8 % at $\rho=0.9$ (the worst case is always $K=1,N=10^3$, where the overlap
term $\omega_1\varepsilon_N$ is 3 %, 10 % and 25 %). For $K\ge5$ it is at most 0.3 %, 0.6 % and 1.1 %.
By contrast, over the same range `exact/pure` lies in $[0.93,1.19]$, $[0.83,1.05]$ and $[0.68,0.82]$, and
`exact/lead(b)` in $[0.87,1.11]$, $[0.76,0.96]$ and $[0.62,0.78]$ for $\rho=0.5,0.7459,0.9$. The
point-process integral "indep" (no overlap cell) lies in $[1.000,1.026]$, $[1.001,1.092]$ and
$[1.002,1.226]$ of the exact value: the overlap cell is the main defect of the pure point-process
picture at small $N$ and large $\rho$.

### 4.6 Local log-log slope over $N=10^3$ to $10^6$

From the $b_N$-form, $d\log\varepsilon_N/d\log N=\frac{2\rho}{1+\rho}\frac{b_N}{a_N}-1$ (because $db_N/d\log N=1/a_N$).
So the local slope is
$$\frac{d\log\mathrm{prec}_K}{d\log N}=-\frac{1-\rho}{1+\rho}-\frac{2\rho}{1+\rho}\Big(1-\frac{b_N}{a_N}\Big)-\frac{2\beta_K}{b_N^4}+\dots\approx-\frac{1-\rho}{1+\rho}-\frac{2\rho}{(1+\rho)b_N^2}-\dots,$$
and the pure law gives $-\kappa-\rho/((1+\rho)\log N)$. The extra steepness decays only like $1/\log N$.

**Table 4c.** Local slopes from the exact values (centred differences on the handoff $N$ grid); pure-law slope $-\kappa-\rho/((1+\rho)\log N)$ at $N=3.2\times10^4$; secant slope from $10^{30}$ to $10^{100}$.

| rho | K | asympt -(1-rho)/(1+rho) | secant 1e3->1e6 | local at 2e3 | local at 3.2e4 | local at 5e5 | pure-law slope at 3.2e4 | slope 1e30->1e100 |
|---|---|---|---|---|---|---|---|---|
| 0.5 | 1 | -0.3333 | -0.3631 | -0.3730 | -0.3616 | -0.3557 | -0.3655 | -0.3358 |
| 0.5 | 5 | -0.3333 | -0.3665 | -0.3772 | -0.3651 | -0.3584 | -0.3655 | -0.3358 |
| 0.5 | 10 | -0.3333 | -0.3688 | -0.3807 | -0.3671 | -0.3598 | -0.3655 | -0.3358 |
| 0.5 | 30 | -0.3333 | -0.3736 | -0.3889 | -0.3712 | -0.3623 | -0.3655 | -0.3359 |
| 0.5 | 100 | -0.3333 | -0.3811 | -0.4034 | -0.3772 | -0.3657 | -0.3655 | -0.3359 |
| 0.7459 | 1 | -0.1455 | -0.1815 | -0.1924 | -0.1801 | -0.1728 | -0.1868 | -0.1486 |
| 0.7459 | 5 | -0.1455 | -0.1817 | -0.1920 | -0.1804 | -0.1736 | -0.1868 | -0.1486 |
| 0.7459 | 10 | -0.1455 | -0.1836 | -0.1949 | -0.1821 | -0.1748 | -0.1868 | -0.1487 |
| 0.7459 | 30 | -0.1455 | -0.1879 | -0.2023 | -0.1858 | -0.1771 | -0.1868 | -0.1487 |
| 0.7459 | 100 | -0.1455 | -0.1950 | -0.2157 | -0.1915 | -0.1804 | -0.1868 | -0.1487 |
| 0.9 | 1 | -0.0526 | -0.0862 | -0.0945 | -0.0853 | -0.0795 | -0.0983 | -0.0557 |
| 0.9 | 5 | -0.0526 | -0.0830 | -0.0905 | -0.0821 | -0.0770 | -0.0983 | -0.0558 |
| 0.9 | 10 | -0.0526 | -0.0841 | -0.0924 | -0.0831 | -0.0776 | -0.0983 | -0.0558 |
| 0.9 | 30 | -0.0526 | -0.0871 | -0.0976 | -0.0857 | -0.0792 | -0.0983 | -0.0559 |
| 0.9 | 100 | -0.0526 | -0.0922 | -0.1071 | -0.0898 | -0.0816 | -0.0983 | -0.0559 |

The asymptotic slope understates the decline in the range of interest. Over $10^3\to10^6$ the
exact secant slope is $-0.363$ to $-0.381$ at $\rho=0.5$ (asymptote $-0.333$), $-0.182$ to $-0.195$ at
$\rho=0.7459$ ($-0.146$), and $-0.083$ to $-0.092$ at $\rho=0.9$ ($-0.053$), for $K=1$ to 100. Larger $K$
gives a steeper local slope at small $N$. The pure law (with its log
factor) predicts the local slope at $3.2\times10^4$ within 0.012 ($\rho=0.5$), 0.007 ($\rho=0.7459$) and
0.016 ($\rho=0.9$), across $K=1$ to 100. Even at $N=10^{30}$ to $10^{100}$ the slope is still 1 to 6 % steeper than
the asymptote.

---

## 5. The mechanism (§6.5)

Three facts carry the whole story.

1. **Quality given score.** $E[Q\mid S=s]=\rho s$ and $\mathrm{SD}(Q\mid S=s)=\tau$ for every $s$. The concomitant of the
   $j$-th largest score therefore has $E[Q_{[j]}]=\rho\,E[S_{(j)}]$ and
   $\mathrm{Var}(Q_{[j]})=\rho^2\mathrm{Var}(S_{(j)})+\tau^2\approx\tau^2$ (since $\mathrm{Var}(S_{(1)})\approx\pi^2/(6b_N^2)\to0$).
2. **Where the top sits.** $E[S_{(1)}]=b_N+\gamma_E/a_N+\dots$ grows like $\sqrt{2\log N}$; the true top-$K$
   quality threshold $Q_{(K)}$ has the same law as $S_{(K)}$ (same marginal), $E[Q_{(K)}]\approx b_N-\log K/b_N$.
3. **The gap.** The top-scored paper's expected quality is $\rho\,E[S_{(1)}]$, so it falls short of the
   true top level by $(1-\rho)E[S_{(1)}]\approx(1-\rho)\sqrt{2\log N}$, which grows without bound, while the
   conditional SD $\tau$ stays fixed. In conditional-SD units the shortfall is
   $(1-\rho)b_N/\tau=\sqrt{\kappa}\,b_N$. The chance to bridge it is a Gaussian tail,
   $\bar\Phi(\sqrt\kappa b_N)\approx e^{-\kappa b_N^2/2}\approx N^{-\kappa}$. This is the exponent of §4.

The reverse view gives the same exponent: a truly best paper has $Q\approx b_N$ and score
$\rho b_N\pm\tau$, so it reaches the score cut $b_N$ only if its noise is about $(1-\rho)b_N/\tau$ SDs.

**Fixed percentile.** The cut is at $z_p$, fixed. A paper at the cut has expected quality $\rho z_p$;
the shortfall $(1-\rho)z_p/\tau$ is a constant (0.888 SD at $p=1\%$, $\rho=0.7459$). Nothing grows with $N$,
so precision is $N$-free (§2).

**Why noise "wins" at the top although its SD is fixed.** The spacing between the best and the
second-best quality shrinks like $1/b_N$ (0.287 at $N=10^3$, 0.198 at $10^6$), while the conditional
SD stays at $\tau$ (0.666 for $\rho=0.7459$). The number of papers whose quality lies within one
conditional SD below the true top-10 threshold grows (37 at $10^3$, 144 at $10^6$, 727 at $10^{12}$).
The selection must find the best few among a growing crowd of near-ties with a fixed resolution.

Exact numbers (`run_mech.py`, `out/mech.json`; order-statistic moments by quadrature):

| $\rho$ | $N$ | $E[S_{(1)}]$ | $\rho E[S_{(1)}]$ (exp. quality of top-scored) | $E[Q_{(10)}]$ (needed for top 10) | shortfall to $E[Q_{(1)}]$, in SD $\tau$ | same at the 10-th cut | $E[S_{(1)}]-E[S_{(2)}]$ | papers within $\tau$ below $E[Q_{(10)}]$ | $\bar\Phi(\text{shortfall})$ | exact $\mathrm{prec}_1$ |
|---|---|---|---|---|---|---|---|---|---|---|
| 0.5 | $10^3$ | 3.241 | 1.621 | 2.343 | 1.87 | 1.35 | 0.287 | 60 | 0.031 | 0.044 |
| 0.5 | $10^6$ | 4.863 | 2.431 | 4.276 | 2.81 | 2.47 | 0.198 | 316 | 0.0025 | 0.0036 |
| 0.7459 | $10^3$ | 3.241 | 2.418 | 2.343 | 1.24 | 0.89 | 0.287 | 37 | 0.108 | 0.164 |
| 0.7459 | $10^4$ | 3.852 | 2.873 | 3.104 | 1.47 | 1.18 | 0.246 | 64 | 0.071 | 0.105 |
| 0.7459 | $10^5$ | 4.384 | 3.270 | 3.731 | 1.67 | 1.42 | 0.218 | 99 | 0.047 | 0.070 |
| 0.7459 | $10^6$ | 4.863 | 3.627 | 4.276 | 1.86 | 1.63 | 0.198 | 144 | 0.032 | 0.047 |
| 0.7459 | $10^{12}$ | 7.113 | 5.305 | 6.713 | 2.71 | 2.56 | 0.138 | 727 | 0.0033 | 0.0049 |
| 0.9 | $10^3$ | 3.241 | 2.917 | 2.343 | 0.74 | 0.54 | 0.287 | 19 | 0.229 | 0.375 |
| 0.9 | $10^6$ | 4.863 | 4.377 | 4.276 | 1.12 | 0.98 | 0.198 | 52 | 0.132 | 0.206 |

The naive tail $\bar\Phi((1-\rho)E[S_{(1)}]/\tau)$ tracks the exact $\mathrm{prec}_1$ within a factor 1.4 to 1.6 and
falls at the same rate; the point-process prefactor of §4 accounts for the rest (the
exponential tilting of the noise and the randomness of both top values).

The optimizer's curse in this language: the top-scored paper is over-rated by
$E[S_{(1)}]-E[Q_{[1]}]=(1-\rho)E[S_{(1)}]$ standardised units, which grows like $\sqrt{\log N}$.

---

## 6. Containment in a fixed top percentile (§6.6)

**Fixed $p$, fixed $K$.** The $j$-th top-scored paper has $Q=\rho S_{(j)}+\tau Z$ with $S_{(j)}\approx b_N\to\infty$.
The true top-$p$ threshold $Q_{(\lceil pN\rceil)}\to z_p$, a constant. So $P(Q_{[j]}>z_p)\to1$:
$$\lim_{N\to\infty}\frac{\lvert\mathrm{Top}_K(S)\cap\mathrm{Top}_{pN}(Q)\rvert}{K}=1\qquad(\rho>0,\ \text{any fixed }p,K).$$
**Rate.** Put $S_{(j)}=b+x_j/a$, $w=(\rho b-z_p)/\tau$, $\gamma_N=\rho w/(a\tau)\to\rho^2/\tau^2$. Then
$\Phi\big((z_p-\rho S_{(j)})/\tau\big)\approx\bar\Phi(w)e^{-\gamma_Nx_j}$, and for the Poisson process $e^{-x_j}\sim\mathrm{Gamma}(j,1)$,
so $E[e^{-\gamma x_j}]=\Gamma(j+\gamma)/\Gamma(j)$. Summing over $j\le K$:
$$1-\text{share}\approx\bar\Phi(w_N)\,\frac{\Gamma(K+1+\gamma_N)}{(1+\gamma_N)\,\Gamma(K+1)},\qquad w_N=\frac{\rho b_N-z_p}{\tau}.$$
Since $w_N^2/2\approx\frac{\rho^2}{1-\rho^2}\log N-\frac{\rho z_p}{1-\rho^2}\sqrt{2\log N}+\dots$, the miss rate is
$N^{-\rho^2/(1-\rho^2)}$ times a factor $e^{+\rho z_p\sqrt{2\log N}/(1-\rho^2)}$ that grows faster than any power of $\log N$.
Convergence is therefore slow in practice (Table 6).

**Fixed multiple $M=mK$.** By §4.2, $E\lvert\mathrm{Top}_K(S)\cap\mathrm{Top}_{mK}(Q)\rvert\sim\varepsilon_NI_K(c)I_{mK}(c)$, so containment in the true
top $2K$ or $10K$ tends to **zero** at the same rate as precision, with
$$\frac{c_{mx}}{\mathrm{prec}_K}\to\frac{I_{mK}(c)}{I_K(c)}\approx m^{c}\quad(K\text{ large}).$$
The dividing line is $M\asymp N^{1-\rho^2}$: a top-scored paper has quality rank about $N\bar\Phi(\rho b_N)\asymp N^{1-\rho^2}$ (§8).
Containment in the true top $M$ tends to 1 if $M/N^{1-\rho^2}\to\infty$ and to 0 if $M$ is fixed.

**Mean true percentile.** $E[\Phi(Q)\mid S=s]=P(Q'<\rho s+\tau Z)=\Phi\big(\rho s/\sqrt{2-\rho^2}\big)$ with $Q'$ an independent
copy. So the mean percentile of $\mathrm{Top}_K(S)$ is exactly
$\frac1K\int N\phi(s)\,P(\mathrm{Bin}(N-1,\bar\Phi(s))\le K-1)\,\Phi(\rho s/\sqrt{2-\rho^2})\,ds$, and
$1-\text{pctl}\approx\bar\Phi(\rho b_N/\sqrt{2-\rho^2})\asymp N^{-\rho^2/(2-\rho^2)}$.

**Table 6.** Containment of Top_K(S) in the true top 1 % and 5 %, in the true top 2K and 10K, and the mean true percentile.

| rho | N | K | c1pct exact | c1pct det. threshold | c1pct asympt. | sim c1pct | c5pct det. | c5pct asympt. | c2x exact | c2x lead | c10x exact | c10x/prec | I_10K/I_K | pctl exact | sim pctl |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0.5 | 1e+03 | 1 | 0.2111 | 0.2121 | 0.0880 | 0.2058 ± 0.0040 | 0.4887 | 0.4477 | 0.07424 | 0.08513 | 0.2111 | 4.767 | 5.085 | 0.88775 | 0.8874 ± 0.0014 |
| 0.5 | 1e+03 | 5 | 0.1533 | 0.1543 | 0.2565 | 0.1516 ± 0.0016 | 0.4029 | 0.4616 | 0.1533 | 0.1646 | 0.403 | 4.234 | 4.734 | 0.85825 | 0.8577 ± 0.0007 |
| 0.5 | 1e+03 | 10 | 0.1268 | 0.1277 | 0.3279 | 0.1242 ± 0.0010 | 0.3572 | 0.4684 | 0.2031 | 0.2108 | 0.5186 | 4.089 | 4.688 | 0.83960 | 0.8395 ± 0.0006 |
| 0.5 | 1e+03 | 30 | 0.0877 | 0.0883 | 0.4305 | 0.0868 ± 0.0005 | 0.2799 | 0.4795 | 0.315 | 0.3074 | 0.7534 | 3.814 | 4.657 | 0.80145 | 0.8014 ± 0.0004 |
| 0.5 | 1e+04 | 1 | 0.3241 | 0.3241 | 0.2583 | 0.3243 ± 0.0047 | 0.6251 | 0.6058 | 0.03161 | 0.03547 | 0.09191 | 4.877 | 5.085 | 0.92598 | 0.9259 ± 0.0011 |
| 0.5 | 1e+04 | 5 | 0.2602 | 0.2603 | 0.3304 | 0.2590 ± 0.0020 | 0.5536 | 0.5872 | 0.06463 | 0.06859 | 0.1769 | 4.408 | 4.734 | 0.90761 | 0.9067 ± 0.0006 |
| 0.5 | 1e+04 | 10 | 0.2290 | 0.2291 | 0.3638 | 0.2285 ± 0.0013 | 0.5139 | 0.5774 | 0.08495 | 0.08785 | 0.229 | 4.317 | 4.688 | 0.89626 | 0.8960 ± 0.0004 |
| 0.5 | 1e+04 | 30 | 0.1796 | 0.1797 | 0.4150 | 0.1800 ± 0.0007 | 0.4440 | 0.5609 | 0.1296 | 0.1281 | 0.341 | 4.199 | 4.657 | 0.87370 | 0.8737 ± 0.0003 |
| 0.5 | 1e+05 | 1 | 0.4390 | 0.4389 | 0.4011 | 0.4428 ± 0.0050 | 0.7337 | 0.7239 | 0.01374 | 0.01516 | 0.04041 | 4.933 | 5.085 | 0.95040 | 0.9508 ± 0.0009 |
| 0.5 | 1e+05 | 5 | 0.3753 | 0.3753 | 0.4230 | 0.3756 ± 0.0022 | 0.6779 | 0.6973 | 0.02787 | 0.02932 | 0.07776 | 4.493 | 4.734 | 0.93854 | 0.9391 ± 0.0004 |
| 0.5 | 1e+05 | 10 | 0.3428 | 0.3429 | 0.4337 | 0.3440 ± 0.0015 | 0.6461 | 0.6829 | 0.03645 | 0.03755 | 0.1006 | 4.419 | 4.688 | 0.93130 | 0.9317 ± 0.0003 |
| 0.5 | 1e+05 | 30 | 0.2894 | 0.2894 | 0.4509 | 0.2895 ± 0.0008 | 0.5886 | 0.6574 | 0.05508 | 0.05476 | 0.15 | 4.342 | 4.657 | 0.91713 | 0.9172 ± 0.0002 |
| 0.5 | 1e+06 | 1 | 0.5476 | 0.5476 | 0.5250 | 0.5425 ± 0.0144 | 0.8157 | 0.8105 | 0.006045 | 0.006586 | 0.01791 | 4.965 | 5.085 | 0.96640 | 0.9697 ± 0.0018 |
| 0.5 | 1e+06 | 5 | 0.4887 | 0.4887 | 0.5209 | 0.4817 ± 0.0065 | 0.7741 | 0.7855 | 0.01218 | 0.01273 | 0.03439 | 4.543 | 4.734 | 0.95858 | 0.9598 ± 0.0010 |
| 0.5 | 1e+06 | 10 | 0.4576 | 0.4576 | 0.5188 | 0.4602 ± 0.0046 | 0.7501 | 0.7714 | 0.01589 | 0.01631 | 0.04444 | 4.478 | 4.688 | 0.95384 | 0.9555 ± 0.0007 |
| 0.5 | 1e+06 | 30 | 0.4050 | 0.4050 | 0.5153 | 0.4048 ± 0.0025 | 0.7056 | 0.7462 | 0.02385 | 0.02378 | 0.06609 | 4.417 | 4.657 | 0.94465 | 0.9448 ± 0.0005 |
| 0.5 | 1e+08 | 1 |  | 0.7271 | 0.7186 |  | 0.9170 | 0.9155 | 0.001196 | 0.001279 | 0.003572 | 5.000 | 5.085 | 0.98424 |  |
| 0.5 | 1e+08 | 5 |  | 0.6836 | 0.6981 |  | 0.8963 | 0.9001 | 0.002389 | 0.002473 | 0.00683 | 4.599 | 4.734 | 0.98070 |  |
| 0.5 | 1e+08 | 10 |  | 0.6598 | 0.6871 |  | 0.8839 | 0.8912 | 0.003102 | 0.003168 | 0.008805 | 4.541 | 4.688 | 0.97858 |  |
| 0.5 | 1e+08 | 30 |  | 0.6177 | 0.6682 |  | 0.8605 | 0.8745 | 0.004622 | 0.00462 | 0.01304 | 4.495 | 4.657 | 0.97450 |  |
| 0.5 | 1e+12 | 1 |  | 0.9212 | 0.9199 |  | 0.9860 | 0.9858 | 4.909e-05 | 5.142e-05 | 0.0001477 | 5.030 | 5.085 | 0.99635 |  |
| 0.5 | 1e+12 | 5 |  | 0.9053 | 0.9080 |  | 0.9820 | 0.9824 | 9.707e-05 | 9.943e-05 | 0.0002807 | 4.648 | 4.734 | 0.99556 |  |
| 0.5 | 1e+12 | 10 |  | 0.8961 | 0.9012 |  | 0.9795 | 0.9803 | 0.0001255 | 0.0001274 | 0.0003607 | 4.596 | 4.688 | 0.99509 |  |
| 0.5 | 1e+12 | 30 |  | 0.8792 | 0.8889 |  | 0.9747 | 0.9764 | 0.0001856 | 0.0001857 | 0.0005312 | 4.558 | 4.657 | 0.99420 |  |
| 0.5 | 1e+20 | 1 |  | 0.9964 | 0.9964 |  | 0.9997 | 0.9997 | 9.01e-08 | 9.271e-08 | 2.726e-07 | 5.053 | 5.085 | 0.99978 |  |
| 0.5 | 1e+20 | 5 |  | 0.9955 | 0.9956 |  | 0.9997 | 0.9997 | 1.766e-07 | 1.793e-07 | 5.15e-07 | 4.685 | 4.734 | 0.99974 |  |
| 0.5 | 1e+20 | 10 |  | 0.9949 | 0.9951 |  | 0.9996 | 0.9996 | 2.274e-07 | 2.296e-07 | 6.599e-07 | 4.635 | 4.688 | 0.99971 |  |
| 0.5 | 1e+20 | 30 |  | 0.9939 | 0.9941 |  | 0.9995 | 0.9995 | 3.345e-07 | 3.348e-07 | 9.671e-07 | 4.602 | 4.657 | 0.99966 |  |
| 0.7459 | 1e+03 | 1 | 0.5507 | 0.5485 | 0.4840 | 0.5507 ± 0.0050 | 0.8604 | 0.8563 | 0.2538 | 0.3377 | 0.5507 | 3.368 | 4.147 | 0.97555 | 0.9757 ± 0.0004 |
| 0.7459 | 1e+03 | 5 | 0.3891 | 0.3892 | 0.4910 | 0.3848 ± 0.0021 | 0.7535 | 0.7857 | 0.3891 | 0.4905 | 0.7546 | 2.887 | 3.822 | 0.95930 | 0.9589 ± 0.0003 |
| 0.7459 | 1e+03 | 10 | 0.3062 | 0.3071 | 0.4945 | 0.3043 ± 0.0013 | 0.6768 | 0.7361 | 0.4524 | 0.5526 | 0.8365 | 2.732 | 3.780 | 0.94659 | 0.9464 ± 0.0002 |
| 0.7459 | 1e+03 | 30 | 0.1834 | 0.1845 | 0.5002 | 0.1821 ± 0.0005 | 0.5188 | 0.6262 | 0.5695 | 0.6563 | 0.9496 | 2.443 | 3.753 | 0.91510 | 0.9150 ± 0.0002 |
| 0.7459 | 1e+04 | 1 | 0.7815 | 0.7811 | 0.7691 | 0.7861 ± 0.0041 | 0.9604 | 0.9601 | 0.1649 | 0.2104 | 0.3764 | 3.569 | 4.147 | 0.99070 | 0.9908 ± 0.0002 |
| 0.7459 | 1e+04 | 5 | 0.6681 | 0.6677 | 0.7076 | 0.6695 ± 0.0021 | 0.9223 | 0.9296 | 0.2522 | 0.3056 | 0.5299 | 3.142 | 3.822 | 0.98468 | 0.9849 ± 0.0001 |
| 0.7459 | 1e+04 | 10 | 0.5972 | 0.5969 | 0.6699 | 0.5981 ± 0.0016 | 0.8911 | 0.9050 | 0.2916 | 0.3442 | 0.5972 | 3.041 | 3.780 | 0.98006 | 0.9802 ± 0.0001 |
| 0.7459 | 1e+04 | 30 | 0.4656 | 0.4655 | 0.5962 | 0.4658 ± 0.0009 | 0.8146 | 0.8427 | 0.3622 | 0.4088 | 0.7104 | 2.895 | 3.753 | 0.96883 | 0.9689 ± 0.0001 |
| 0.7459 | 1e+05 | 1 | 0.9130 | 0.9130 | 0.9108 | 0.9097 ± 0.0029 | 0.9906 | 0.9906 | 0.1093 | 0.1354 | 0.2573 | 3.694 | 4.147 | 0.99640 | 0.9962 ± 0.0001 |
| 0.7459 | 1e+05 | 5 | 0.8554 | 0.8553 | 0.8683 | 0.8569 ± 0.0016 | 0.9801 | 0.9816 | 0.1668 | 0.1967 | 0.3658 | 3.286 | 3.822 | 0.99412 | 0.9941 ± 0.0001 |
| 0.7459 | 1e+05 | 10 | 0.8146 | 0.8145 | 0.8387 | 0.8145 ± 0.0013 | 0.9708 | 0.9736 | 0.1921 | 0.2215 | 0.414 | 3.207 | 3.780 | 0.99237 | 0.9923 ± 0.0001 |
| 0.7459 | 1e+05 | 30 | 0.7279 | 0.7279 | 0.7737 | 0.7283 ± 0.0008 | 0.9455 | 0.9518 | 0.2368 | 0.2631 | 0.4975 | 3.111 | 3.753 | 0.98819 | 0.9882 ± 0.0000 |
| 0.7459 | 1e+06 | 1 | 0.9706 | 0.9706 | 0.9702 | 0.9733 ± 0.0047 | 0.9980 | 0.9981 | 0.07348 | 0.08893 | 0.1764 | 3.778 | 4.147 | 0.99859 | 0.9986 ± 0.0002 |
| 0.7459 | 1e+06 | 5 | 0.9474 | 0.9474 | 0.9511 | 0.9553 ± 0.0026 | 0.9956 | 0.9959 | 0.1118 | 0.1292 | 0.2518 | 3.380 | 3.822 | 0.99771 | 0.9979 ± 0.0001 |
| 0.7459 | 1e+06 | 10 | 0.9295 | 0.9295 | 0.9366 | 0.9313 ± 0.0023 | 0.9934 | 0.9939 | 0.1284 | 0.1455 | 0.2853 | 3.311 | 3.780 | 0.99704 | 0.9970 ± 0.0001 |
| 0.7459 | 1e+06 | 30 | 0.8878 | 0.8878 | 0.9019 | 0.8888 ± 0.0017 | 0.9868 | 0.9880 | 0.1574 | 0.1728 | 0.3437 | 3.238 | 3.753 | 0.99544 | 0.9954 ± 0.0001 |
| 0.7459 | 1e+08 | 1 |  | 0.9977 | 0.9977 |  | 0.9999 | 0.9999 | 0.03403 | 0.03984 | 0.08374 | 3.880 | 4.147 | 0.99978 |  |
| 0.7459 | 1e+08 | 5 |  | 0.9954 | 0.9956 |  | 0.9998 | 0.9999 | 0.0515 | 0.05787 | 0.1197 | 3.494 | 3.822 | 0.99965 |  |
| 0.7459 | 1e+08 | 10 |  | 0.9934 | 0.9939 |  | 0.9998 | 0.9998 | 0.05893 | 0.06518 | 0.1356 | 3.435 | 3.780 | 0.99954 |  |
| 0.7459 | 1e+08 | 30 |  | 0.9882 | 0.9892 |  | 0.9995 | 0.9995 | 0.07173 | 0.07743 | 0.1633 | 3.382 | 3.753 | 0.99930 |  |
| 0.7459 | 1e+12 | 1 |  | 1.0000 | 1.0000 |  | 1.0000 | 1.0000 | 0.007722 | 0.008672 | 0.01945 | 3.974 | 4.147 | 0.99999 |  |
| 0.7459 | 1e+12 | 5 |  | 1.0000 | 1.0000 |  | 1.0000 | 1.0000 | 0.01158 | 0.0126 | 0.02774 | 3.604 | 3.822 | 0.99999 |  |
| 0.7459 | 1e+12 | 10 |  | 1.0000 | 1.0000 |  | 1.0000 | 1.0000 | 0.01319 | 0.01419 | 0.03137 | 3.553 | 3.780 | 0.99999 |  |
| 0.7459 | 1e+12 | 30 |  | 1.0000 | 1.0000 |  | 1.0000 | 1.0000 | 0.01594 | 0.01685 | 0.03764 | 3.513 | 3.753 | 0.99998 |  |
| 0.7459 | 1e+20 | 1 |  | 1.0000 | 1.0000 |  | 1.0000 | 1.0000 | 0.0004386 | 0.0004728 | 0.001124 | 4.043 | 4.147 | 1.00000 |  |
| 0.7459 | 1e+20 | 5 |  | 1.0000 | 1.0000 |  | 1.0000 | 1.0000 | 0.0006506 | 0.0006867 | 0.001595 | 3.690 | 3.822 | 1.00000 |  |
| 0.7459 | 1e+20 | 10 |  | 1.0000 | 1.0000 |  | 1.0000 | 1.0000 | 0.0007381 | 0.0007735 | 0.001799 | 3.644 | 3.780 | 1.00000 |  |
| 0.7459 | 1e+20 | 30 |  | 1.0000 | 1.0000 |  | 1.0000 | 1.0000 | 0.000886 | 0.0009188 | 0.002149 | 3.611 | 3.753 | 1.00000 |  |
| 0.9 | 1e+03 | 1 | 0.8743 | 0.8666 | 0.8667 | 0.8821 ± 0.0032 | 0.9932 | 0.9935 | 0.5363 | 0.9173 | 0.8743 | 2.334 | 3.739 | 0.99509 | 0.9953 ± 0.0001 |
| 0.9 | 1e+03 | 5 | 0.6815 | 0.6747 | 0.7206 | 0.6843 ± 0.0020 | 0.9670 | 0.9668 | 0.6815 | 1.153 | 0.9681 | 1.981 | 3.436 | 0.98900 | 0.9891 ± 0.0001 |
| 0.9 | 1e+03 | 10 | 0.5317 | 0.5291 | 0.5847 | 0.5315 ± 0.0013 | 0.9259 | 0.9153 | 0.7342 | 1.218 | 0.9866 | 1.855 | 3.398 | 0.98297 | 0.9830 ± 0.0001 |
| 0.9 | 1e+03 | 30 | 0.2785 | 0.2797 | 0.1887 | 0.2785 ± 0.0004 | 0.7627 | 0.5678 | 0.8168 | 1.307 | 0.9989 | 1.664 | 3.372 | 0.96413 | 0.9642 ± 0.0001 |
| 0.9 | 1e+04 | 1 | 0.9891 | 0.9890 | 0.9893 | 0.9882 ± 0.0011 | 0.9999 | 0.9999 | 0.4398 | 0.6971 | 0.7725 | 2.556 | 3.739 | 0.99902 | 0.9990 ± 0.0000 |
| 0.9 | 1e+04 | 5 | 0.9595 | 0.9590 | 0.9606 | 0.9608 ± 0.0009 | 0.9993 | 0.9993 | 0.5614 | 0.8759 | 0.8889 | 2.233 | 3.436 | 0.99782 | 0.9978 ± 0.0000 |
| 0.9 | 1e+04 | 10 | 0.9216 | 0.9208 | 0.9182 | 0.9228 ± 0.0009 | 0.9980 | 0.9978 | 0.6036 | 0.9255 | 0.9216 | 2.137 | 3.398 | 0.99664 | 0.9967 ± 0.0000 |
| 0.9 | 1e+04 | 30 | 0.7942 | 0.7933 | 0.7123 | 0.7939 ± 0.0007 | 0.9883 | 0.9825 | 0.6684 | 0.9929 | 0.961 | 1.995 | 3.372 | 0.99300 | 0.9930 ± 0.0000 |
| 0.9 | 1e+05 | 1 | 0.9996 | 0.9996 | 0.9996 | 0.9994 ± 0.0002 | 1.0000 | 1.0000 | 0.3653 | 0.5494 | 0.6754 | 2.720 | 3.739 | 0.99980 | 0.9998 ± 0.0000 |
| 0.9 | 1e+05 | 5 | 0.9981 | 0.9981 | 0.9981 | 0.9983 ± 0.0002 | 1.0000 | 1.0000 | 0.4678 | 0.6903 | 0.794 | 2.411 | 3.436 | 0.99956 | 0.9996 ± 0.0000 |
| 0.9 | 1e+05 | 10 | 0.9954 | 0.9954 | 0.9951 | 0.9956 ± 0.0002 | 1.0000 | 1.0000 | 0.5021 | 0.7294 | 0.8304 | 2.332 | 3.398 | 0.99933 | 0.9993 ± 0.0000 |
| 0.9 | 1e+05 | 30 | 0.9816 | 0.9816 | 0.9752 | 0.9814 ± 0.0002 | 0.9998 | 0.9998 | 0.5537 | 0.7825 | 0.8802 | 2.226 | 3.372 | 0.99861 | 0.9986 ± 0.0000 |
| 0.9 | 1e+06 | 1 | 1.0000 | 1.0000 | 1.0000 | 1.0000 ± 0.0000 | 1.0000 | 1.0000 | 0.3061 | 0.4428 | 0.5878 | 2.847 | 3.739 | 0.99996 | 1.0000 ± 0.0000 |
| 0.9 | 1e+06 | 5 | 1.0000 | 1.0000 | 1.0000 | 1.0000 ± 0.0000 | 1.0000 | 1.0000 | 0.393 | 0.5564 | 0.6999 | 2.541 | 3.436 | 0.99991 | 0.9999 ± 0.0000 |
| 0.9 | 1e+06 | 10 | 0.9999 | 0.9999 | 0.9999 | 0.9999 ± 0.0001 | 1.0000 | 1.0000 | 0.4213 | 0.5879 | 0.7355 | 2.473 | 3.398 | 0.99986 | 0.9999 ± 0.0000 |
| 0.9 | 1e+06 | 30 | 0.9993 | 0.9993 | 0.9992 | 0.9993 ± 0.0001 | 1.0000 | 1.0000 | 0.4631 | 0.6307 | 0.7859 | 2.390 | 3.372 | 0.99972 | 0.9997 ± 0.0000 |
| 0.9 | 1e+08 | 1 |  | 1.0000 | 1.0000 |  | 1.0000 | 1.0000 | 0.2191 | 0.2999 | 0.4432 | 3.030 | 3.739 | 1.00000 |  |
| 0.9 | 1e+08 | 5 |  | 1.0000 | 1.0000 |  | 1.0000 | 1.0000 | 0.2822 | 0.3769 | 0.535 | 2.720 | 3.436 | 1.00000 |  |
| 0.9 | 1e+08 | 10 |  | 1.0000 | 1.0000 |  | 1.0000 | 1.0000 | 0.302 | 0.3982 | 0.5645 | 2.664 | 3.398 | 0.99999 |  |
| 0.9 | 1e+08 | 30 |  | 1.0000 | 1.0000 |  | 1.0000 | 1.0000 | 0.3306 | 0.4272 | 0.6072 | 2.603 | 3.372 | 0.99999 |  |
| 0.9 | 1e+12 | 1 |  | 1.0000 | 1.0000 |  | 1.0000 | 1.0000 | 0.1176 | 0.1506 | 0.2521 | 3.246 | 3.739 | 1.00000 |  |
| 0.9 | 1e+12 | 5 |  | 1.0000 | 1.0000 |  | 1.0000 | 1.0000 | 0.1519 | 0.1892 | 0.3075 | 2.922 | 3.436 | 1.00000 |  |
| 0.9 | 1e+12 | 10 |  | 1.0000 | 1.0000 |  | 1.0000 | 1.0000 | 0.1622 | 0.1999 | 0.3251 | 2.873 | 3.398 | 1.00000 |  |
| 0.9 | 1e+12 | 30 |  | 1.0000 | 1.0000 |  | 1.0000 | 1.0000 | 0.1766 | 0.2145 | 0.3506 | 2.830 | 3.372 | 1.00000 |  |
| 0.9 | 1e+20 | 1 |  | 1.0000 | 1.0000 |  | 1.0000 | 1.0000 | 0.03713 | 0.04434 | 0.08374 | 3.439 | 3.739 | 1.00000 |  |
| 0.9 | 1e+20 | 5 |  | 1.0000 | 1.0000 |  | 1.0000 | 1.0000 | 0.0479 | 0.05571 | 0.1025 | 3.104 | 3.436 | 1.00000 |  |
| 0.9 | 1e+20 | 10 |  | 1.0000 | 1.0000 |  | 1.0000 | 1.0000 | 0.05101 | 0.05887 | 0.1084 | 3.059 | 3.398 | 1.00000 |  |
| 0.9 | 1e+20 | 30 |  | 1.0000 | 1.0000 |  | 1.0000 | 1.0000 | 0.05531 | 0.06315 | 0.1168 | 3.025 | 3.372 | 1.00000 |  |

The deterministic-threshold integral (`fk.contain_det`) matches the exact finite-$N$ share to $2\times10^{-3}$ at $N=10^3$ and $10^{-4}$ at $N\ge10^4$; the simulator agrees with both. The asymptotic miss-rate formula becomes accurate only when $w_N$ is large ($N\gtrsim10^{8}$ here); at $N=10^{12}$ to $10^{20}$ it agrees with the integral to $10^{-3}$. $c_{10x}/\mathrm{prec}_K$ climbs slowly toward $I_{10K}/I_K$, as §4.4 predicts for a $1/b_N^2$ correction.

---

## 7. Best-paper probability (§6.7)

**Exact formula.** Let $m$ be the best paper's quality, with density $N\phi(m)\Phi(m)^{N-1}$, and $s$ its
score, $s\mid m\sim N(\rho m,\tau^2)$. The other $N-1$ papers are iid given $Q<m$, and each out-scores the
best paper with probability
$$\pi(m,s)=P(S>s\mid Q<m)=\frac{\bar\Phi(s)-P_2(m,s;\rho)}{\Phi(m)}.$$
So, exactly,
$$P(\text{best}\in\mathrm{Top}_K(S))=\int\!\!\int N\phi(m)\Phi(m)^{N-1}\,\frac{\phi\big((s-\rho m)/\tau\big)}{\tau}\,P\big(\mathrm{Bin}(N-1,\pi(m,s))\le K-1\big)\,ds\,dm .$$
The handoff's Poisson route replaces the binomial by Poisson($\lambda$), $\lambda=(N-1)\pi(m,s)$. That changes
the answer by a relative $O(K/N)$: $-5\times10^{-4}$ at $N=10^3$, $-5\times10^{-7}$ at $N=10^6$ (Table 7).
For $K=1$ the event equals $\{\arg\max S=\arg\max Q\}$, so $P(\text{best}\in\mathrm{Top}_1)=\mathrm{prec}_1$. The two
quadratures (different integrands) agree to $3\times10^{-9}$ relative over the whole grid.

**Point-process limit.** Write $m=b+x/a$ with $x$ Gumbel (density $e^{-x}e^{-e^{-x}}$) and $s=b+y/a$. The
exponent of $\phi((s-\rho m)/\tau)$ is
$-\frac{(1-\rho)b^2}{2(1+\rho)}-c\frac{b}{a}(y-\rho x)+O(a^{-2})$. The count of out-scorers is Poisson($e^{-y}$) to
leading order. So
$$P(\text{best}\in\mathrm{Top}_K)\approx\frac{\phi(\sqrt\kappa\,b_N)}{\tau a_N}\;E_{\rm Gumbel}\big[e^{(1-c)x}\big]\int e^{-cy}F_K(e^{-y})\,dy
=\varepsilon_N\,\Gamma(c)\,I_K(c),$$
using $E[e^{\theta x}]=\Gamma(1-\theta)$ for a Gumbel variable ($\theta=c\rho=1-c$) and
$\phi(\sqrt\kappa b_N)/(\tau a_N)=\varepsilon_N$. In terms of $N$:
$$\boxed{P(\text{best}\in\mathrm{Top}_K(S))\sim\frac{(1+\rho)\,\Gamma\!\big(\tfrac1{1+\rho}\big)}{\sqrt{1-\rho^2}}\,\frac{\Gamma(K+\frac1{1+\rho})}{\Gamma(K)}\,(4\pi\log N)^{-\frac{\rho}{1+\rho}}\,N^{-\frac{1-\rho}{1+\rho}}.}$$
- Same rate as $\mathrm{prec}_K$. At $K=1$ the constant equals $C_1$ of §4.3 because $\Gamma(c)=\Gamma(1+c)/c$.
- $P(\text{best}\in\mathrm{Top}_K)/\mathrm{prec}_K\to\Gamma(1+c)\,\Gamma(K+1)/\Gamma(K+c)\approx\Gamma(1+c)K^{1-c}$: widening the award set from
  1 to $K$ raises the chance of including the best paper roughly like $K^{\rho/(1+\rho)}$.
- In $K$ at fixed $N$: $P\propto\Gamma(K+c)/\Gamma(K)\approx K^{c}$, so it grows like $K^{1/(1+\rho)}$, until the
  approximation fails when $K$ approaches $N^{1-\rho^2}$ (the probability then tends to 1, §8).

**Checks.** Small $N$: the exact formula against 4-dimensional orthant probabilities ($N=3,K=2$,
differences $\le3\times10^{-8}$) and against 42 Monte Carlo cells ($N=3$ to 50) in §4.1. Large $N$:
`exact/pure` rises to 0.998, 0.989, 0.961 at $N=10^{100}$ for $K=1$ ($\rho=0.5,0.7459,0.9$). The
corrections are larger for larger $K$ (0.993, 0.974, 0.917 at $K=30$, $N=10^{100}$) because the
quadratic terms grow like $(\log K)^2/b_N^2$ here: unlike $\beta_K$ for precision, the $(\log K)^2$ terms do
not cancel. Repository simulator: Table 7 (pooled `simulate` and `simulate_best_paper` runs; 2,700 to
50,000 conferences).

**Table 7** (`run_best.py`, `out/best_table.jsonl`; simulator rows pool `simulate` and `simulate_best_paper`).

| rho | N | K | exact | Poisson route | exact/Poisson - 1 | exact/lead(b) | exact/pure | simulator (pooled reps) | z |
|---|---|---|---|---|---|---|---|---|---|
| 0.5 | 1e+03 | 1 | 0.044297 | 0.044321 | -5.5e-04 | 0.8673 | 0.9263 | 0.04200 ± 0.00090 (50000) | -2.56 |
| 0.5 | 1e+03 | 5 | 0.13794 | 0.13801 | -4.7e-04 | 0.8523 | 0.9104 | 0.13558 ± 0.00153 (50000) | -1.54 |
| 0.5 | 1e+03 | 10 | 0.21115 | 0.21124 | -4.2e-04 | 0.8129 | 0.8683 | 0.20822 ± 0.00182 (50000) | -1.61 |
| 0.5 | 1e+03 | 30 | 0.38395 | 0.38407 | -3.2e-04 | 0.7055 | 0.7535 | 0.38210 ± 0.00217 (50000) | -0.85 |
| 0.5 | 1e+04 | 1 | 0.018845 | 0.018846 | -5.5e-05 | 0.8854 | 0.9345 | 0.01874 ± 0.00061 (50000) | -0.17 |
| 0.5 | 1e+04 | 5 | 0.059208 | 0.059211 | -4.9e-05 | 0.8779 | 0.9266 | 0.05928 ± 0.00106 (50000) | 0.07 |
| 0.5 | 1e+04 | 10 | 0.091911 | 0.091915 | -4.6e-05 | 0.8492 | 0.8963 | 0.09190 ± 0.00129 (50000) | -0.01 |
| 0.5 | 1e+04 | 30 | 0.1745 | 0.17451 | -4.0e-05 | 0.7695 | 0.8121 | 0.17452 ± 0.00170 (50000) | 0.01 |
| 0.5 | 1e+05 | 1 | 0.0081925 | 0.0081926 | -5.5e-06 | 0.9005 | 0.9428 | 0.00806 ± 0.00067 (18000) | -0.21 |
| 0.5 | 1e+05 | 5 | 0.025838 | 0.025838 | -5.1e-06 | 0.8962 | 0.9384 | 0.02622 ± 0.00119 (18000) | 0.32 |
| 0.5 | 1e+05 | 10 | 0.040414 | 0.040414 | -4.8e-06 | 0.8735 | 0.9146 | 0.04239 ± 0.00150 (18000) | 1.31 |
| 0.5 | 1e+05 | 30 | 0.0785 | 0.078501 | -4.3e-06 | 0.8097 | 0.8478 | 0.07767 ± 0.00199 (18000) | -0.42 |
| 0.5 | 1e+06 | 1 | 0.0036065 | 0.0036065 | -5.6e-07 | 0.9127 | 0.9502 | 0.00370 ± 0.00117 (2700) | 0.08 |
| 0.5 | 1e+06 | 5 | 0.011395 | 0.011395 | -5.2e-07 | 0.9101 | 0.9475 | 0.01370 ± 0.00224 (2700) | 1.03 |
| 0.5 | 1e+06 | 10 | 0.017907 | 0.017907 | -4.9e-07 | 0.8912 | 0.9278 | 0.01963 ± 0.00267 (2700) | 0.65 |
| 0.5 | 1e+06 | 30 | 0.035276 | 0.035276 | -4.6e-07 | 0.8378 | 0.8723 | 0.03481 ± 0.00353 (2700) | -0.13 |
| 0.5 | 1e+12 | 1 | 2.936e-05 | 2.936e-05 | -5.6e-13 | 0.9516 | 0.9746 |  |  |
| 0.5 | 1e+12 | 5 | 9.2966e-05 | 9.2966e-05 | -5.5e-13 | 0.9509 | 0.9739 |  |  |
| 0.5 | 1e+12 | 10 | 0.00014768 | 0.00014768 | -5.4e-13 | 0.9412 | 0.9640 |  |  |
| 0.5 | 1e+12 | 30 | 0.00030046 | 0.00030046 | -5.2e-13 | 0.9139 | 0.9360 |  |  |
| 0.5 | 1e+30 | 1 | 2.1996e-11 | 2.1996e-11 | 0.0e+00 | 0.9795 | 0.9910 |  |  |
| 0.5 | 1e+30 | 5 | 6.9687e-11 | 6.9687e-11 | -1.5e-14 | 0.9793 | 0.9908 |  |  |
| 0.5 | 1e+30 | 10 | 1.1138e-10 | 1.1138e-10 | -1.8e-14 | 0.9754 | 0.9868 |  |  |
| 0.5 | 1e+30 | 30 | 2.3072e-10 | 2.3072e-10 | -3.6e-13 | 0.9642 | 0.9755 |  |  |
| 0.5 | 1e+100 | 1 | 6.8831e-35 | 6.8831e-35 | 0.0e+00 | 0.9937 | 0.9980 |  |  |
| 0.5 | 1e+100 | 5 | 2.181e-34 | 2.181e-34 | 5.1e-15 | 0.9937 | 0.9980 |  |  |
| 0.5 | 1e+100 | 10 | 3.4958e-34 | 3.4958e-34 | -3.0e-14 | 0.9925 | 0.9968 |  |  |
| 0.5 | 1e+100 | 30 | 7.3002e-34 | 7.3002e-34 | 5.6e-13 | 0.9891 | 0.9934 |  |  |
| 0.7459 | 1e+03 | 1 | 0.16354 | 0.16361 | -3.9e-04 | 0.7616 | 0.8288 | 0.16454 ± 0.00166 (50000) | 0.60 |
| 0.7459 | 1e+03 | 5 | 0.41067 | 0.41078 | -2.6e-04 | 0.6943 | 0.7555 | 0.40828 ± 0.00220 (50000) | -1.09 |
| 0.7459 | 1e+03 | 10 | 0.55074 | 0.55084 | -1.9e-04 | 0.6185 | 0.6730 | 0.54934 ± 0.00223 (50000) | -0.63 |
| 0.7459 | 1e+03 | 30 | 0.77472 | 0.77478 | -8.5e-05 | 0.4600 | 0.5005 | 0.77386 ± 0.00187 (50000) | -0.46 |
| 0.7459 | 1e+04 | 1 | 0.10547 | 0.10548 | -4.1e-05 | 0.7886 | 0.8450 | 0.10568 ± 0.00137 (50000) | 0.15 |
| 0.7459 | 1e+04 | 5 | 0.27273 | 0.27274 | -3.1e-05 | 0.7403 | 0.7932 | 0.27176 ± 0.00199 (50000) | -0.49 |
| 0.7459 | 1e+04 | 10 | 0.37644 | 0.37645 | -2.5e-05 | 0.6787 | 0.7273 | 0.37574 ± 0.00217 (50000) | -0.32 |
| 0.7459 | 1e+04 | 30 | 0.56956 | 0.56957 | -1.6e-05 | 0.5429 | 0.5817 | 0.57218 ± 0.00221 (50000) | 1.18 |
| 0.7459 | 1e+05 | 1 | 0.069652 | 0.069653 | -4.2e-06 | 0.8091 | 0.8582 | 0.07106 ± 0.00191 (18000) | 0.73 |
| 0.7459 | 1e+05 | 5 | 0.18321 | 0.18321 | -3.3e-06 | 0.7727 | 0.8196 | 0.18461 ± 0.00289 (18000) | 0.48 |
| 0.7459 | 1e+05 | 10 | 0.25731 | 0.25731 | -2.9e-06 | 0.7208 | 0.7645 | 0.25706 ± 0.00326 (18000) | -0.08 |
| 0.7459 | 1e+05 | 30 | 0.4068 | 0.4068 | -2.1e-06 | 0.6024 | 0.6390 | 0.40461 ± 0.00366 (18000) | -0.60 |
| 0.7459 | 1e+06 | 1 | 0.046696 | 0.046696 | -4.3e-07 | 0.8258 | 0.8696 | 0.04704 ± 0.00407 (2700) | 0.08 |
| 0.7459 | 1e+06 | 5 | 0.12416 | 0.12416 | -3.5e-07 | 0.7972 | 0.8394 | 0.12222 ± 0.00630 (2700) | -0.31 |
| 0.7459 | 1e+06 | 10 | 0.17641 | 0.17641 | -3.1e-07 | 0.7524 | 0.7922 | 0.18074 ± 0.00741 (2700) | 0.58 |
| 0.7459 | 1e+06 | 30 | 0.2872 | 0.2872 | -2.5e-07 | 0.6475 | 0.6818 | 0.28630 ± 0.00870 (2700) | -0.10 |
| 0.7459 | 1e+12 | 1 | 0.0048937 | 0.0048937 | -4.4e-13 | 0.8875 | 0.9152 |  |  |
| 0.7459 | 1e+12 | 5 | 0.013303 | 0.013303 | -4.1e-13 | 0.8759 | 0.9032 |  |  |
| 0.7459 | 1e+12 | 10 | 0.01945 | 0.01945 | -3.9e-13 | 0.8506 | 0.8772 |  |  |
| 0.7459 | 1e+12 | 30 | 0.034077 | 0.034077 | -3.5e-13 | 0.7879 | 0.8125 |  |  |
| 0.7459 | 1e+30 | 1 | 8.3479e-06 | 8.3479e-06 | 0.0e+00 | 0.9478 | 0.9621 |  |  |
| 0.7459 | 1e+30 | 5 | 2.2879e-05 | 2.2879e-05 | -1.2e-14 | 0.9430 | 0.9573 |  |  |
| 0.7459 | 1e+30 | 10 | 3.4025e-05 | 3.4025e-05 | -1.7e-14 | 0.9316 | 0.9456 |  |  |
| 0.7459 | 1e+30 | 30 | 6.2348e-05 | 6.2348e-05 | -3.1e-13 | 0.9025 | 0.9161 |  |  |
| 0.7459 | 1e+100 | 1 | 3.3278e-16 | 3.3278e-16 | 0.0e+00 | 0.9832 | 0.9887 |  |  |
| 0.7459 | 1e+100 | 5 | 9.152e-16 | 9.152e-16 | 7.8e-15 | 0.9816 | 0.9871 |  |  |
| 0.7459 | 1e+100 | 10 | 1.3726e-15 | 1.3726e-15 | -2.5e-14 | 0.9779 | 0.9834 |  |  |
| 0.7459 | 1e+100 | 30 | 2.5711e-15 | 2.5711e-15 | 4.8e-13 | 0.9684 | 0.9738 |  |  |
| 0.9 | 1e+03 | 1 | 0.3746 | 0.3747 | -2.6e-04 | 0.6233 | 0.6845 | 0.37324 ± 0.00216 (50000) | -0.63 |
| 0.9 | 1e+03 | 5 | 0.74838 | 0.74845 | -9.1e-05 | 0.4856 | 0.5333 | 0.74742 ± 0.00194 (50000) | -0.50 |
| 0.9 | 1e+03 | 10 | 0.87434 | 0.87437 | -3.0e-05 | 0.3891 | 0.4273 | 0.87384 ± 0.00148 (50000) | -0.34 |
| 0.9 | 1e+03 | 30 | 0.97806 | 0.97805 | 1.1e-05 | 0.2421 | 0.2659 | 0.97724 ± 0.00067 (50000) | -1.23 |
| 0.9 | 1e+04 | 1 | 0.30229 | 0.3023 | -2.9e-05 | 0.6619 | 0.7146 | 0.30208 ± 0.00205 (50000) | -0.10 |
| 0.9 | 1e+04 | 5 | 0.63635 | 0.63636 | -1.4e-05 | 0.5433 | 0.5866 | 0.63770 ± 0.00215 (50000) | 0.63 |
| 0.9 | 1e+04 | 10 | 0.77253 | 0.77254 | -7.5e-06 | 0.4523 | 0.4884 | 0.77398 ± 0.00187 (50000) | 0.77 |
| 0.9 | 1e+04 | 30 | 0.92421 | 0.92421 | -1.0e-06 | 0.3010 | 0.3250 | 0.92582 ± 0.00117 (50000) | 1.38 |
| 0.9 | 1e+05 | 1 | 0.24833 | 0.24833 | -3.1e-06 | 0.6900 | 0.7366 | 0.25272 ± 0.00324 (18000) | 1.35 |
| 0.9 | 1e+05 | 5 | 0.54164 | 0.54164 | -1.7e-06 | 0.5868 | 0.6265 | 0.54128 ± 0.00371 (18000) | -0.10 |
| 0.9 | 1e+05 | 10 | 0.67544 | 0.67544 | -1.1e-06 | 0.5019 | 0.5357 | 0.67322 ± 0.00350 (18000) | -0.64 |
| 0.9 | 1e+05 | 30 | 0.85153 | 0.85153 | -3.9e-07 | 0.3519 | 0.3757 | 0.85367 ± 0.00263 (18000) | 0.81 |
| 0.9 | 1e+06 | 1 | 0.20649 | 0.20649 | -3.2e-07 | 0.7118 | 0.7537 | 0.19630 ± 0.00764 (2700) | -1.33 |
| 0.9 | 1e+06 | 5 | 0.46211 | 0.46211 | -2.0e-07 | 0.6212 | 0.6578 | 0.46296 ± 0.00960 (2700) | 0.09 |
| 0.9 | 1e+06 | 10 | 0.58784 | 0.58784 | -1.4e-07 | 0.5419 | 0.5738 | 0.58444 ± 0.00948 (2700) | -0.36 |
| 0.9 | 1e+06 | 30 | 0.77203 | 0.77203 | -6.7e-08 | 0.3959 | 0.4192 | 0.76630 ± 0.00814 (2700) | -0.70 |
| 0.9 | 1e+12 | 1 | 0.077667 | 0.077667 | -3.6e-13 | 0.7873 | 0.8146 |  |  |
| 0.9 | 1e+12 | 5 | 0.18683 | 0.18683 | -2.9e-13 | 0.7385 | 0.7641 |  |  |
| 0.9 | 1e+12 | 10 | 0.25208 | 0.25208 | -2.5e-13 | 0.6833 | 0.7070 |  |  |
| 0.9 | 1e+12 | 30 | 0.37639 | 0.37639 | -1.9e-13 | 0.5676 | 0.5872 |  |  |
| 0.9 | 1e+30 | 1 | 0.0062119 | 0.0062119 | 0.0e+00 | 0.8761 | 0.8908 |  |  |
| 0.9 | 1e+30 | 5 | 0.015594 | 0.015594 | -1.4e-14 | 0.8577 | 0.8720 |  |  |
| 0.9 | 1e+30 | 10 | 0.021969 | 0.021969 | -1.5e-14 | 0.8286 | 0.8425 |  |  |
| 0.9 | 1e+30 | 30 | 0.036279 | 0.036279 | -2.6e-13 | 0.7612 | 0.7739 |  |  |
| 0.9 | 1e+100 | 1 | 7.8348e-07 | 7.8348e-07 | 0.0e+00 | 0.9545 | 0.9605 |  |  |
| 0.9 | 1e+100 | 5 | 1.9958e-06 | 1.9958e-06 | 1.1e-14 | 0.9482 | 0.9541 |  |  |
| 0.9 | 1e+100 | 10 | 2.8771e-06 | 2.8771e-06 | -1.4e-14 | 0.9374 | 0.9432 |  |  |
| 0.9 | 1e+100 | 30 | 5.0282e-06 | 5.0282e-06 | 4.3e-13 | 0.9113 | 0.9169 |  |  |

Largest relative difference between $P(\text{best}\in\mathrm{Top}_1)$ and $\mathrm{prec}_1$ over the grid of Table 7: $3.1\times10^{-9}$.

One cell (ρ = 0.5, $N=10^3$, $K=1$) showed $z=-2.56$ on the pooled runs. A follow-up
(`check_rho05_N1000.py`) gave $0.044155\pm0.000325$ with my own Monte Carlo ($4\times10^5$ conferences) and
$0.04419\pm0.00033$ with four fresh repository runs ($4\times10^5$ conferences) against the exact 0.044297
($z=-0.44$ and $-0.33$). The first gap was chance.

---

## 8. Rank of the winner (§6.8)

Let $W$ be the true rank (1 = best) of the top-scored paper.

**Exact identity.** $(Q_i,S_i)_{i\le N}$ has the same joint law as $(S_i,Q_i)_{i\le N}$ (equal variances, symmetric
correlation). The event $\{W\le r\}$ = "the top-$S$ paper is in $\mathrm{Top}_r(Q)$" maps under the swap to
"the top-$Q$ paper is in $\mathrm{Top}_r(S)$". Hence, for every $r$ and $N$,
$$P(W\le r)=P(\text{best paper}\in\mathrm{Top}_r(S)).$$
So §7 gives the whole distribution of $W$, and its median is the smallest $r$ with $P(\text{best}\in\mathrm{Top}_r)\ge1/2$.
The simulator reports both sides of the identity (`winner_rank_q*` and `best_in_K*`), so it checks it.

**Asymptotics.** For large $r$ the fixed-$r$ limit of §7 no longer applies. Given $S_{(1)}=s$ and
$Q_{[1]}=q$, $W-1\sim\mathrm{Bin}(N-1,P(Q>q\mid S<s))\approx\mathrm{Poisson}(N\bar\Phi(q))$, because a paper above $q\approx\rho b_N$ in
quality is very unlikely to also beat $b_N$ in score. When $N\bar\Phi(q)$ is large the Poisson noise is
negligible, so $W\approx N\bar\Phi(Q_{[1]})$, a decreasing function of $Q_{[1]}=\rho S_{(1)}+\tau Z$. Hence
$$W_u\approx N\,\bar\Phi\big(m_{1-u}\big),\qquad m_v=v\text{-quantile of }\rho S_{(1)}+\tau Z\quad(\text{semi-asymptotic quantile}),$$
and with $S_{(1)}=b_N+G/a_N$, $G$ Gumbel, the median of $\tau Z+\rho G/a$ is $\rho\gamma_E/a+O(a^{-2})$, so
$$\boxed{\mathrm{median}(W)\approx N\bar\Phi\big(\rho b_N+\rho\gamma_E/a_N\big)\approx\frac{e^{-\gamma_E\rho^2}}{\rho}\Big(\frac{N}{\sqrt{4\pi\log N}}\Big)^{1-\rho^2}.}$$
The winner's true percentile tends to 1 ($W/N\asymp N^{-\rho^2}\to0$) while its rank tends to infinity like
$N^{1-\rho^2}$. The spread: $\log W\approx\log N\bar\Phi(\rho b_N)-\rho b_N\tau Z$, so $\log W$ is nearly normal with SD
$\rho\tau b_N\approx\rho\sqrt{1-\rho^2}\sqrt{2\log N}$; the interquartile ratio $W_{75}/W_{25}\approx e^{1.349\rho\tau b_N}$ also grows.

**Table 8a** (`run_winner.py`, `run_winner_fix.py`, `out/winner_table.jsonl`, `out/winner_fix.json`). Exact quantiles
$W_u$ = the smallest $r$ with $P(W\le r)\ge u$, from the §7 quadrature through the identity above. Semi-asymptotic
quantiles from $N\bar\Phi(m_{1-u})$. Closed medians from the boxed formula ($b_N$ form, then $\log N$ form). The simulator's
`winner_rank_q50`, Gaussian model, $R=1$. † At $N=10^{12}$ the exact column uses the Poisson route of §7, because scipy's
binomial cdf (`bdtr`) fails for $n\approx10^{12}$ (it returned $W_{90}=2^{33}-1$ at $\rho=0.5$). The Poisson route differs from
the binomial by $O(r/N)$; at $N=10^8$ the two agree to $6\times10^{-9}$ relative for $r=1$ to $10^4$ at all three $\rho$.

| $\rho$ | $N$ | $W_{10}$ | $W_{25}$ | median | $W_{75}$ | $W_{90}$ | semi-asympt. $W_{25}$ / median / $W_{75}$ | closed median ($b_N$) | closed median ($\log N$) | simulator medians (conferences) |
|---|---|---|---|---|---|---|---|---|---|---|
| 0.5 | 1e+03 | 4 | 14 | 53 | 153 | 313 | 13.3 / 52.6 / 153 | 51.5 | 57.7 | 54 (40000), 56 (10000) |
| 0.5 | 1e+04 | 12 | 60 | 271 | 914 | 2120 | 58.9 / 271 / 914 | 267 | 291 | 267 (40000), 269.5 (10000) |
| 0.5 | 1e+05 | 46 | 270 | 1421 | 5473 | 14252 | 269 / 1420 / 5473 | 1401 | 1507 | 1379 (8000), 1464 (8000), 1536 (2000) |
| 0.5 | 1e+06 | 191 | 1259 | 7528 | 32797 | 95004 | 1259 / 7527 / 32797 | 7445 | 7916 | 6571 (1500), 7051 (1000), 11083.5 (200) |
| 0.5 | 1e+08 | 3563 | 28869 | 216309 | 1175939 | 4132907 | 28869 / 216309 / 1175938 | 214555 | 224733 |  |
| 0.5 | 1e+12† | 1492803 | 17122535 | 188214240 | 1493513779 | 7326397681 | 17122534 / 188214240 / 1493513778 | 187210397 | 193033218 |  |
| 0.7459 | 1e+03 | 1 | 2 | 8 | 27 | 66 | 1.9 / 7.9 / 26.6 | 7.5 | 7.7 | 8 (40000), 8 (10000) |
| 0.7459 | 1e+04 | 1 | 5 | 21 | 83 | 242 | 4.1 / 20.5 / 82.6 | 19.7 | 20.2 | 21 (40000), 20 (10000) |
| 0.7459 | 1e+05 | 2 | 10 | 55 | 256 | 866 | 9.3 / 54.2 / 256 | 52.4 | 53.3 | 53 (8000), 55 (8000), 53 (2000) |
| 0.7459 | 1e+06 | 4 | 22 | 145 | 788 | 3044 | 21.4 / 144 / 788 | 140 | 142 | 158 (1500), 150 (1000), 156.5 (200) |
| 0.7459 | 1e+08 | 15 | 120 | 1043 | 7399 | 36209 | 119 / 1042 / 7399 | 1020 | 1029 |  |
| 0.7459 | 1e+12† | 331 | 4147 | 56530 | 626444 | 4581510 | 4147 / 56530 / 626443 | 55704 | 55963 |  |
| 0.9 | 1e+03 | 1 | 1 | 2 | 6 | 13 | 0.5 / 1.8 / 5.4 | 1.7 | 1.7 | 2 (40000), 2 (10000) |
| 0.9 | 1e+04 | 1 | 1 | 3 | 9 | 24 | 0.7 / 2.7 / 9.2 | 2.5 | 2.6 | 3 (40000), 3 (10000) |
| 0.9 | 1e+05 | 1 | 2 | 5 | 16 | 46 | 1.0 / 4.1 / 15.5 | 3.8 | 3.9 | 5 (8000), 4 (8000), 4 (2000) |
| 0.9 | 1e+06 | 1 | 2 | 7 | 26 | 87 | 1.3 / 6.2 / 26.2 | 5.9 | 5.9 | 7 (1500), 6 (1000), 7 (200) |
| 0.9 | 1e+08 | 1 | 3 | 15 | 74 | 295 | 2.5 / 14.4 / 74.2 | 13.7 | 13.7 |  |
| 0.9 | 1e+12† | 2 | 10 | 79 | 573 | 3126 | 9.6 / 78.6 / 573 | 75.9 | 76.1 |  |

**Table 8b.** Each simulated median $m$ against the exact cdf. A sample median $m$ is consistent with the exact law when
0.5 lies within 2 SE of the bracket $[P(W\le m-1),P(W\le m)]$; SE $=0.5/\sqrt{n}$ for $n$ conferences. For a half-integer
$m$ the bracket is the single value $P(W\le\lfloor m\rfloor)$.

| $\rho$ | $N$ | conferences | simulator median $m$ | exact $P(W\le m-1)$ | exact $P(W\le m)$ | SE of the empirical CDF | consistent (0.5 within 2 SE of the bracket) |
|---|---|---|---|---|---|---|---|
| 0.5 | 1e+03 | 10000 | 56 | 0.5101 | 0.5141 | 0.0050 | NO |
| 0.5 | 1e+03 | 40000 | 54 | 0.5018 | 0.5060 | 0.0025 | yes |
| 0.5 | 2e+03 | 10000 | 86 | 0.4977 | 0.5002 | 0.0050 | yes |
| 0.5 | 5e+03 | 10000 | 166 | 0.4999 | 0.5012 | 0.0050 | yes |
| 0.5 | 1e+04 | 10000 | 269.5 | (half-integer) | 0.4986 | 0.0050 | yes |
| 0.5 | 1e+04 | 40000 | 267 | 0.4964 | 0.4971 | 0.0025 | yes |
| 0.5 | 2e+04 | 10000 | 430 | 0.4928 | 0.4933 | 0.0050 | yes |
| 0.5 | 5e+04 | 4000 | 834 | 0.4939 | 0.4941 | 0.0079 | yes |
| 0.5 | 1e+05 | 2000 | 1536 | 0.5140 | 0.5141 | 0.0112 | yes |
| 0.5 | 1e+05 | 8000 | 1379 | 0.4946 | 0.4948 | 0.0056 | yes |
| 0.5 | 1e+05 | 8000 | 1464 | 0.5053 | 0.5055 | 0.0056 | yes |
| 0.5 | 2e+05 | 1000 | 2413 | 0.5050 | 0.5051 | 0.0158 | yes |
| 0.5 | 5e+05 | 400 | 3657.5 | (half-integer) | 0.4636 | 0.0250 | yes |
| 0.5 | 1e+06 | 200 | 11083.5 | (half-integer) | 0.5652 | 0.0354 | yes |
| 0.5 | 1e+06 | 1000 | 7051 | 0.4892 | 0.4892 | 0.0158 | yes |
| 0.5 | 1e+06 | 1500 | 6571 | 0.4777 | 0.4777 | 0.0129 | yes |
| 0.7459 | 1e+03 | 10000 | 8 | 0.4771 | 0.5044 | 0.0050 | yes |
| 0.7459 | 1e+03 | 40000 | 8 | 0.4771 | 0.5044 | 0.0025 | yes |
| 0.7459 | 2e+03 | 10000 | 11 | 0.4913 | 0.5101 | 0.0050 | yes |
| 0.7459 | 5e+03 | 10000 | 15.5 | (half-integer) | 0.4960 | 0.0050 | yes |
| 0.7459 | 1e+04 | 10000 | 20 | 0.4864 | 0.4956 | 0.0050 | yes |
| 0.7459 | 1e+04 | 40000 | 21 | 0.4956 | 0.5044 | 0.0025 | yes |
| 0.7459 | 2e+04 | 10000 | 27 | 0.4907 | 0.4972 | 0.0050 | yes |
| 0.7459 | 5e+04 | 4000 | 41 | 0.4984 | 0.5025 | 0.0079 | yes |
| 0.7459 | 1e+05 | 2000 | 53 | 0.4934 | 0.4965 | 0.0112 | yes |
| 0.7459 | 1e+05 | 8000 | 53 | 0.4934 | 0.4965 | 0.0056 | yes |
| 0.7459 | 1e+05 | 8000 | 55 | 0.4995 | 0.5025 | 0.0056 | yes |
| 0.7459 | 2e+05 | 1000 | 81.5 | (half-integer) | 0.5172 | 0.0158 | yes |
| 0.7459 | 5e+05 | 400 | 118 | 0.5132 | 0.5145 | 0.0250 | yes |
| 0.7459 | 1e+06 | 200 | 156.5 | (half-integer) | 0.5116 | 0.0354 | yes |
| 0.7459 | 1e+06 | 1000 | 150 | 0.5048 | 0.5058 | 0.0158 | yes |
| 0.7459 | 1e+06 | 1500 | 158 | 0.5126 | 0.5136 | 0.0129 | yes |
| 0.9 | 1e+03 | 10000 | 2 | 0.3746 | 0.5363 | 0.0050 | yes |
| 0.9 | 1e+03 | 40000 | 2 | 0.3746 | 0.5363 | 0.0025 | yes |
| 0.9 | 2e+03 | 10000 | 2 | 0.3503 | 0.5044 | 0.0050 | yes |
| 0.9 | 5e+03 | 10000 | 3 | 0.4662 | 0.5563 | 0.0050 | yes |
| 0.9 | 1e+04 | 10000 | 3 | 0.4398 | 0.5267 | 0.0050 | yes |
| 0.9 | 1e+04 | 40000 | 3 | 0.4398 | 0.5267 | 0.0025 | yes |
| 0.9 | 2e+04 | 10000 | 4 | 0.4991 | 0.5595 | 0.0050 | yes |
| 0.9 | 5e+04 | 4000 | 4 | 0.4653 | 0.5233 | 0.0079 | yes |
| 0.9 | 1e+05 | 2000 | 4 | 0.4416 | 0.4977 | 0.0112 | yes |
| 0.9 | 1e+05 | 8000 | 5 | 0.4977 | 0.5416 | 0.0056 | yes |
| 0.9 | 1e+05 | 8000 | 4 | 0.4416 | 0.4977 | 0.0056 | yes |
| 0.9 | 2e+05 | 1000 | 4 | 0.4193 | 0.4735 | 0.0158 | yes |
| 0.9 | 5e+05 | 400 | 5.5 | (half-integer) | 0.4846 | 0.0250 | yes |
| 0.9 | 1e+06 | 200 | 7 | 0.4950 | 0.5231 | 0.0354 | yes |
| 0.9 | 1e+06 | 1000 | 6 | 0.4621 | 0.4950 | 0.0158 | yes |
| 0.9 | 1e+06 | 1500 | 7 | 0.4950 | 0.5231 | 0.0129 | yes |

**Reading Table 8.**
- 47 of 48 simulated medians are consistent with the exact law. The one exception ($\rho=0.5$, $N=10^3$, $10^4$
  conferences) sits at 2.02 SE; the run with $4\times10^4$ conferences at the same point is consistent.
- The semi-asymptotic quantiles are within 2.2 % of the exact median for $\rho\le0.7459$ at every $N\ge10^3$, and
  within $10^{-5}$ relative at $N=10^{12}$. At $\rho=0.9$ the winner rank is small (median 2 to 7), the Poisson count noise
  that the semi-asymptotic form drops still matters, and it is low by 8 to 18 % over $N=10^3$ to $10^6$; the gap
  falls to 0.6 % at $10^{12}$.
- The closed median ($b_N$ form) is low by 1 to 3 % ($\rho=0.5$), 3 to 6 % ($\rho=0.7459$) and 16 to 23 % ($\rho=0.9$) over
  $N=10^3$ to $10^6$; at $10^{12}$ by 0.5 %, 1.5 % and 3.9 %. The $\log N$ form is off by $+5$ to $+9$ %, $-2$ to $-4$ % and $-15$ to $-23$ %
  over the same range.
- Growth: at $\rho=0.7459$ the median is 8, 21, 55, 145 at $N=10^3,10^4,10^5,10^6$, a local exponent of 0.42 against
  $1-\rho^2=0.444$ (the log factor $(4\pi\log N)^{-(1-\rho^2)/2}$ accounts for the difference).
- Spread: $W_{75}/W_{25}$ grows with $N$ (13.5, 16.6, 25.6, 35.8 at $\rho=0.7459$ for $N=10^3$ to $10^6$; 151 at $10^{12}$). The
  leading estimate $e^{1.349\rho\tau b_N}$ gives 24 at $10^6$ and 112 at $10^{12}$: it understates the spread, because it drops
  the Gumbel spread of $S_{(1)}$ and the curvature of $\log\bar\Phi$. The semi-asymptotic quantiles keep both and give 36.8 at $10^6$.

---

## 9. Two-committee top-$K$ overlap (§6.9)

Committee scores $(S^{(1)}_i,S^{(2)}_i)$ are iid over papers and standard bivariate normal with correlation
$\rho^2$. The overlap $\lvert\mathrm{Top}_K(S^{(1)})\cap\mathrm{Top}_K(S^{(2)})\rvert/K$ is the precision problem of §4 with the pair
$(S^{(1)},S^{(2)})$ in place of $(S,Q)$. So every result of §4 holds with $\rho\to\rho^2$:
$$\mathrm{ovl}_K(N,\rho)=\mathrm{prec}_K(N,\rho^2)\sim C_K(\rho^2)\,(\log N)^{-\frac{\rho^2}{1+\rho^2}}\,N^{-\frac{1-\rho^2}{1+\rho^2}},$$
and the fixed-percentile version is $P_2(z_p,z_p;\rho^2)/p$ (§3 is its $p=\alpha$ case). At the central
$\rho^2=0.5563$ the overlap exponent is $0.285$, about twice the precision exponent $0.146$; the overlap
falls faster because each committee carries its own noise. Since the overlap is observable without
knowing $q$, it is the field-testable proxy for precision; the map between them at fixed $N,K$ is
monotone through $\rho$.

**Table 9.** Two-committee top-K overlap: exact = prec_K(N, rho^2), against the simulator.

| rho | rho^2 | N | K | exact | simulator | z |
|---|---|---|---|---|---|---|
| 0.5 | 0.2500 | 1e+03 | 1 | 0.0089085 | 0.00950 ± 0.00097 | 0.61 |
| 0.5 | 0.2500 | 1e+03 | 5 | 0.027366 | 0.02692 ± 0.00071 | -0.63 |
| 0.5 | 0.2500 | 1e+03 | 10 | 0.043114 | 0.04211 ± 0.00062 | -1.62 |
| 0.5 | 0.2500 | 1e+03 | 30 | 0.087923 | 0.08712 ± 0.00049 | -1.63 |
| 0.5 | 0.2500 | 1e+04 | 1 | 0.0021194 | 0.00220 ± 0.00047 | 0.17 |
| 0.5 | 0.2500 | 1e+04 | 5 | 0.0064483 | 0.00664 ± 0.00036 | 0.53 |
| 0.5 | 0.2500 | 1e+04 | 10 | 0.010099 | 0.01018 ± 0.00032 | 0.25 |
| 0.5 | 0.2500 | 1e+04 | 30 | 0.020333 | 0.02065 ± 0.00026 | 1.21 |
| 0.5 | 0.2500 | 1e+05 | 1 | 0.00051091 | 0.00060 ± 0.00024 | 0.36 |
| 0.5 | 0.2500 | 1e+05 | 5 | 0.0015442 | 0.00156 ± 0.00018 | 0.09 |
| 0.5 | 0.2500 | 1e+05 | 10 | 0.0024098 | 0.00246 ± 0.00016 | 0.32 |
| 0.5 | 0.2500 | 1e+05 | 30 | 0.0048182 | 0.00496 ± 0.00013 | 1.10 |
| 0.5 | 0.2500 | 1e+06 | 1 | 0.00012408 | 0.00000 ± 0.00000 | nan |
| 0.5 | 0.2500 | 1e+06 | 5 | 0.00037326 | 0.00000 ± 0.00000 | nan |
| 0.5 | 0.2500 | 1e+06 | 10 | 0.00058111 | 0.00017 ± 0.00012 | -3.52 |
| 0.5 | 0.2500 | 1e+06 | 30 | 0.0011568 | 0.00069 ± 0.00014 | -3.36 |
| 0.7459 | 0.5564 | 1e+03 | 1 | 0.060642 | 0.05900 ± 0.00236 | -0.70 |
| 0.7459 | 0.5564 | 1e+03 | 5 | 0.12148 | 0.12112 ± 0.00139 | -0.26 |
| 0.7459 | 0.5564 | 1e+03 | 10 | 0.15678 | 0.15632 ± 0.00108 | -0.43 |
| 0.7459 | 0.5564 | 1e+03 | 30 | 0.23211 | 0.23120 ± 0.00071 | -1.29 |
| 0.7459 | 0.5564 | 1e+04 | 1 | 0.028678 | 0.03110 ± 0.00174 | 1.40 |
| 0.7459 | 0.5564 | 1e+04 | 5 | 0.056997 | 0.05672 ± 0.00101 | -0.28 |
| 0.7459 | 0.5564 | 1e+04 | 10 | 0.073006 | 0.07330 ± 0.00080 | 0.37 |
| 0.7459 | 0.5564 | 1e+04 | 30 | 0.10624 | 0.10622 ± 0.00054 | -0.03 |
| 0.7459 | 0.5564 | 1e+05 | 1 | 0.013876 | 0.01400 ± 0.00117 | 0.11 |
| 0.7459 | 0.5564 | 1e+05 | 5 | 0.027383 | 0.02648 ± 0.00071 | -1.27 |
| 0.7459 | 0.5564 | 1e+05 | 10 | 0.034908 | 0.03492 ± 0.00057 | 0.02 |
| 0.7459 | 0.5564 | 1e+05 | 30 | 0.050314 | 0.05041 ± 0.00039 | 0.26 |
| 0.7459 | 0.5564 | 1e+06 | 1 | 0.0068047 | 0.00333 ± 0.00167 | -2.08 |
| 0.7459 | 0.5564 | 1e+06 | 5 | 0.013347 | 0.00933 ± 0.00124 | -3.23 |
| 0.7459 | 0.5564 | 1e+06 | 10 | 0.016957 | 0.01467 ± 0.00109 | -2.11 |
| 0.7459 | 0.5564 | 1e+06 | 30 | 0.024288 | 0.02317 ± 0.00079 | -1.42 |
| 0.9 | 0.8100 | 1e+03 | 1 | 0.22784 | 0.22140 ± 0.00415 | -1.55 |
| 0.9 | 0.8100 | 1e+03 | 5 | 0.33655 | 0.33966 ± 0.00191 | 1.63 |
| 0.9 | 0.8100 | 1e+03 | 10 | 0.38243 | 0.38186 ± 0.00134 | -0.43 |
| 0.9 | 0.8100 | 1e+03 | 30 | 0.46248 | 0.46182 ± 0.00077 | -0.85 |
| 0.9 | 0.8100 | 1e+04 | 1 | 0.16142 | 0.16180 ± 0.00368 | 0.10 |
| 0.9 | 0.8100 | 1e+04 | 5 | 0.23948 | 0.23842 ± 0.00178 | -0.59 |
| 0.9 | 0.8100 | 1e+04 | 10 | 0.27063 | 0.27093 ± 0.00129 | 0.23 |
| 0.9 | 0.8100 | 1e+04 | 30 | 0.32269 | 0.32220 ± 0.00076 | -0.65 |
| 0.9 | 0.8100 | 1e+05 | 1 | 0.11694 | 0.12060 ± 0.00326 | 1.12 |
| 0.9 | 0.8100 | 1e+05 | 5 | 0.17392 | 0.17668 ± 0.00163 | 1.69 |
| 0.9 | 0.8100 | 1e+05 | 10 | 0.19591 | 0.19676 ± 0.00118 | 0.73 |
| 0.9 | 0.8100 | 1e+05 | 30 | 0.23177 | 0.23147 ± 0.00071 | -0.42 |
| 0.9 | 0.8100 | 1e+06 | 1 | 0.085956 | 0.08417 ± 0.00802 | -0.22 |
| 0.9 | 0.8100 | 1e+06 | 5 | 0.12799 | 0.13017 ± 0.00430 | 0.51 |
| 0.9 | 0.8100 | 1e+06 | 10 | 0.14383 | 0.14392 ± 0.00308 | 0.03 |
| 0.9 | 0.8100 | 1e+06 | 30 | 0.16929 | 0.16883 ± 0.00187 | -0.25 |

At $N=10^6$ the simulated overlap is low for $\rho=0.5$ and $0.7459$ ($z$ down to $-3.5$; nan where no conference had a hit).
§13.3 examines this with a code replay, own Monte Carlo and fresh runs. It finds no defect in the simulator.

---

## 10. Tails (§6.10)

### 10.1 The general principle

Write $S=Q+E$ on the original scale ($E$ = the per-paper noise, mean of $R$ errors). Fixed-$K$
selection at large $N$ looks only at the extreme upper corner of the (quality, score) pair. Let
$u=K/N$ and
$$\chi=\lim_{u\to0}P\big(F_S(S)>1-u\mid F_Q(Q)>1-u\big)$$
be the upper tail-dependence coefficient. The expected count of papers above both $(1-u)$-quantiles
is $N\cdot u\cdot(\chi+o(1))$, and §4.5 shows that fixed-$K$ precision is this count over $K$ up to a
finite-$K$ factor. So:
- $\chi=0$ (asymptotic independence): precision $\to0$. Its rate is set by how fast the joint tail
  vanishes. For a bivariate normal $P(\text{both}>1-u)\asymp u^{1/\eta}\times\mathrm{slowly\ varying}$ with $\eta=(1+\rho)/2$, so
  precision $\asymp u^{1/\eta-1}=(K/N)^{(1-\rho)/(1+\rho)}$, which is §4.
- $0<\chi<1$ (asymptotic dependence, partial): precision tends to a positive plateau below 1.
- $\chi=1$ with noise negligible against the spacing of the top qualities: precision $\to1$.

Which case occurs depends on two comparisons.
1. **Noise tail against quality tail.** If $P(E>x)/P(Q>x)\to\infty$ (noise tail heavier), the top scores
   are noise extremes. Their qualities are near-typical draws, so $\chi=0$ and precision falls like
   random selection, $\mathrm{prec}_K\asymp K/N$ up to slowly varying factors.
2. **Noise scale against the extreme-value scale of quality.** If the noise tail is lighter, the
   top scores are the top qualities displaced by the noise. Let $a_Q(N)$ be the spacing of the top
   qualities (the auxiliary function of the quality's extreme-value limit). Then precision $\to1$ if
   $a_Q(N)/\sigma_E\to\infty$, a plateau if $a_Q(N)$ is constant, and $\to0$ if $a_Q(N)\to0$ (the
   Gaussian case, where both tails are of the same type and the competition is §4).

| quality | top spacing $a_Q(N)$ | Gaussian noise | $t_3$ noise |
|---|---|---|---|
| Gaussian | $\sigma_q/\sqrt{2\log N}\to0$ | $\chi=0$; $\to0$ like $N^{-(1-\rho)/(1+\rho)}(\log N)^{-\rho/(1+\rho)}$ (§4) | noise tail heavier: $\chi=0$; $\to0$ like $K/N$ |
| exponential | $\sigma_q$ (constant) | $\chi=2\bar\Phi(\sigma/2)$, $\sigma=\sigma_E/\sigma_q$; **plateau** (10.2) | noise tail heavier: $\chi=0$; $\to0$ like $K/N$ |
| lognormal | $\propto x_N/\log x_N\to\infty$ slowly | $\chi=1$; $\to1$, very slowly | noise tail heavier: $\to0$ |
| Student-$t_3$ | $\propto N^{1/3}$ | $\chi=1$; **$\to1$**, $1-\mathrm{prec}_K\propto(K/N)^{1/3}$ (10.3) | same tail index: $\chi=w$; **plateau $w$** (10.4) |
| bounded Beta($a,a$) | $\propto N^{-1/a}\to0$ | noise tail heavier: $\chi=0$; $\to0$ like $K(\log N)^{a/2}/N$ (10.5) | $\chi=0$; $\to0$ like $K/N$ |

### 10.2 Exponential quality, Gaussian noise: the plateau

Work in units of $\sigma_q$ with $\sigma=\sigma_E/\sigma_q$. After a shift by $\log N$, the top qualities form a
Poisson process with intensity $e^{-x}dx$ on the whole line, exactly (no slowly varying correction,
apart from binomial effects of order $K/N$). Each point carries an independent noise $e\sim N(0,\sigma^2)$
and score $x+e$. For a typical point at $(x,x+e)$ the other points fall in independent Poisson cells:
$$\mu_Q=\lambda,\qquad \mu_S=\lambda e^{\sigma^2/2-e},\qquad \mu_{11}=\lambda\,g(e),\quad g(d)=\bar\Phi(d/\sigma)+e^{\sigma^2/2-d}\,\bar\Phi\big((\sigma^2-d)/\sigma\big),$$
with $\lambda=e^{-x}$ (the last is $\int_x^\infty e^{-t}\bar\Phi((x+d-t)/\sigma)dt$ in closed form). By the Mecke formula
$$\lim_{N\to\infty}\mathrm{prec}_K=\frac1K\int_0^\infty d\lambda\;E_e\Big[\sum_{m=0}^{K-1}\mathrm{Pois}(m;\mu_{11})\,F_{K-m}(\mu_Q-\mu_{11})\,F_{K-m}(\mu_S-\mu_{11})\Big].$$
This limit is free of $N$ and strictly between 0 and 1. Checks of the formula (`tails.exp_gauss_limit`):
$\sigma=10^{-3}$ gives $0.999436$, equal to the small-noise law $1-\sigma/\sqrt\pi$ of 10.3; doubling the
grid changes the value by $10^{-11}$; as $K$ grows the limit rises to $\chi=2\bar\Phi(\sigma/2)$
($\sigma=1$: 0.5387, 0.5925, 0.6042, 0.6126, 0.6157 for $K=1,5,10,30,100$, against $\chi=0.6171$).
The tail-dependence coefficient follows from $P(S>s)=e^{\sigma^2/2}e^{-s}$:
$\chi=\int_0^\infty e^{-t}\bar\Phi((\sigma^2/2-t)/\sigma)dt=2\bar\Phi(\sigma/2)$.

### 10.3 Regularly varying quality, Gaussian noise: precision rises to one

$t_3$ quality: $P(Q>x)\sim c_Qx^{-3}$ with $c_Q=2\sigma_q^3/(3\pi)$ (the $t_3$ density is $6\sqrt3/(\pi(3+t^2)^2)$). The top
qualities sit at scale $(Nc_Q)^{1/3}$ and their spacings grow at the same rate, while the noise stays
$O(\sigma_E)$. Errors happen only when the $K$-th and $(K+1)$-th papers swap, i.e. when the noise
difference $D=E_{K+1}-E_K$ exceeds the gap $G_K=Q_{(K)}-Q_{(K+1)}$. Non-adjacent swaps need two gaps and cost
$O(\sigma_E^2/a_Q^2)$. To first order in $\sigma_E/a_Q$:
$$1-\mathrm{prec}_K\approx\frac1K\,f_{G_K}(0)\,E[D^+],\qquad E[D^+]=\sigma_E/\sqrt\pi\ \ (\text{Gaussian }E),$$
$$f_{G_K}(0)=N(N-1)\binom{N-2}{K-1}\int f_Q(x)^2\,\bar F_Q(x)^{K-1}F_Q(x)^{N-K-1}dx\ \xrightarrow{\ \text{Pareto tail}\ }\ 3\,(Nc_Q)^{-1/3}\,\frac{\Gamma(K+4/3)}{\Gamma(K)} .$$
(For the Poisson process with intensity $\lambda(x)$, $f_{G_K}(0)=\int\lambda^2e^{-\Lambda}\Lambda^{K-1}/(K-1)!\,dx$; substitute
$v=\Lambda(x)=Nc_Qx^{-3}$.) So $1-\mathrm{prec}_K\approx\frac{3\sigma_E}{\sqrt\pi}\frac{\Gamma(K+4/3)}{K\,\Gamma(K)}(Nc_Q)^{-1/3}\propto(K/N)^{1/3}$. The same
small-noise formula gives $1-\sigma/\sqrt\pi$ for the exponential (where $f_{G_K}(0)=K$ for every $K$), which
checks 10.2 at small $\sigma$.

### 10.4 $t_3$ quality and $t_3$ noise: the plateau $w$

Both tails are regularly varying with index 3. The mean of $R$ iid errors $\sigma_\varepsilon T_3/\sqrt3$ has
$P(E>x)\sim R\,P(\sigma_\varepsilon T_3/\sqrt3>Rx)=c_Ex^{-3}$, $c_E=2\sigma_\varepsilon^3/(3\pi R^2)$ (one big jump). The score
tail is the sum, $(c_Q+c_E)x^{-3}$. In the limit the top scores are the union of two independent
Poisson processes with intensities proportional to $c_Q$ and $c_E$ (quality extremes with $O(1)$ noise,
and noise extremes with typical quality). The union's points carry iid type marks, quality type
with probability $w=c_Q/(c_Q+c_E)$. Every quality-type point in the top $K$ of the union is in the top $K$
of quality (the quality points keep their order, because their noise is negligible against
their spacing). So, for every $K$,
$$\lim_{N\to\infty}\mathrm{prec}_K=\chi=w=\frac{\sigma_q^3}{\sigma_q^3+\sigma_\varepsilon^3/R^2}=\Big[1+\frac{(1/\rho^2-1)^{3/2}}{\sqrt R}\Big]^{-1}.$$
The last form shows that the plateau depends on $R$ at fixed $\rho$: more reviewers at the same
reliability thin the noise tail.

### 10.5 Bounded quality

Beta($a,a$) on $[q_{\min},q_{\max}]$: $P(Q>q_{\max}-t)\approx C_Bt^a$. With Gaussian noise the top scores are noise
extremes ($s-q_{\max}\approx\sigma_E\sqrt{2\log N}$). Given such an $s$, $q_{\max}-Q$ is approximately
Gamma($a$, rate $(s-q_{\max})/\sigma_E^2$) (density $\propto t^{a-1}e^{-t(s-q_{\max})/\sigma_E^2}$). The true top-$K$ band is
$t\lesssim(K/(NC_B))^{1/a}$. So $P(\text{a selected paper is truly top-}K)\approx\frac{\big((s-q_{\max})/\sigma_E^2\big)^a}{\Gamma(a+1)}\frac{K}{NC_B}$
and $\mathrm{prec}_K\asymp K(2\log N)^{a/2}/(N\sigma_E^aC_B)\to0$. For $\sigma_q=1.2$, $a=6.53$: the factor $(\log N)^{3.27}$ is
large, and the condition $\lambda t_K\ll1$ for this law fails for $N\le10^6$, so the observed decline
in the range is much slower than $1/N$ (Table 10a). With $t_3$ noise the conditional law of $Q$ given an
extreme score tends to the unconditional law, so $\mathrm{prec}_K\to K/N$-like decay.

### 10.6 Fixed-percentile precision for non-Gaussian shapes

For any continuous shapes, the argument of §2 applies unchanged: the empirical $(1-p)$-quantiles of $Q$
and $S$ converge to the population quantiles $q_p,s_p$, and
$$\lim_{N\to\infty}\mathrm{prec}_{pN}=\frac{P(Q>q_p,S>s_p)}{p}=\frac1p\int_{q_p}^\infty f_Q(q)\,\bar F_E(s_p-q)\,dq,\qquad \bar F_S(s_p)=p.$$
So fixed-percentile precision does **not** depend on $N$ for any shape (finite-$N$ corrections are
$O(1/(pN))$). Its value depends on the shape at fixed $\rho$. For $t_3$ noise I compute $\bar F_E$ for the
mean of $R$ errors by Gil–Pelaez inversion of $\varphi_E(t)=[(1+\sigma_\varepsilon|t|/R)e^{-\sigma_\varepsilon|t|/R}]^R$ (checks: SD
1.07156 against 1.07156; the tail joins the one-big-jump asymptote, 0.5 % apart at $x=30$, 0.05 % at
$x=100$).

**Table 10a.** Fixed-number precision from the repository simulator (R = 3, sigma_q = 1.2, sigma_eps = 1.856, so rho^2 = 0.5563 for every shape; one committee), with the large-N limit from 10.2 to 10.5. Entries: mean ± SE.

| quality | noise | K | N=1e3 | 1e4 | 1e5 | 1e6 | limit N -> inf | chi |
|---|---|---|---|---|---|---|---|---|
| gaussian | gaussian | 1 | 0.1544 ± 0.0036 | 0.1036 ± 0.0030 | 0.0680 ± 0.0056 | 0.0550 ± 0.0162 | 0 | 0 |
| gaussian | gaussian | 10 | 0.3059 ± 0.0013 | 0.1959 ± 0.0012 | 0.1303 ± 0.0022 | 0.0900 ± 0.0059 | 0 | 0 |
| gaussian | gaussian | 100 | 0.5081 ± 0.0004 | 0.3126 ± 0.0004 | 0.1999 ± 0.0008 | 0.1305 ± 0.0024 | 0 | 0 |
| exp | gaussian | 1 | 0.5802 ± 0.0049 | 0.5707 ± 0.0050 | 0.5650 ± 0.0111 | 0.5950 ± 0.0348 | 0.5787 | 0.6552 |
| exp | gaussian | 10 | 0.6413 ± 0.0013 | 0.6410 ± 0.0013 | 0.6447 ± 0.0028 | 0.6355 ± 0.0090 | 0.6420 | 0.6552 |
| exp | gaussian | 100 | 0.6557 ± 0.0004 | 0.6536 ± 0.0004 | 0.6539 ± 0.0009 | 0.6525 ± 0.0028 | 0.6538 | 0.6552 |
| lognormal | gaussian | 1 | 0.3804 ± 0.0049 | 0.3657 ± 0.0048 | 0.3810 ± 0.0109 | 0.3900 ± 0.0346 | 1 (very slowly) | 1 |
| lognormal | gaussian | 10 | 0.4807 ± 0.0014 | 0.4471 ± 0.0014 | 0.4356 ± 0.0030 | 0.4315 ± 0.0099 | 1 (very slowly) | 1 |
| lognormal | gaussian | 100 | 0.5786 ± 0.0004 | 0.4885 ± 0.0004 | 0.4551 ± 0.0010 | 0.4484 ± 0.0031 | 1 (very slowly) | 1 |
| t3 | gaussian | 1 | 0.7365 ± 0.0044 | 0.8705 ± 0.0034 | 0.9420 ± 0.0052 | 0.9800 ± 0.0099 | 1.0000 | 1 |
| t3 | gaussian | 10 | 0.6026 ± 0.0014 | 0.8040 ± 0.0011 | 0.9029 ± 0.0017 | 0.9480 ± 0.0041 | 1.0000 | 1 |
| t3 | gaussian | 100 | 0.4982 ± 0.0004 | 0.6177 ± 0.0004 | 0.8177 ± 0.0007 | 0.9091 ± 0.0016 | 1.0000 | 1 |
| beta | gaussian | 1 | 0.0847 ± 0.0028 | 0.0292 ± 0.0017 | 0.0105 ± 0.0023 | 0.0050 ± 0.0050 | 0 | 0 |
| beta | gaussian | 10 | 0.2431 ± 0.0012 | 0.1016 ± 0.0009 | 0.0358 ± 0.0013 | 0.0155 ± 0.0027 | 0 | 0 |
| beta | gaussian | 100 | 0.4967 ± 0.0004 | 0.2466 ± 0.0004 | 0.1040 ± 0.0006 | 0.0359 ± 0.0012 | 0 | 0 |
| gaussian | t3 | 1 | 0.0378 ± 0.0019 | 0.0007 ± 0.0003 | 0.0000 ± 0.0000 | 0.0000 ± 0.0000 | 0 | 0 |
| gaussian | t3 | 10 | 0.2479 ± 0.0013 | 0.0282 ± 0.0005 | 0.0003 ± 0.0002 | 0.0000 ± 0.0000 | 0 | 0 |
| gaussian | t3 | 100 | 0.5478 ± 0.0004 | 0.2535 ± 0.0004 | 0.0264 ± 0.0005 | 0.0005 ± 0.0002 | 0 | 0 |
| exp | t3 | 1 | 0.4275 ± 0.0049 | 0.1814 ± 0.0039 | 0.0030 ± 0.0017 | 0.0000 ± 0.0000 | 0 | 0 |
| exp | t3 | 10 | 0.6129 ± 0.0013 | 0.4914 ± 0.0014 | 0.1459 ± 0.0038 | 0.0015 ± 0.0009 | 0 | 0 |
| exp | t3 | 100 | 0.6833 ± 0.0004 | 0.6278 ± 0.0004 | 0.5019 ± 0.0014 | 0.1433 ± 0.0028 | 0 | 0 |
| t3 | t3 | 1 | 0.5630 ± 0.0050 | 0.6488 ± 0.0048 | 0.6660 ± 0.0149 | 0.7500 ± 0.0307 | 0.7086 | 0.7086 |
| t3 | t3 | 10 | 0.5352 ± 0.0014 | 0.6359 ± 0.0014 | 0.6860 ± 0.0045 | 0.7130 ± 0.0097 | 0.7086 | 0.7086 |
| t3 | t3 | 100 | 0.5315 ± 0.0004 | 0.5479 ± 0.0005 | 0.6480 ± 0.0014 | 0.6942 ± 0.0029 | 0.7086 | 0.7086 |
| beta | t3 | 1 | 0.0190 ± 0.0014 | 0.0002 ± 0.0001 | 0.0000 ± 0.0000 | 0.0000 ± 0.0000 | 0 | 0 |
| beta | t3 | 10 | 0.1845 ± 0.0012 | 0.0120 ± 0.0003 | 0.0003 ± 0.0002 | 0.0000 ± 0.0000 | 0 | 0 |
| beta | t3 | 100 | 0.5365 ± 0.0004 | 0.1872 ± 0.0004 | 0.0108 ± 0.0003 | 0.0003 ± 0.0001 | 0 | 0 |

**Table 10b.** $t_3$ quality, Gaussian noise: $1-\mathrm{prec}_K$, simulator against the first-order law of 10.3 (exact gap density; Pareto-tail value in brackets).

| K | N | simulator | first-order law |
|---|---|---|---|
| 1 | 1e+03 | 0.2635 ± 0.0044 | 0.2960 (0.3017) |
| 1 | 1e+04 | 0.1295 ± 0.0034 | 0.1395 (0.1401) |
| 1 | 1e+05 | 0.0580 ± 0.0052 | 0.0650 (0.0650) |
| 1 | 1e+06 | 0.0200 ± 0.0099 | 0.0302 (0.0302) |
| 10 | 1e+03 | 0.3974 ± 0.0014 | 0.5266 (0.5579) |
| 10 | 1e+04 | 0.1960 ± 0.0011 | 0.2558 (0.2590) |
| 10 | 1e+05 | 0.0971 ± 0.0017 | 0.1199 (0.1202) |
| 10 | 1e+06 | 0.0520 ± 0.0041 | 0.0558 (0.0558) |
| 100 | 1e+03 | 0.5018 ± 0.0004 | 0.8940 (1.1789) |
| 100 | 1e+04 | 0.3823 ± 0.0004 | 0.5185 (0.5472) |
| 100 | 1e+05 | 0.1823 ± 0.0007 | 0.2511 (0.2540) |
| 100 | 1e+06 | 0.0909 ± 0.0016 | 0.1176 (0.1179) |

**Table 10c.** Fixed-percentile precision: N-free population limit (10.6) against the simulator at four N.

| quality | noise | selection | limit | N=1e3 | 1e4 | 1e5 | 1e6 |
|---|---|---|---|---|---|---|---|
| gaussian | gaussian | p1pct | 0.3126 | 0.3059 | 0.3126 | 0.3124 | 0.3124 |
| gaussian | gaussian | p5pct | 0.4360 | 0.4335 | 0.4359 | 0.4359 | 0.4359 |
| gaussian | gaussian | acc0.25 | 0.6342 | 0.6341 | 0.6341 | 0.6343 | 0.6343 |
| exp | gaussian | p1pct | 0.6552 | 0.6413 | 0.6536 | 0.6549 | 0.6547 |
| exp | gaussian | p5pct | 0.6553 | 0.6526 | 0.6548 | 0.6552 | 0.6553 |
| exp | gaussian | acc0.25 | 0.6712 | 0.6710 | 0.6711 | 0.6712 | 0.6711 |
| lognormal | gaussian | p1pct | 0.4896 | 0.4807 | 0.4885 | 0.4898 | 0.4901 |
| lognormal | gaussian | p5pct | 0.5418 | 0.5393 | 0.5418 | 0.5418 | 0.5419 |
| lognormal | gaussian | acc0.25 | 0.6581 | 0.6575 | 0.6581 | 0.6581 | 0.6582 |
| t3 | gaussian | p1pct | 0.6197 | 0.6026 | 0.6177 | 0.6192 | 0.6200 |
| t3 | gaussian | p5pct | 0.5008 | 0.4992 | 0.5005 | 0.5009 | 0.5007 |
| t3 | gaussian | acc0.25 | 0.5695 | 0.5696 | 0.5696 | 0.5696 | 0.5694 |
| beta | gaussian | p1pct | 0.2463 | 0.2431 | 0.2466 | 0.2466 | 0.2466 |
| beta | gaussian | p5pct | 0.4081 | 0.4058 | 0.4082 | 0.4080 | 0.4082 |
| beta | gaussian | acc0.25 | 0.6385 | 0.6381 | 0.6385 | 0.6385 | 0.6385 |
| gaussian | t3 | p1pct | 0.2538 | 0.2479 | 0.2535 | 0.2542 | 0.2543 |
| gaussian | t3 | p5pct | 0.4575 | 0.4559 | 0.4573 | 0.4576 | 0.4574 |
| gaussian | t3 | acc0.25 | 0.6798 | 0.6794 | 0.6797 | 0.6798 | 0.6799 |
| exp | t3 | p1pct | 0.6288 | 0.6129 | 0.6278 | 0.6292 | 0.6288 |
| exp | t3 | p5pct | 0.6690 | 0.6660 | 0.6688 | 0.6689 | 0.6689 |
| exp | t3 | acc0.25 | 0.7137 | 0.7131 | 0.7136 | 0.7136 | 0.7137 |
| t3 | t3 | p1pct | 0.5495 | 0.5352 | 0.5479 | 0.5494 | 0.5494 |
| t3 | t3 | p5pct | 0.5145 | 0.5114 | 0.5146 | 0.5147 | 0.5145 |
| t3 | t3 | acc0.25 | 0.6142 | 0.6137 | 0.6140 | 0.6141 | 0.6141 |
| beta | t3 | p1pct | 0.1872 | 0.1845 | 0.1872 | 0.1870 | 0.1870 |
| beta | t3 | p5pct | 0.4286 | 0.4283 | 0.4284 | 0.4286 | 0.4285 |
| beta | t3 | acc0.25 | 0.6844 | 0.6837 | 0.6843 | 0.6845 | 0.6844 |

Largest |simulator(N=1e6) - limit| over the 27 cells: 0.0005.

**Reading Table 10.**
- **Decay to zero.** Gaussian/Gaussian falls steadily (§4). Bounded quality with Gaussian noise falls faster
  (0.085 to 0.005 for $K=1$), but far slower than $1/N$ in this range, as 10.5 predicts. Every
  combination with $t_3$ noise and a lighter quality tail (Gaussian, exponential, Beta) collapses to
  near zero once the score extremes are noise extremes; the collapse sets in where the $t_3$ tail
  overtakes the quality tail: by $N=10^4$ for Gaussian and Beta quality, and only by $N=10^5$ to $10^6$
  for exponential quality, which holds out longer (at $K=100$ it is still 0.14 at $N=10^6$). At
  $N=10^6$, $K=100$, Gaussian/$t_3$ and Beta/$t_3$ sit at 5 and 3 times the random-selection value
  $K/N=10^{-4}$, in line with $K/N$ times a slowly varying factor.
- **Plateau.** Exponential/Gaussian sits on the Poisson-limit plateau of 10.2 at every $N$ (it converges at
  rate $K/N$): for example $K=10$: 0.6413, 0.6410, 0.6447, 0.6355 against 0.6420. $t_3$/$t_3$ climbs toward
  $w=0.7086$ (0.694 to 0.75 at $N=10^6$); its approach is slow because the noise of the quality-extreme
  papers and the second-order tail terms decay only like a power of $N^{-1/3}$.
- **Rise to one.** $t_3$/Gaussian rises from 0.74 to 0.98 ($K=1$) and from 0.50 to 0.91 ($K=100$). The
  first-order law (Table 10b) is an upper bound on the miss rate in this range and becomes sharp as
  $N$ grows (ratio simulator/law 0.89, 0.93, 0.89 at $K=1$; 0.56, 0.74, 0.73, 0.77 at $K=100$).
- **Lognormal** has $\chi=1$ but a top spacing that grows only like $Q_{(1)}s/b_N$ ($s=0.237$): spacing/noise is
  0.70 at $N=10^6$, 0.87 at $10^{12}$, 1.5 at $10^{30}$. In the handoff range it behaves like a plateau that
  drifts down for $K\ge10$; the limit 1 is out of reach.
- **Fixed percentile is $N$-free for every shape** (Table 10c): the largest gap between the simulator at
  $N=10^6$ and the population limit over 27 cells is 0.0005; the only visible $N$-dependence is at $N=10^3$
  with $p=1\%$ ($K=10$), the finite-$K$ deficit of Table 2.
- The value at fixed $\rho$ depends strongly on the shape: at $p=1\%$ it ranges from 0.19 (Beta/$t_3$) to 0.66
  (exponential/Gaussian), against 0.31 for Gaussian/Gaussian. Heavier quality tails help at the very
  top; heavier noise tails hurt.

---

## 11. Acceptance rate (§6.11)

At fixed $\rho$ (Gaussian model, $N$-free):
$$\mathrm{swap}(\alpha)=1-\frac{P_2(z_\alpha,z_\alpha;\rho)}{\alpha}=\frac{P(Q>z_\alpha,S<z_\alpha)}{\alpha},\qquad D(\alpha)=\frac{P(S^{(1)}>z_\alpha,S^{(2)}<z_\alpha)}{\alpha}\ \ (\text{correlation }\rho^2).$$

**Why both fall as $\alpha$ rises.** The numerator is the mass that crosses the boundary: papers on the
right side in quality but the wrong side in score. For small noise ($\rho\to1$), write $S=\rho Q+\tau Z$; the
crossing mass is $\phi(z_\alpha)\,\tau\,E[Z^+]=\phi(z_\alpha)\tau/\sqrt{2\pi}$. So
$$\mathrm{swap}(\alpha)\approx h(z_\alpha)\,\frac{\tau}{\sqrt{2\pi}},\qquad h(z)=\frac{\phi(z)}{\bar\Phi(z)}\ \text{(hazard)},\qquad D(\alpha)\approx h(z_\alpha)\frac{\sqrt{1-\rho^4}}{\sqrt{2\pi}}.$$
The swap fraction is the boundary density per accepted paper times the noise width. The hazard
$h(z_\alpha)$ rises as $\alpha$ falls ($h(z)\approx z$ for large $z$), because a thinner accepted set has a larger
share of its members near the boundary. Check of the small-noise law: at $\rho=0.99$ the ratio
exact/approx is 1.001 ($\alpha=0.05$) and 1.003 ($\alpha=0.25$); at $\rho=0.9999$ it is $1.00001$ and $1.00003$. At the
central $\rho=0.7459$ the approximation is still within 10 % (table below).

**Monotonicity.** On a 2,000-point grid of $\alpha\in(0.001,0.999)$, `swap_fraction` is strictly decreasing for
$\rho\in\{0.1,0.3,0.5,0.7459,0.9,0.99\}$ (`out/items123_11.json`).

**Counts and symmetry.** The wrong accepts per submission, $\alpha\cdot\mathrm{swap}=P(Q>z_\alpha,S<z_\alpha)$, and the
inconsistent share $2(\alpha-P_2(z_\alpha,z_\alpha;\rho^2))$ are both symmetric under $\alpha\leftrightarrow1-\alpha$ (by $(Q,S)\to(-Q,-S)$). Both
peak at $\alpha=1/2$, with values $\tfrac14-\arcsin(\rho)/(2\pi)$ and $\tfrac12-\arcsin(\rho^2)/\pi$. So a lower acceptance rate
lowers the number of wrong accepts but raises their share among accepts.

| $\alpha$ | $z_\alpha$ | hazard | swap | wrong accepts / submission | swap, small-noise approx. | $D$ | inconsistent share |
|---|---|---|---|---|---|---|---|
| 0.01 | 2.326 | 2.665 | 0.687 | 0.0069 | 0.708 | 0.840 | 0.0168 |
| 0.05 | 1.645 | 2.063 | 0.564 | 0.0282 | 0.548 | 0.720 | 0.0720 |
| 0.10 | 1.282 | 1.755 | 0.491 | 0.0491 | 0.466 | 0.640 | 0.1280 |
| 0.20 | 0.842 | 1.400 | 0.400 | 0.0801 | 0.372 | 0.531 | 0.2124 |
| 0.25 | 0.674 | 1.271 | 0.366 | 0.0914 | 0.338 | 0.488 | 0.2438 |
| 0.30 | 0.524 | 1.159 | 0.335 | 0.1005 | 0.308 | 0.448 | 0.2688 |
| 0.40 | 0.253 | 0.966 | 0.280 | 0.1122 | 0.257 | 0.377 | 0.3015 |
| 0.50 | 0 | 0.798 | 0.232 | 0.1160 | 0.212 | 0.312 | 0.3122 |
| 0.60 | -0.253 | 0.644 | 0.187 | 0.1122 | 0.171 | 0.251 | 0.3015 |
| 0.80 | -0.842 | 0.350 | 0.100 | 0.0801 | 0.093 | 0.133 | 0.2124 |

($\rho=0.7459$, $\rho^2=0.5563$.) The simulator's `prec_acc*` and `dis_acc*` match these $N$-free values up to the
$O(1/K)$ finite-$N$ deficit of §2, which large runs at $N\le2\times10^3$ resolve (§13, Table 13c).

---

## 12. Discretisation (§6.12)

**Why no closed form.** Each review is snapped, $r_{ij}=\mathrm{snap}(q_i+u_i+\varepsilon_{ij})$, before averaging.
1. The snapped review is a step function of a Gaussian: $P(r_{ij}=m_k\mid q)=\Phi\big((c_k-q)/\sigma_\varepsilon\big)-\Phi\big((c_{k-1}-q)/\sigma_\varepsilon\big)$ with
   cut points $c_k$ halfway between scale points. The mean of $R$ snapped reviews lives on a lattice, and its
   law given $q$ is an $R$-fold convolution of these categorical laws.
2. So $(Q,S)$ is no longer bivariate normal, and $S$ is not a linear function of $Q$ plus independent
   noise. $E[S\mid q]$ is a smoothed staircase, and $\mathrm{Var}(S\mid q)$ depends on $q$. $P_2$ and every result of §2 to §9
   lose their basis.
3. The metrics depend on $\mu_q,\sigma_q,\sigma_\varepsilon,R$ and the placement of the scale points separately, not
   through $\rho$ alone (§1).
4. Ties have positive probability. With random tie-breaking, $\mathrm{Top}_K(S)$ is partly a uniform draw
   from a tie class whose size is a binomial count, so the metrics are mixtures over the tie
   configuration.

**What can still be computed (no simulation).** For fixed-percentile rules at large $N$, the tie class
at the threshold has a deterministic share. Let $V$ be the lattice score with marginal pmf $\pi(v)=E_q[P(V=v\mid q)]$.
At acceptance rate $\alpha$ let $v^\ast$ be the class with $P(V>v^\ast)<\alpha\le P(V\ge v^\ast)$ and $f^\ast=(\alpha-P(V>v^\ast))/\pi(v^\ast)$
the share of that class accepted. Then a paper of quality $q$ is accepted with probability
$a(q)=P(V>v^\ast\mid q)+f^\ast P(V=v^\ast\mid q)$, and
$$\mathrm{prec}=\frac{E[a(Q)\,1\{Q>q_\alpha\}]}{\alpha},\qquad P(\mathrm{rej}_2\mid\mathrm{acc}_1)=1-\frac{E[a(Q)^2]}{\alpha}.$$
These are one-dimensional integrals over $q$ of lattice probabilities (`discrete.py`). They are exact
in the $N\to\infty$ limit and, like §2, free of $N$. Checks against the repository simulator at
$N=5000$ (400 conferences, $R=4$, $\sigma_\varepsilon=2$): disagreement 0.4908 vs $0.4907\pm0.0006$ (int10), 0.4945
vs $0.4953\pm0.0006$ (six), 0.4971 vs $0.4969\pm0.0006$ (ICLR six), 0.5073 vs $0.5062\pm0.0006$ (five); precision
0.6328, 0.6296, 0.6274, 0.6186 against simulated 0.6320, 0.6281, 0.6268, 0.6178 (`t_disc.py`).

Because the disagreement is now a deterministic function of $\sigma_\varepsilon$, the §7.3 recalibration can be
done by root-finding with no Monte Carlo noise. Calibrated to the NeurIPS 2021 target
($\alpha=0.227$, $D=0.50696$) at $R=4$ (`run_discrete.py`, `out/discrete.json`):

**Table 12a.** Per-scale calibration to the NeurIPS 2021 target ($R=4$, $\sigma_q=1.2$, $\sigma_u=0$). "latent $\rho^2$" is
$\sigma_q^2/(\sigma_q^2+\sigma_\varepsilon^2/R)$ of the unsnapped mean. $\pi_{\rm top}$ is the share of papers whose four reviews all sit at
the top point. $N^\ast=K/\pi_{\rm top}$. The simulator runs use 1000 conferences of $N=5000$ (`peerreview.simulate.disagreement`).

| scale | calibrated $\sigma_\varepsilon$ | latent $\rho^2$ | prec, $\alpha=0.227$ | simulator prec, $N=5000$ | simulator $D$, $N=5000$ (z vs 0.50696) | prec, $\alpha=0.25$ | $D$, $\alpha=0.25$ | prec, $p=1\%$ | prec, $p=0.5\%$ | $\pi_{\rm top}$ | $N^\ast$, $K=1$ | $N^\ast$, $K=10$ | $N^\ast$, $K=30$ |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| continuous | 2.1433 | 0.5563 | 0.6189 | – | – | 0.6342 | 0.4875 | 0.3126 | 0.2728 | 0 | $\infty$ | $\infty$ | $\infty$ |
| int10 | 2.1113 | 0.5637 | 0.6189 | 0.6192 | 0.5066 ± 0.0004 (−1.08) | 0.6345 | 0.4873 | 0.2974 | 0.2531 | 1.07e-04 | 9308 | 93078 | 279235 |
| six | 2.0827 | 0.5704 | 0.6188 | 0.6186 | 0.5076 ± 0.0004 (+1.82) | 0.6313 | 0.4910 | 0.2917 | 0.2517 | 2.52e-04 | 3970 | 39701 | 119102 |
| iclr6 | 2.0688 | 0.5737 | 0.6188 | 0.6189 | 0.5072 ± 0.0004 (+0.71) | 0.6345 | 0.4873 | 0.2894 | 0.2453 | 3.07e-04 | 3253 | 32531 | 97594 |
| five | 1.9974 | 0.5908 | 0.6188 | 0.6191 | 0.5066 ± 0.0004 (−0.96) | 0.6327 | 0.4893 | 0.3032 | 0.2456 | 3.71e-04 | 2695 | 26953 | 80859 |

What the table shows:
1. Snapping adds noise. So a coarser scale needs a smaller $\sigma_\varepsilon$ to reach the same $D$; the latent $\rho^2$ rises
   from 0.556 (continuous) to 0.591 (five points).
2. After the recalibration, the precision at the calibration rate $\alpha=0.227$ equals the continuous value to
   $10^{-4}$ for every scale. The simulator agrees to $4\times10^{-4}$. At the calibration point, $D$ and precision move together.
3. At $\alpha=0.25$ the scales stay within 0.003 of the continuous model. At $p=1\,\%$ they lose 0.010 to 0.023, and at
   $p=0.5\,\%$ they lose 0.020 to 0.028. At small $p$ the threshold tie class is a large share of the selected set.
4. The simulated $D$ at $N=5000$ lies within $1.9\sigma$ of the target for all four scales.

**Fixed-number selection at large $N$: the top tie class.** Let $\pi_{\rm top}=E_q[P(\text{review at the top point}\mid q)^R]$
be the share of papers whose $R$ reviews all sit at the top point. The top tie class holds about $N\pi_{\rm top}$
papers. Once $N\pi_{\rm top}\gg K$, $\mathrm{Top}_K(S)$ is a uniform draw of $K$ papers from that class (random
tie-breaking). A truly top paper is in the class with probability $p_{\rm top}(Q_{(j)})^R$, so
$$\mathrm{prec}_K\approx\frac{\sum_{j\le K}E\big[p_{\rm top}(Q_{(j)})^R\big]}{N\,\pi_{\rm top}}\ \xrightarrow{N\to\infty}\ \frac{K}{N\pi_{\rm top}} .$$
This decays like $1/N$: faster than the continuous $N^{-(1-\rho)/(1+\rho)}$. A bounded scale with
uninformed tie-breaking turns the top of the ranking into a lottery among the papers that every
reviewer gave the top mark. The crossover sample size is $N^\ast=K/\pi_{\rm top}$ (table above). Continuous
scores are the opposite extreme (an AC who breaks ties with full information).

**Table 12b** (`sim_discrete_b.py`, `sim_discrete_c.py`, `report12c.py`). Fixed-$K$ precision with snapped scores ($R=4$,
$\sigma_q=1.2$, calibrated $\sigma_\varepsilon$ of Table 12a, random tie-breaking by the simulator's jitter). The repository simulator
against the top-tie-class law (`discrete.prec_tie_regime`) and against the continuous model with the same calibration
(exact quadrature at $\rho=0.7459$). Conferences are pooled over two sets of runs with different salts. The z column uses
the law's own variance, $\text{law}/(Kn)$ for $n$ conferences, because the sample SE is unreliable when hits are rare.

| scale | $N$ | conferences | $N\pi_{\rm top}/K$ | $K$ | simulator prec$_K$ | tie-class law | z | continuous model |
|---|---|---|---|---|---|---|---|---|
| five | 1e+04 | 2000 | 3.7 | 1 | 0.0560 ± 0.0051 | 0.0491 | +1.43 | 0.1055 |
| five | 1e+04 | 2000 | 0.7 | 5 | 0.1337 ± 0.0032 | 0.1531 | -5.39 (law not applicable) | 0.1687 |
| five | 1e+04 | 2000 | 0.4 | 10 | 0.1555 ± 0.0024 | 0.2310 | -25.33 (law not applicable) | 0.1964 |
| five | 1e+04 | 2000 | 0.1 | 30 | 0.2204 ± 0.0016 | 0.4026 | -91.00 (law not applicable) | 0.2454 |
| five | 1e+05 | 4400 | 37.1 | 1 | 0.0075 ± 0.0013 | 0.0089 | -0.99 | 0.0697 |
| five | 1e+05 | 4400 | 7.4 | 5 | 0.0330 ± 0.0012 | 0.0328 | +0.16 | 0.1113 |
| five | 1e+05 | 4400 | 3.7 | 10 | 0.0548 ± 0.0011 | 0.0545 | +0.21 | 0.1291 |
| five | 1e+05 | 4400 | 1.2 | 30 | 0.1141 ± 0.0008 | 0.1146 | -0.62 (law not applicable) | 0.1599 |
| five | 1e+06 | 900 | 371.0 | 1 | 0.0022 ± 0.0016 | 0.0013 | +0.75 | 0.0467 |
| five | 1e+06 | 900 | 74.2 | 5 | 0.0056 ± 0.0011 | 0.0054 | +0.14 | 0.0745 |
| five | 1e+06 | 900 | 37.1 | 10 | 0.0102 ± 0.0010 | 0.0096 | +0.62 | 0.0862 |
| five | 1e+06 | 900 | 12.4 | 30 | 0.0241 ± 0.0009 | 0.0228 | +1.45 | 0.1061 |
| int10 | 1e+04 | 2000 | 1.1 | 1 | 0.0575 ± 0.0052 | 0.0767 | -3.23 (law not applicable) | 0.1055 |
| int10 | 1e+04 | 2000 | 0.2 | 5 | 0.1316 ± 0.0032 | 0.2146 | -20.23 (law not applicable) | 0.1687 |
| int10 | 1e+04 | 2000 | 0.1 | 10 | 0.1620 ± 0.0024 | 0.3072 | -44.50 (law not applicable) | 0.1964 |
| int10 | 1e+04 | 2000 | 0.0 | 30 | 0.2200 ± 0.0016 | 0.4924 | -133.47 (law not applicable) | 0.2454 |
| int10 | 1e+05 | 4400 | 10.7 | 1 | 0.0186 ± 0.0020 | 0.0163 | +1.25 | 0.0697 |
| int10 | 1e+05 | 4400 | 2.1 | 5 | 0.0551 ± 0.0015 | 0.0545 | +0.40 (law not applicable) | 0.1113 |
| int10 | 1e+05 | 4400 | 1.1 | 10 | 0.0839 ± 0.0013 | 0.0864 | -1.86 (law not applicable) | 0.1291 |
| int10 | 1e+05 | 4400 | 0.4 | 30 | 0.1189 ± 0.0009 | 0.1673 | -47.17 (law not applicable) | 0.1599 |
| int10 | 1e+06 | 900 | 107.4 | 1 | 0.0022 ± 0.0016 | 0.0028 | -0.31 | 0.0467 |
| int10 | 1e+06 | 900 | 21.5 | 5 | 0.0111 ± 0.0015 | 0.0105 | +0.42 | 0.0745 |
| int10 | 1e+06 | 900 | 10.7 | 10 | 0.0183 ± 0.0014 | 0.0178 | +0.37 | 0.0862 |
| int10 | 1e+06 | 900 | 3.6 | 30 | 0.0387 ± 0.0012 | 0.0394 | -0.56 | 0.1061 |

**Reading Table 12b.**
- Where $N\pi_{\rm top}/K\ge3$ (13 cells), the tie-class law matches the simulator: largest $\lvert z\rvert=1.45$, RMS 0.80.
  One early run (int10, $N=10^5$, $K=1$, 400 conferences) gave $0.040\pm0.010$ against 0.0163. The 4000 fresh conferences
  bring the pooled value to $0.0186\pm0.0020$ ($z=+1.25$). The first gap was chance.
- In these runs the law also holds at $N\pi_{\rm top}/K$ between 1 and 2.1 (int10 $N=10^5$, $K=5,10$; five $N=10^5$, $K=30$;
  all within 1.9 SE). Below 0.7 it fails, as it must: the top class then holds fewer than $K$ papers, and the selection
  reaches into lower classes.
- Snapping lowers fixed-$K$ precision far below the continuous model at the same calibration, already at $N=10^4$
  ($K=5$: 0.13 for both scales against 0.169). At $N=10^6$ the loss is a factor 2.7 to 4.4 at $K=30$ (int10 0.039, five 0.024,
  continuous 0.106) and a factor of about 20 at $K=1$ (0.0022 for both scales, continuous 0.047).
- The decay steepens towards the law's $1/N$: for int10, $K=30$, the log-log slope from $10^5$ to $10^6$ is $-0.49$; the
  continuous model gives $-0.18$.

**Qualitatively, then.** (a) Fixed-percentile metrics stay $N$-free; after recalibration to the same
disagreement they differ little from the continuous model at moderate $\alpha$ and lose more at small $p$,
where the threshold class is a larger share of the selected set. (b) Fixed-number metrics
eventually collapse like $K/(N\pi_{\rm top})$; how soon depends on $\pi_{\rm top}$, which is set by the scale's top
point, $\sigma_\varepsilon$, $R$ and the latent placement. (c) At fixed $\sigma_\varepsilon$, more reviewers ($R$) shrink $\pi_{\rm top}$ geometrically
(all $R$ must agree), so they postpone the collapse.

---

## 13. Verification summary

### 13.1 The layers of checking

Each result above rests on a chain: tail-accurate orthant cells, then the exact finite-$N$ quadrature,
then the asymptotic formulas, then the repository simulator. Each link is checked against an
independent reference.

| link | reference | section | worst disagreement |
|---|---|---|---|
| orthant cells $P_2$ and $\bar\Phi(q)-P_2$ (`fk.cells`) | 40-digit mpmath at 60 random points, thresholds to 14, $\rho\le0.97$ | §4.1 | $4\times10^{-11}$ and $4\times10^{-9}$ relative |
| exact finite-$N$ quadrature (`fk.overlap_exact`, `best_exact`) | $\rho=0$ closed form; $N=2$ closed form; $N=3$ identity; 4-D orthant probabilities at $N=3$; own Monte Carlo at $N\le50$ (84 cells) and at $N=10^3$, $K=30$ to 150 ($8\times10^5$ conferences); slow reference code; grid refinement | §4.1, §7, §13.2 | $2\times10^{-10}$; $4\times10^{-7}$ (default grid, $N=2$); $\lvert z\rvert\le2.17$; $3\times10^{-15}$; $3\times10^{-10}$ |
| leading law with prefactor, $\beta_K$, $\omega_K$ | exact quadrature at $N$ to $10^{300}$ | §4.4, Tables 4a, 4b | exact/pure in $[0.986,1.002]$ at $10^{300}$; $\beta_K$ to 3 or 4 digits; $\omega_K\varepsilon_N$ to the expected $1/b^2$ |
| hybrid $R_K\times$ fixed-percentile formula | exact quadrature, $N=10^3$ to $10^6$ | §4.5 | 8 % ($K=1$, $\rho=0.9$, $N=10^3$); 1.1 % for $K\ge5$ |
| fixed-percentile finite-$N$ deficit $\kappa/K$ | exact quadrature, $K=3$ to 200 | §2, Table 2 | $\kappa$ settles in $K$; $p\to0$ value $-\rho/(1+\rho)^2$ |
| best paper: Poisson route against binomial | exact quadrature | §7, Table 7 | relative $O(K/N)$; $P_{\rm best}(1)=\mathrm{prec}_1$ to $3\times10^{-9}$ |
| winner rank | exchangeability identity; semi-asymptotic quantiles; Poisson route at $10^{12}$ | §8, Tables 8a, 8b | 47 of 48 simulated medians inside 2 SE |
| containment | deterministic-threshold integral against exact | §6, Table 6 | $2\times10^{-3}$ at $N=10^3$, $10^{-4}$ at $N\ge10^4$ |
| tails | marked Poisson limits; Gil–Pelaez noise law; simulator | §10, Tables 10a–c | fixed percentile: 0.0005 over 27 cells |
| snapped scores | 1-D lattice integrals; top-tie-class law; simulator | §12, Tables 12a, 12b | $\lvert z\rvert\le1.45$ in the law's regime |
| repository simulator, Gaussian model | all of the above | §13.2, §13.3 | RMS $z=1.09$ over 2119 cells (Table 13a); RMS $z=1.05$ against exact finite-$N$ values at fixed $\alpha$ (Table 13c) |

### 13.2 The repository simulator, Gaussian model

**Runs** (`sim_gauss.py`, `sim_smallN.py`). `ReviewModel(R=1, sigma_q=1, sigma_u=0, sigma_eps=sqrt(1/rho^2-1))`, so the
standardised (quality, score) pair is bivariate normal with correlation $\rho$, for $\rho\in\{0.5,0.7459,0.9\}$.
`simulate` with two committees at $N=10^3$, $2\times10^3$, $5\times10^3$, $10^4$, $2\times10^4$, $5\times10^4$, $10^5$, $2\times10^5$, $5\times10^5$, $10^6$
(10,000 down to 200 conferences), with extra runs at $10^5$ (8000) and $10^6$ (1000), and fresh runs of
$10^5$ conferences at $N=10^3$ and $2\times10^3$. `simulate_best_paper` at $N=10^3$ to $10^6$ (40,000 down to 1500 conferences).

**Exact values** (`run_simcompare.py`, `out/simcompare.json`). For each simulator metric:
- `prec_K`, `ovl_K`, `c2x_K`, `c10x_K`, `c1pct_K` (fixed $K$): the exact quadrature of §4.1 with $M=K,2K,10K,\mathrm{round}(0.01N)$,
  at $\rho$ (or $\rho^2$ for the overlap).
- `prec_p…pct` (fixed $p$, $K=\mathrm{round}(pN)$): the exact quadrature when $K\le300$, else the $N$-free limit.
- `pctl_K` (mean true percentile): the exact 1-D integral of §6.
- `prec_acc…`, `dis_acc…` (fixed $\alpha$): the $N$-free limits of §2 and §3 at $\alpha_{\rm eff}=\mathrm{round}(\alpha N)/N$.
- `corr_qs`, `corr_s12`: $\rho$ and $\rho^2$.

**Table 13a** (`report13.py`). z = (simulator − exact)/(simulator SE), grouped by metric family. Cells with a zero
SE are left out (see below).

| metric family | cells | mean z | RMS z | max abs z | error measure | median error | largest error (cell) | largest relative error where the relative SE is below 1 % | cells with abs z > 3 |
|---|---|---|---|---|---|---|---|---|---|
| c10x at fixed K (exact) | 144 | -0.03 | 1.01 | 3.21 | relative | 0.0042 | 0.72 (K1, rho=0.5, N=1e+06, z=-2.6) | 0.013 (K1, rho=0.9, N=1e+05, z=+1.7; 82 cells) | K5, rho=0.5, N=1e+06 (-3.2) |
| c10x at fixed p (exact) | 27 | -0.17 | 0.94 | 2.22 | relative | 0.0007 | 0.018 (p0.3pct, rho=0.5, N=1e+03, z=-2.2) | 0.018 (p0.3pct, rho=0.5, N=1e+03, z=-2.2; 27 cells) | – |
| c1pct at fixed K (exact) | 136 | +0.11 | 1.10 | 2.85 | relative | 0.002 | 0.16 (K1, rho=0.5, N=1e+06, z=-2.5) | 0.021 (K10, rho=0.5, N=1e+03, z=-2.7; 110 cells) | – |
| c1pct at fixed p (exact) | 27 | -0.19 | 1.25 | 2.66 | relative | 0.0024 | 0.032 (p0.3pct, rho=0.5, N=1e+03, z=-2.6) | 0.021 (p1pct, rho=0.5, N=1e+03, z=-2.7; 25 cells) | – |
| c2x at fixed K (exact) | 180 | -0.09 | 1.02 | 2.46 | relative | 0.0057 | 0.94 (K1, rho=0.5, N=5e+05, z=+1.2) | 0.017 (K10, rho=0.7459, N=5e+04, z=+1.8; 88 cells) | – |
| c2x at fixed p (exact) | 66 | -0.07 | 1.07 | 3.03 | relative | 0.0012 | 0.034 (p0.3pct, rho=0.5, N=1e+03, z=-2.3) | 0.011 (p0.5pct, rho=0.7459, N=1e+03, z=-2.0; 63 cells) | p1pct, rho=0.9, N=2e+04 (+3.0) |
| corr_qs | 36 | -0.28 | 1.17 | 3.07 | absolute | 1.9e-05 | 0.00052 (rho=0.5, N=1e+03, z=-2.2) | – | rho=0.5, N=1e+04 (-3.1) |
| corr_s12 | 36 | -0.30 | 1.09 | 2.09 | absolute | 3.2e-05 | 0.00054 (rho=0.5, N=1e+03, z=-1.8) | – | – |
| dis at fixed alpha (N-free limit) | 252 | +0.54 | 1.24 | 3.67 | absolute | 5.3e-05 | 0.0011 (acc0.10, rho=0.5, N=1e+03, z=+3.0) | – | acc0.10, rho=0.5, N=1e+03 (+3.0); acc0.15, rho=0.9, N=5e+03 (+3.0); acc0.20, rho=0.9, N=5e+03 (+3.7) |
| ovl at fixed K (exact) | 172 | -0.21 | 1.03 | 3.64 | relative | 0.013 | 2 (K1, rho=0.5, N=2e+05, z=+0.7) | 0.012 (K10, rho=0.7459, N=5e+03, z=-1.3; 56 cells) | K30, rho=0.5, N=1e+06 (-3.6); K5, rho=0.7459, N=1e+06 (-3.2) |
| ovl at fixed p (N-free limit) | 78 | -0.16 | 0.94 | 2.83 | absolute | 0.0001 | 0.0008 (p0.5pct, rho=0.9, N=5e+05, z=-1.9) | – | – |
| ovl at fixed p (exact) | 66 | -0.25 | 0.98 | 2.70 | relative | 0.0027 | 0.024 (p0.3pct, rho=0.5, N=2e+04, z=-2.7) | 0.024 (p0.3pct, rho=0.5, N=2e+04, z=-2.7; 54 cells) | – |
| pctl at fixed K (exact) | 180 | +0.20 | 1.03 | 3.10 | absolute | 7e-05 | 0.0055 (K1, rho=0.5, N=1e+06, z=-1.1) | – | K1, rho=0.9, N=2e+05 (+3.1) |
| pctl at fixed p (N-free limit) | 78 | +0.41 | 0.98 | 2.31 | absolute | 2.9e-05 | 0.00029 (p0.3pct, rho=0.5, N=1e+06, z=+1.4) | – | – |
| pctl at fixed p (exact) | 66 | +0.26 | 1.16 | 4.36 | absolute | 5.9e-05 | 0.00064 (p0.3pct, rho=0.5, N=2e+03, z=+1.0) | – | p1pct, rho=0.9, N=2e+04 (+4.4) |
| prec at fixed K (exact) | 179 | -0.15 | 1.10 | 3.11 | relative | 0.0076 | 1.7 (K1, rho=0.5, N=5e+05, z=+1.4) | 0.025 (K100, rho=0.5, N=1e+05, z=+2.7; 80 cells) | K1, rho=0.5, N=2e+05 (-3.1) |
| prec at fixed alpha (N-free limit) | 252 | -0.54 | 1.21 | 3.20 | absolute | 4.6e-05 | 0.00091 (acc0.10, rho=0.5, N=1e+03, z=-2.2) | – | acc0.15, rho=0.9, N=1e+03 (-3.0); acc0.20, rho=0.9, N=1e+03 (-3.2); acc0.40, rho=0.9, N=5e+04 (-3.1) |
| prec at fixed p (N-free limit) | 78 | -0.25 | 1.01 | 2.77 | absolute | 0.00013 | 0.0011 (p0.5pct, rho=0.7459, N=2e+05, z=-2.6) | – | – |
| prec at fixed p (exact) | 66 | -0.27 | 1.02 | 2.86 | relative | 0.0013 | 0.032 (p0.3pct, rho=0.5, N=1e+03, z=-1.6) | 0.021 (p1pct, rho=0.5, N=1e+03, z=-2.7; 63 cells) | – |

All 2119 cells: mean $z=-0.04$, RMS $z=1.09$; $\lvert z\rvert>2$ in 7.5 % of cells (normal: 4.6 %), $\lvert z\rvert>3$ in 0.66 % (normal: 0.27 %).
17 cells have a zero SE and are left out: every conference gave the same value (no hit at all for `ovl` at $\rho=0.5$
and `prec_K1` at $\rho=0.5$, $N=10^6$; full containment for `c1pct` at $\rho=0.9$, $N\ge2\times10^5$).

**Reading Table 13a.**
- Every family has a mean $z$ near 0 and an RMS $z$ near 1. The simulator and the exact formulas agree over the
  whole grid.
- The two fixed-$\alpha$ families are compared with $N$-free limits. They carry the finite-$N$ deficit of §2:
  mean $z=-0.54$ for precision and $+0.54$ for disagreement, the predicted signs. Without them, 1615 cells give RMS
  $z=1.045$, $\lvert z\rvert>2$ in 6.3 %, $\lvert z\rvert>3$ in 0.50 %. Table 13c compares the same metrics with the exact finite-$N$ values.
- `corr_qs` and `corr_s12` have mean $z=-0.28$ and $-0.30$. The sample correlation is biased low,
  $E[r]\approx\rho-\rho(1-\rho^2)/(2N)$; at $N=10^3$, $\rho=0.5$ that is $-0.8$ SE.
- The 14 cells with $\lvert z\rvert>3$ fall in three groups.
  (a) Rare hits at $N\ge2\times10^5$, where the sample SE is unreliable. With the variance taken from the exact value,
  `prec_K1` ($\rho=0.5$, $N=2\times10^5$) is at $z=-1.7$, `c10x_K5` ($\rho=0.5$, $N=10^6$) at $-2.5$, and the two $N=10^6$ overlap cells
  at $-2.7$ (§13.3). `pctl_K1` ($\rho=0.9$, $N=2\times10^5$) is a mean of values within $10^{-4}$ of 1.
  (b) Correlated metrics from one run. At $\rho=0.9$, $N=2\times10^4$, six top-of-ranking metrics (the top 1 to 200
  papers) lie at $z=+2.6$ to $+4.4$ in the same 10,000 conferences. At $\rho=0.9$, $N=5\times10^3$, seven fixed-$\alpha$ cells lie
  beyond $\lvert z\rvert=2$ in one run, with precision low and disagreement high together.
  (c) Fixed-$\alpha$ cells at $N=10^3$ that carry the finite-$N$ deficit, and two isolated cells (`corr_qs` at $\rho=0.5$,
  $N=10^4$, $z=-3.1$; `prec_acc0.40` at $\rho=0.9$, $N=5\times10^4$, $z=-3.1$).
- **Error measures** (handoff §6.13). Fixed-$K$ quantities: the median relative error is 0.07 % to 1.3 % by family.
  Among cells whose relative SE is below 1 %, the largest relative error is 1.1 % to 2.5 %, each within 2.7 SE. The
  large relative errors in the "largest error" column are rare-hit cells with relative SE of 50 % or more.
  $N$-free quantities: the median absolute error is $2\times10^{-5}$ to $1.3\times10^{-4}$; the largest is $1.1\times10^{-3}$, within 3 SE
  ($z=+3.0$ at $N=10^3$, where the finite-$N$ deficit adds to it, and $z=-2.6$ at $N=2\times10^5$).

**Table 13c** (`run_acc_exact.py`, `report13d.py`). The finite-$N$ deficit at fixed $\alpha$. At $N=10^3$ and $2\times10^3$
the exact value is below the $N$-free limit by a relative $\kappa/K$ (§2). The large fresh runs resolve it.

| $\rho$ | $N$ | $\alpha$ | metric | exact finite $N$ | $N$-free limit | simulator, `sim_gauss` | z vs exact | simulator, fresh runs | z vs exact | z vs limit |
|---|---|---|---|---|---|---|---|---|---|---|
| 0.5 | 1000 | 0.1 | prec | 0.32357 | 0.32402 | 0.32311 ± 0.00041 | -1.13 | 0.32368 ± 0.00013 (100000) | +0.88 | -2.63 |
| 0.5 | 1000 | 0.1 | dis | 0.80685 | 0.80666 | 0.80775 ± 0.00036 | +2.51 | 0.80672 ± 0.00011 (100000) | -1.18 | +0.47 |
| 0.5 | 1000 | 0.25 | prec | 0.48091 | 0.48110 | 0.48058 ± 0.00025 | -1.30 | 0.48096 ± 0.00008 (100000) | +0.69 | -1.73 |
| 0.5 | 1000 | 0.25 | dis | 0.64285 | 0.64276 | 0.64319 ± 0.00026 | +1.34 | 0.64285 ± 0.00008 (100000) | +0.01 | +1.15 |
| 0.5 | 2000 | 0.1 | prec | 0.32379 | 0.32402 | 0.32416 ± 0.00029 | +1.30 | 0.32391 ± 0.00009 (100000) | +1.33 | -1.16 |
| 0.5 | 2000 | 0.1 | dis | 0.80676 | 0.80666 | 0.80707 ± 0.00025 | +1.21 | 0.80671 ± 0.00008 (100000) | -0.60 | +0.57 |
| 0.7459 | 1000 | 0.1 | prec | 0.50779 | 0.50859 | 0.50897 ± 0.00040 | +2.90 | 0.50815 ± 0.00013 (100000) | +2.78 | -3.37 |
| 0.7459 | 1000 | 0.1 | dis | 0.64042 | 0.63990 | 0.64046 ± 0.00041 | +0.09 | 0.64030 ± 0.00013 (100000) | -0.92 | +3.07 |
| 0.7459 | 1000 | 0.25 | prec | 0.63395 | 0.63426 | 0.63401 ± 0.00023 | +0.29 | 0.63407 ± 0.00007 (100000) | +1.75 | -2.57 |
| 0.7459 | 1000 | 0.25 | dis | 0.48773 | 0.48751 | 0.48796 ± 0.00025 | +0.94 | 0.48769 ± 0.00008 (100000) | -0.47 | +2.30 |
| 0.7459 | 2000 | 0.1 | prec | 0.50819 | 0.50859 | 0.50872 ± 0.00029 | +1.84 | 0.50818 ± 0.00009 (100000) | -0.12 | -4.45 |
| 0.7459 | 2000 | 0.1 | dis | 0.64016 | 0.63990 | 0.63974 ± 0.00029 | -1.45 | 0.64024 ± 0.00009 (100000) | +0.84 | +3.67 |
| 0.9 | 1000 | 0.1 | prec | 0.68755 | 0.68865 | 0.68794 ± 0.00036 | +1.07 | 0.68747 ± 0.00011 (100000) | -0.73 | -10.39 |
| 0.9 | 1000 | 0.1 | dis | 0.42768 | 0.42677 | 0.42736 ± 0.00040 | -0.79 | 0.42770 ± 0.00013 (100000) | +0.21 | +7.42 |
| 0.9 | 1000 | 0.25 | prec | 0.77175 | 0.77218 | 0.77188 ± 0.00019 | +0.67 | 0.77182 ± 0.00006 (100000) | +1.11 | -5.84 |
| 0.9 | 1000 | 0.25 | dis | 0.31569 | 0.31533 | 0.31554 ± 0.00022 | -0.64 | 0.31567 ± 0.00007 (100000) | -0.24 | +4.89 |
| 0.9 | 2000 | 0.1 | prec | 0.68810 | 0.68865 | 0.68822 ± 0.00025 | +0.48 | 0.68814 ± 0.00008 (100000) | +0.47 | -6.43 |
| 0.9 | 2000 | 0.1 | dis | 0.42723 | 0.42677 | 0.42724 ± 0.00028 | +0.04 | 0.42717 ± 0.00009 (100000) | -0.69 | +4.44 |


**Reading Table 13c.**
- With $10^5$ conferences per cell the simulator resolves the finite-$N$ deficit. Against the exact finite-$N$
  value the 18 fresh cells give RMS $z=1.05$ (largest 2.78). Against the $N$-free limit they give RMS $z=4.5$
  (largest 10.4, at $\rho=0.9$, $N=10^3$, $\alpha=0.10$). So the $O(1/K)$ deficit of §2 is real, it has the predicted size,
  and the simulator reproduces it.
- The largest cell ($\rho=0.7459$, $N=10^3$, $\alpha=0.10$; the same quantity as `prec_K100` at $N=10^3$) is $+2.8$ in the fresh
  runs and $+2.9$ in the `sim_gauss` run. I checked it four ways (`t_G_check.py`, `t_owen_region.py`, `t_alt_grid.py`,
  `check_N1000_K100.py`, `check_N1000_mc2.py`; `out/check_N1000_summary.json`):
  (a) the binomial kernel $G$ against a direct scipy convolution at 25 nodes: largest relative difference $2\times10^{-13}$;
  (b) the orthant cells in the Owen-$T$ region against 30-digit mpmath at 192 points: $2\times10^{-10}$;
  (c) a refined $t$-grid and an independent Gauss–Legendre grid in $(q,s)$: 0.50779469 in all three, to $10^{-9}$;
  (d) two own Monte Carlo runs of $4\times10^5$ conferences each: $z=+2.5$ and $-0.7$ (pooled $+1.3$); the same runs give
  $z=+0.5$ ($K=30$), $-0.1$ ($K=50$) and $-1.6$ ($K=150$).
  So the exact value stands. The cell is a fluctuation that the search picked out.

### 13.3 The two-committee overlap at $N=10^6$

Table 9 shows low simulated overlaps at $N=10^6$ for $\rho=0.5$ and $\rho=0.7459$ ($z$ down to $-3.5$). I ran four
checks.

1. **Code replay** (`check_ovl_replay.py`). I reran `simulate_chunk` with seeds 0 to 59 (240 conferences,
   $\rho=0.7459$), regenerated the same draws with the repository's own `sample_quality`, `sample_scores` and
   `jitter`, and recomputed the overlap with independent code (full sort, threshold, count). The largest
   difference per conference is 0. So the simulator computes the overlap it should from its draws.
2. **The draws.** The same draws give `corr_qs`, `corr_s12`, precision, containment and the best-paper
   metrics, and all of these agree with the exact values (Table 13a, Table 7). A defect in the draws
   would show there.
3. **Own Monte Carlo** (`check_ovl_1e6*.py`, plain numpy, 6000 conferences at $\rho=0.7459$): it agrees with
   the exact value at every $K$ ($\lvert z\rvert\le0.3$). So the exact value is right.
4. **Fresh repository runs** with new salts.

**Table 13b** (`report13c.py`). Every $N=10^6$ overlap run. In brackets: $z$ against the exact value, with the
SE taken from the exact value, $\sqrt{p(1-p)/(Kn)}$, because the sample SE is zero when no conference has a hit.

| $\rho$ | source | conferences | ovl$_{1}$ | ovl$_{5}$ | ovl$_{10}$ | ovl$_{30}$ | ovl$_{100}$ |
|---|---|---|---|---|---|---|---|
| 0.5 | **exact** | – | **0.00012** | **0.00037** | **0.00058** | **0.00116** | **0.00245** |
| 0.5 | sim_gauss (b-full-extra) | 1000 | 0.00000 (-0.4) | 0.00000 (-1.4) | 0.00020 (-1.6) | 0.00063 (-2.7) | 0.00247 (+0.2) |
| 0.5 | sim_gauss (b-full) | 200 | 0.00000 (-0.2) | 0.00000 (-0.6) | 0.00000 (-1.1) | 0.00100 (-0.4) | 0.00265 (+0.6) |
| 0.5 | repo chk5 | 1500 | 0.00000 (-0.4) | 0.00040 (+0.1) | 0.00047 (-0.6) | 0.00098 (-1.1) | 0.00237 (-0.6) |
| 0.5 | repo chk6 | 1500 | 0.00000 (-0.4) | 0.00040 (+0.1) | 0.00053 (-0.2) | 0.00104 (-0.7) | 0.00241 (-0.3) |
| 0.5 | repository, all runs | 4200 | 0.00000 (-0.7) | 0.00029 (-0.7) | 0.00040 (-1.5) | 0.00092 (-2.5) | 0.00242 (-0.3) |
| 0.7459 | **exact** | – | **0.00680** | **0.01335** | **0.01696** | **0.02429** | **0.03568** |
| 0.7459 | sim_gauss (b-full-extra) | 1000 | 0.00300 (-1.5) | 0.00900 (-2.7) | 0.01420 (-2.1) | 0.02270 (-1.8) | 0.03623 (+0.9) |
| 0.7459 | sim_gauss (b-full) | 200 | 0.00500 (-0.3) | 0.01100 (-0.6) | 0.01700 (+0.0) | 0.02550 (+0.6) | 0.03555 (-0.1) |
| 0.7459 | repo chk1 | 500 | 0.00200 (-1.3) | 0.00840 (-2.2) | 0.01080 (-3.4) | 0.02240 (-1.5) | 0.03524 (-0.5) |
| 0.7459 | repo chk2 | 500 | 0.00800 (+0.3) | 0.01200 (-0.6) | 0.01420 (-1.5) | 0.02220 (-1.7) | 0.03504 (-0.8) |
| 0.7459 | own MC seed 12 | 1500 | 0.00733 (+0.2) | 0.01480 (+1.1) | 0.01747 (+0.5) | 0.02353 (-1.0) | 0.03537 (-0.6) |
| 0.7459 | own MC seed 11 | 1500 | 0.00333 (-1.6) | 0.01200 (-1.0) | 0.01607 (-0.8) | 0.02438 (+0.1) | 0.03552 (-0.3) |
| 0.7459 | own MC seed 21 | 1500 | 0.01133 (+2.1) | 0.01480 (+1.1) | 0.01767 (+0.7) | 0.02482 (+0.7) | 0.03613 (+0.9) |
| 0.7459 | own MC seed 22 | 1500 | 0.00667 (-0.1) | 0.01253 (-0.6) | 0.01693 (-0.0) | 0.02424 (-0.1) | 0.03561 (-0.2) |
| 0.7459 | repo chk3 | 1500 | 0.00867 (+0.9) | 0.01547 (+1.6) | 0.01947 (+2.4) | 0.02456 (+0.4) | 0.03552 (-0.3) |
| 0.7459 | repo chk4 | 1500 | 0.00400 (-1.3) | 0.01187 (-1.1) | 0.01473 (-2.1) | 0.02431 (+0.0) | 0.03575 (+0.1) |
| 0.7459 | repository, all runs | 5200 | 0.00538 (-1.2) | 0.01200 (-1.9) | 0.01565 (-2.3) | 0.02373 (-1.4) | 0.03565 (-0.1) |
| 0.7459 | own MC, all runs | 6000 | 0.00717 (+0.3) | 0.01353 (+0.3) | 0.01703 (+0.1) | 0.02424 (-0.1) | 0.03566 (-0.1) |

**Reading Table 13b.** The runs that raised the question (`sim_gauss`, salt `b-full-extra`, 1000 conferences) are
low at both $\rho$. The fresh runs are close to exact: at $\rho=0.7459$ chk3 and chk4 (3000 conferences) give
$z=+0.3,+0.2,+0.3$ at $K=5,10,30$; at $\rho=0.5$ chk5 and chk6 (3000 conferences) give $z=+0.2,-0.6,-1.3$. Without the
`sim_gauss` runs, the repository runs at $\rho=0.7459$ (chk1 to chk4, 4000 conferences) give
$z=-0.7,-1.6,-0.9$ at $K=5,10,30$. The values at different $K$ in one run are strongly correlated, so the table holds
far fewer independent tests than cells. With all runs pooled, the largest deficit is $z=-2.5$ ($\rho=0.5$, $K=30$).

**Conclusion.** I found no defect in the simulator. The replay shows that the computation is right. The
draws pass every other check. The fresh runs agree with the exact values. The remaining pooled deficit is
within what chance and the post-hoc choice of the first runs can produce. This is an open item only in
the sense that a decisive test needs about $2\times10^4$ conferences at $N=10^6$ (for a 5 % effect at $3\sigma$ at $K=10$).

### 13.4 The repository code

I read `model.py`, `simulate.py`, `calibrate.py` and `analytic.py`. I did not edit them. I found no bug.

- `analytic.py` implements the formulas of §1 to §3 and §11 exactly (checks in those sections).
- `analytic.P2_diag` uses Owen's $T$. It loses relative accuracy far in the tail (threshold $\ge12$), which the
  handoff range never reaches (§2). This is a limit of the formula, not a bug.
- `simulate.py`: the replay of §13.3 confirms the overlap computation, and every other metric agrees with
  its exact value (Table 13a, Table 7, Table 8b).
- The simulator's SE is the sample SE over conferences. For a rare-hit metric (overlap at $\rho=0.5$,
  $N=10^6$) it is zero or too small when few conferences have a hit. A z-score from it then overstates the
  deviation (Table 9 shows $z=-3.5$ there). This is a property of the estimator, not a bug. A z-score with the
  variance taken from the exact value (Table 13b) is the robust check.
- `model.jitter` breaks ties uniformly at random for snapped scores. The tie-class law of §12 assumes
  exactly that, and it agrees with the simulator (Table 12b).
- My own code has one known limit: scipy's `bdtr` fails for $n\approx10^{12}$, so §8 uses the Poisson route
  there (checked against the binomial at $N=10^8$ to $6\times10^{-9}$).
