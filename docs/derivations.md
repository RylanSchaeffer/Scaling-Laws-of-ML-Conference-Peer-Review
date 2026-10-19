# Derivations for handoff §6: the final, reconciled version

This document gives the final derivations of handoff §6, items 1 to 13. It merges two
independent derivations, `docs/derivations/notes_a.md` (notes A) and `docs/derivations/notes_b.md`
(notes B). Section R lists every point where the two notes differ and how it was settled. Each
result is followed by its numerical check.

The code is Part 2 of `src/peerreview/analytic.py`. The tests are in `tests/test_analytic.py`.
"Exact" below means the finite-$N$ integral of §4.1, as `analytic.py` evaluates it (composite
Gauss–Legendre quadrature in tail coordinates; relative error about $10^{-9}$, for $N$ up to $10^{300}$).
Each number can be reproduced with the function that the text names.

---

## Notation

| symbol | meaning |
|---|---|
| $X=Q^\ast$, $Y=S^\ast$ | standardised quality and score; standard bivariate normal with correlation $\rho$ |
| $\tau=\sqrt{1-\rho^2}$ | SD of $X$ given $Y$ (and of $Y$ given $X$) |
| $c=1/(1+\rho)$, $\kappa=\rho/(1+\rho)=1-c$ | tail exponents of the Gaussian copula |
| $\beta=(1-\rho)/(1+\rho)=1-2\kappa=2c-1$ | decay exponent of fixed-$K$ precision |
| $\bar\Phi=1-\Phi$; $z_p=\bar\Phi^{-1}(p)$ | upper tail; upper $p$-quantile |
| $\phi_2(x,y;r)$, $P_2(a,b;r)=P(X>a,Y>b)$ | bivariate normal density and upper orthant |
| $b_N=\bar\Phi^{-1}(1/N)$, $a_N=N\phi(b_N)$ | location and inverse scale of the top order statistics; $a_N=b_N+1/b_N+O(b_N^{-3})$, $b_N^2=2\log N-\log(4\pi\log N)+o(1)$ |
| $\varepsilon_N=e^{\kappa b_N^2}/(N\tau)=N\phi_2(b_N,b_N)/a_N^2$ | mean number of papers in both rescaled tops |
| $I_n=\Gamma(n+c)/(c\,\Gamma(n))$ | basic integral of the point-process limit |
| $R_K=[\Gamma(K+c)/(\Gamma(K)K^c)]^2$ | finite-$K$ factor (a Jensen gap) |
| $F_n(\lambda)=P(\mathrm{Pois}(\lambda)\le n-1)$, $\pi_n(\lambda)=e^{-\lambda}\lambda^n/n!$ | Poisson cdf and pmf |
| $D_n=\psi(n+c)-(1+\rho)$, $P_n=\psi'(n+c)$ | moments of the point-process weight (§4.4) |
| $\mathrm{prec}_{N,K}=E\lvert\mathrm{Top}_K(Y)\cap\mathrm{Top}_K(X)\rvert/K$ | fixed-number precision |

**Symbol clash.** Notes A use $\kappa=\rho/(1+\rho)$ and $\beta=(1-\rho)/(1+\rho)$. Notes B use
$\kappa_B=(1-\rho)/(1+\rho)$, which is $\beta$ here. Notes A write $B_N$ for $b_N$ and $F_K$ for $R_K$.
This document uses A's $\kappa$ and $\beta$, and B's $c$, $b_N$, $a_N$, $\varepsilon_N$, $I_n$, $R_K$.

Reference values of $\rho$. The analysts used $\rho=0.7459$ ($\rho^2=0.5563$, from the quoted
NeurIPS 2021 figures 22.7 % and 23.0 %). The repository's `calibrate.CENTRAL_TARGET` is the
decided-papers target, $\rho^2=0.5038$, $\rho=0.7098$, which the study uses as its central level. The checks below keep the analysts' $\rho=0.7459$ as a reference setting (row R3c).

---

## Summary of the final results

| item | result |
|---|---|
| 1 | $\rho^2=\sigma_q^2/(\sigma_q^2+\sigma_u^2+\sigma_\varepsilon^2/R)$. Two committees with $u$ redrawn: $r_{12}=\rho^2$. As $R\to\infty$, $\rho^2\to\sigma_q^2/(\sigma_q^2+\sigma_u^2)$. Spearman–Brown gives the shared-$u$ correlation, an upper bound on $\rho^2$. |
| 2 | $\mathrm{prec}_\infty(p)=P_2(z_p,z_p;\rho)/p$, free of $N$. At finite $N$, with $p_K=K/N$, $K=\mathrm{round}(pN)$: $\mathrm{prec}=H/p_K-(1-p_K)g(\rho-\varphi_I)/N+O(N^{-2})$. The relative deficit is $\kappa(p,\rho)/K$, with $\kappa(p,\rho)\to-\rho/(1+\rho)^2$ as $p\to0$; for $K<30$ use the exact integral, not the limit. The closed form's own relative error is $O(K^{-2})$ ($-1$ % at $K=3$), so use the exact integral for $K<10$. Swap fraction $=1-$ precision at $p=\alpha$. |
| 3 | $d(\alpha)=1-P_2(z_\alpha,z_\alpha;r_{12})/\alpha$; inconsistent share $=2\alpha d$; $d$ strictly decreases in $r_{12}$, so the inverse is unique; at $\alpha=\tfrac12$, $r_{12}=\cos(\pi d)$. |
| 4 | Exact 2-D integral at finite $N$. $\mathrm{prec}_{N,K}\to0$ for every $\rho<1$: $\mathrm{prec}_{N,K}=\frac{\varepsilon_NI_K^2}{K}\big[1+\frac{\beta_K}{b_N^2}+\omega_K\varepsilon_N+O(b_N^{-4})\big]$, that is $C_K\,N^{-\beta}(4\pi\log N)^{-\kappa}(1+O(\frac{\log\log N}{\log N}))$ with $C_K=\frac{(1+\rho)^2}{\tau K}\big[\frac{\Gamma(K+c)}{\Gamma(K)}\big]^2$. Practical form: $R_K\,P_2(z,z;\rho)/(K/N)$, $z=\bar\Phi^{-1}(K/N)$. The local slope over $10^3$–$10^6$ is 1.1 to 1.9 times the asymptotic slope $-\beta$. |
| 5 | The top scores sit near $b_N\approx\sqrt{2\log N}$. Their quality is $N(\rho b_N,\tau^2)$. The true top-$K$ bar also sits near $b_N$. The gap $(1-\rho)b_N$ grows; the spread $\tau$ does not. In SD units the gap is $\sqrt\beta\,b_N$, which gives $N^{-\beta}$. A fixed percentile keeps both bars at $z_p$. |
| 6 | For fixed $K$ and fixed $p$, the share of $\mathrm{Top}_K(Y)$ in the true top $p$ tends to 1. The miss rate is $\approx\bar\Phi(w_N)\Gamma(K+1+\gamma_N)/((1+\gamma_N)\Gamma(K+1))$, $w_N=(\rho b_N-z_p)/\tau$, of order $N^{-\rho^2/\tau^2}e^{(\rho z_p/\tau^2)\sqrt{2\log N}}$. The share in the true top $M$ ($M$ fixed) tends to 0 like $\varepsilon_NI_KI_M/K$. |
| 7 | Exact 2-D integral; the Poisson route differs by a relative $O(K/N)$. $P_{\rm best}=E\lvert\mathrm{Top}_K(Y)\cap\mathrm{Top}_1(X)\rvert$ exactly, so $P_{\rm best}\sim\varepsilon_N\Gamma(c)I_K[1+\beta_{K,1}/b_N^2+\omega_{K,1}\varepsilon_N]$, the same $N^{-\beta}$ rate; $P_{\rm best}(K=1)=\mathrm{prec}_{N,1}$. |
| 8 | $P(\text{winner rank}\le r)=P(\text{best}\in\mathrm{Top}_r(Y))$ exactly. Median $\approx N\bar\Phi(\rho b_N+\rho\gamma_E/a_N)\approx\frac{e^{-\gamma_E\rho^2}}{\rho}\big(\frac{N}{\sqrt{4\pi\log N}}\big)^{1-\rho^2}$. |
| 9 | $\mathrm{ovl}(N,K,\rho)=\mathrm{prec}(N,K,\rho^2)$ exactly; rate $N^{-(1-\rho^2)/(1+\rho^2)}$. |
| 10 | The tail dependence of (quality, score) decides. Gaussian/Gaussian: decay $N^{-\beta}$. Exponential/Gaussian: plateau below $\chi=2\bar\Phi(\sigma_n/2\sigma_q)$. $t_3$/Gaussian: rise to 1, deficit $\propto N^{-1/3}$. $t_3$/$t_3$: plateau $w=[1+(\sigma_\varepsilon/\sigma_q)^3/R^2]^{-1}$. Bounded/Gaussian and every heavier-noise case: decay to 0. Fixed-percentile precision is $N$-free for every shape. |
| 11 | Wrong accepts per paper $w(\alpha)=\alpha\,\mathrm{swap}(\alpha)$ satisfy $w(\alpha)=w(1-\alpha)$ and $w'(\alpha)=2\Phi(\sqrt\beta z_\alpha)-1$. So $w$ is concave and the swap fraction strictly decreases in $\alpha$. The same holds for the disagreement at $\rho^2$. |
| 12 | No closed form after snapping (lattice law, ties, bounded top). Fixed-percentile limits are 1-D integrals and stay $N$-free. Fixed $K$ at large $N$ becomes a lottery in the top tie class: $\mathrm{prec}\approx K/(N\pi_{\rm top})$. |
| 13 | Every exact formula agrees with closed forms, small-$N$ orthant probabilities, own Monte Carlo and the repository simulator (§13). The asymptotic law was re-derived and confirmed at $N$ up to $10^{300}$. No bug in `model.py`, `simulate.py`, `calibrate.py`. |

---

## R. Reconciliation of notes A and B

Each row is a point where the two notes differ. The last column gives the settlement and its evidence.

| # | item | notes A | notes B | settlement |
|---|---|---|---|---|
| R1 | all | $\kappa=\rho/(1+\rho)$, $\beta=(1-\rho)/(1+\rho)$, $B_N$, $F_K$ | $\kappa=(1-\rho)/(1+\rho)$, $c=1/(1+\rho)$, $b_N$, $R_K$ | Notation only. This document fixes one set (see Notation). $F_K=R_K$ identically. |
| R2 | 2 | Closed-form $O(1/N)$ correction $-(1-p_K)g(\rho-\varphi_I)/N$ | Deficit $\kappa_B(p,\rho)/K$ found numerically; only its $p\to0$ limit in closed form | Both right. A's formula is the $K\to\infty$ limit of B's numbers: closed-form $K(\mathrm{prec}/\mathrm{lim}-1)=-0.1259$ against B's $-0.1255$ at $K=200$ ($\rho=0.7459$, $p=0.25$); all 12 $(\rho,p)$ cells agree to 0.0007 at $K=200$. The closed form has a relative error $O(K^{-2})$: it overshoots the shift by 2–11 % at $K=10$, 0.4–2 % at $K=50$, under 0.5 % at $K=200$ (§2.3). Both give the same $p\to0$ limit $-\rho/(1+\rho)^2$. |
| R3a | 3 | Finite-$N$ inversion at $N=882$: $r_{12}$ moves 0.5563 → 0.5571 | not computed | The pure finite-$N$ shift is $+0.00046$ (0.5563 → 0.5568), by root search on the exact law and by $\delta r=\alpha\,\delta d/\phi_2$. A's 0.5571 also contains the rounding $\alpha=0.227$ against $200/882$ (target $d=0.50705$ gives 0.5570). Both effects are far below the sampling error. |
| R3b | 3 | — | — | Both use average acceptance counts (43.5/166; 200.5/764). Solving with the two committees' own counts moves $r_{12}$ by $+0.0001$ (2014), $+0.0007$ (2021). Negligible. |
| R3c | 3 | — | — | Both notes calibrate to $\rho^2=0.5563$ (882 papers, quoted). `calibrate.CENTRAL_TARGET` is the decided-papers target $\rho^2=0.5038$. Not a derivation error. Resolved: the study uses 0.5038 as central (REPORT.md section 8.2); 0.5563 stays here as the notes' reference setting. |
| R4a | 4 | Prefactor $C_K^{A}$ multiplies $e^{\kappa B_N^2}/N$ or $N^{-\beta}(4\pi\log N)^{-\kappa}$ | $C_K^{B}$ multiplies $(\log N)^{-\kappa}N^{-\beta}$ | Same law: $C_K^B=(4\pi)^{-\kappa}C_K^A$ (e.g. $2.1173\times(4\pi)^{-1/3}=0.9107$ at $\rho=0.5$, $K=1$). The exact value divided by either form tends to 1 (0.9964 at $N=10^{300}$, $\rho=0.7459$, $K=1$). This document and the docstring of `precision_fixed_K_asymptotic` both use $C_K=C_K^A$, which multiplies $N^{-\beta}(4\pi\log N)^{-\kappa}$; the code's `form="logN"` value equals $C_K N^{-\beta}(4\pi\log N)^{-\kappa}$ to $4\times10^{-15}$. |
| R4b | 4 | Next correction $-\rho\sigma_K^2/(\tau^2B_\ast^2)$ about a re-centred level $B_\ast$ ($K=1$: $-2.04$, $-6.60$, $-21.43$ at $\rho$ = 0.5, 0.7459, 0.9) | $\beta_K/b_N^2$ about $b_N$ ($K=1$: $-2.92$, $-8.01$, $-23.17$) | Both right; they expand about different levels. Expanding A's form about $b_N$ gives exactly $\beta_K=2\kappa D_K-\rho\sigma_K^2/\tau^2$ (algebra in §4.4; numerically equal to $10^{-15}$). Fits of the exact value at $N=10^{100}$–$10^{300}$ return both coefficients to 3–4 digits (§4.4). |
| R4c | 4 | Joint-exceedance term $\Delta$ | $\omega_K\varepsilon_N$ | Same term: $\Delta/\text{lead}=\omega_K\varepsilon_N(1+O(b_N^{-2}))$ with $\omega_K=[\Gamma(K+\beta)/\Gamma(K+c)]^2$. |
| R4d | 4 | Local slope $\approx-\beta-2\kappa(1-B_\ast R(B_\ast))$ | $-\beta-2\kappa(1-b_N/a_N)-2\beta_K/b_N^4$ | Same leading term with different reference points. The exact slopes (§4.6) settle the size: secant/asymptote 1.11–1.90 over the requested grid. Both notes' tables are reproduced. |
| R4e | 4 | "corrections $O(1/\log N)$" | "first correction $O(\log\log N/\log N)$" | Both right: the $b_N$ form has a $1/b_N^2$ correction; the pure $\log N$ form adds $\kappa\log(4\pi\log N)/(2\log N)$. |
| R5 | 5 | Gap $(E X_{(10)}-\rho EY_{(1)})/\tau$ | Shortfalls $(1-\rho)EY_{(i)}/\tau$ | Same mechanism; different summary numbers. Both reproduced (§5). |
| R6 | 6 | Miss rate as a sum of $\bar\Phi((\rho EY_{(i)}-z_p)/\tau)$; exponent $N^{-\rho^2/\tau^2}e^{(\rho z_p/\tau^2)B_N}$ | Explicit asymptotic miss rate with $\Gamma(K+1+\gamma_N)$ | Same exponent. B's explicit form is accurate to 1–3 % at $K=1$ once the miss is small ($N\ge10^6$ at $\rho=0.7459$, $N\ge10^8$ at $\rho=0.5$); at $K=10$ it is 4–10 % low there and approaches slowly (2–3 % at $N=10^{20}$) (§6). |
| R7 | 7 | $\Gamma(1-\kappa)(1+\rho)\Gamma(K+1-\kappa)/(\tau\Gamma(K))\cdot e^{\kappa B^2}/N$ | $\varepsilon_N\Gamma(c)I_K$ | Identical ($1-\kappa=c$). Poisson-route error $5.5\times10^{-4}$ at $N=10^3$ in both; reproduced. |
| R8a | 8 | Direct formula for the winner-rank cdf | Exchangeability identity $P(W\le r)=P(\text{best}\in\mathrm{Top}_r)$ | Equivalent. The code uses the identity; Monte Carlo confirms it (§8). |
| R8b | 8 | Median power form with $(N/(\sqrt{2\pi}B_N))^{1-\rho^2}$ | Power form with $(N/\sqrt{4\pi\log N})^{1-\rho^2}$ | Asymptotically equal ($2\pi b_N^2\sim4\pi\log N$). In range they are 2–25 % off (worst at $\rho=0.5$, $N=10^3$, and at $\rho=0.9$); the semi-asymptotic $N\bar\Phi(\rho b_N+\rho\gamma_E/a_N)$ is within 1–7 % for $\rho\le0.75$ (§8). |
| R8c | 8 | SD of log rank $\sqrt{\rho^2\tau^2B_N^2+\pi^2\rho^4/6}$ | $\rho\tau b_N$ | A's form is closer, but both understate the spread: exact $W_{75}/W_{25}=35.8$ at $N=10^6$, $\rho=0.7459$, against 27.9 (A) and 24.2 (B). Use the exact cdf. |
| R9 | 9 | Formula identical | Formula identical; open item: simulated overlap low at $N=10^6$ (pooled $-7.7$ % at $K=10$, $\rho=0.7459$) | 48,000 fresh repository conferences at $N=10^6$ (§13.2): $\rho=0.7459$ gives $-2.1\pm1.5$ % ($z=-1.35$) at $K=10$; $\rho=0.5$ gives $+1.1\pm8$ %. A $-7.7$ % deficit is excluded at $3.7\sigma$. |
| R10 | 10 | Setting $\rho^2=0.5$, $\sigma_n=\sigma_q$; no lognormal | Setting $\rho^2=0.5563$, $R=3$; lognormal included | Different settings, same formulas. Both sets of limits are reproduced (§10): plateaus 0.5387…0.6157 ($\chi=0.6171$) and 0.5787…0.6538 ($\chi=0.6552$); $w=0.6340$ and $0.7086$. |
| R11 | 11 | Proof of monotonicity via $w'(\alpha)$ | Numerical monotonicity and a small-noise argument | Both right; A's derivative is checked to $10^{-10}$ (§11). |
| R12 | 12 | $\pi_{\rm top}$ = 1.2e-4, 3.5e-4, 4.5e-4 | $\pi_{\rm top}$ = 1.07e-4, 3.07e-4, 3.71e-4 | Different $\sigma_\varepsilon$ (one value for all scales in A; per-scale calibration in B). No conflict. |
| R13 | 13 | `analytic.P2` loses relative accuracy deep in the tail | same | Confirmed, and worse for unequal thresholds: `P2(11, 3, 0.7)` returns $-1.4\times10^{-18}$ (true $1.9\times10^{-28}$). The absolute error is about $10^{-16}\bar\Phi(\min(a,b))$. It is harmless in the study range (thresholds $\le4.8$). New code uses `log_P2`. |

---

## 1. Reliability (item 1)

**Derivation.** The mean score of paper $i$ is $\bar s_i=q_i+u_i+\bar\varepsilon_i$, with
$\bar\varepsilon_i=R^{-1}\sum_j\varepsilon_{ij}$. The three terms are independent. So
$\mathrm{Var}(\bar s)=\sigma_q^2+\sigma_u^2+\sigma_\varepsilon^2/R$ and $\mathrm{Cov}(q,\bar s)=\sigma_q^2$. Hence

$$\rho^2=\mathrm{corr}(q,\bar s)^2=\frac{\sigma_q^2}{\sigma_q^2+\sigma_u^2+\sigma_\varepsilon^2/R}.$$

Two committees score the same paper: $\bar s^{(k)}=q+u^{(k)}+\bar\varepsilon^{(k)}$. If $u$ is redrawn,
$\mathrm{Cov}(\bar s^{(1)},\bar s^{(2)})=\sigma_q^2$ and $r_{12}=\rho^2$. If $u$ is shared,
$r_{12}=(\sigma_q^2+\sigma_u^2)/(\sigma_q^2+\sigma_u^2+\sigma_\varepsilon^2/R)>\rho^2$. As $R\to\infty$,
$\rho^2\to\sigma_q^2/(\sigma_q^2+\sigma_u^2)<1$ when $\sigma_u>0$.

Two reviews of one paper share $q$ and $u$, so they correlate at
$r_1=(\sigma_q^2+\sigma_u^2)/(\sigma_q^2+\sigma_u^2+\sigma_\varepsilon^2)$. Spearman–Brown gives
$Rr_1/(1+(R-1)r_1)=(\sigma_q^2+\sigma_u^2)/(\sigma_q^2+\sigma_u^2+\sigma_\varepsilon^2/R)$. This is the
shared-$u$ committee correlation. It treats $u$ as signal, so it is an upper bound on $\rho^2$.

**Which metrics depend on $\rho$ alone.** With continuous Gaussian scores and $u$ redrawn,
$(X,Y_1,Y_2)$ is trivariate normal with correlations $(\rho,\rho,\rho^2)$. Every metric of handoff §4
is a function of the ranks of these vectors (the mean percentile uses $\Phi(X)$, also a rank
function). So these metrics depend on $(\sigma_q,\sigma_\varepsilon,R,\sigma_u)$ only through $\rho$.
The exceptions: a shared $u$ (then $r_{12}$ is a second parameter); $t_3$ noise (the mean of $R$ $t_3$
errors has an $R$-dependent shape, §10); snapped scores (§12); non-Gaussian quality (a different
function of $\rho$ for each shape).

**Checks.** `rho2(1.5, 3)` $=0.6575$; `rho2(2, 4, sigma_u=0.5)` $=0.5353$; the shared-$u$ correlation
and Spearman–Brown both give $0.6283$ there; `rho2_limit(1.2, 0.5)` $=0.8521$. Notes A checked
these against 400,000-paper simulations (e.g. 0.5353 against 0.5342; shared-$u$ 0.6283 against
0.6295). The simulator's `corr_qs` and `corr_s12` agree with $\rho$ and $\rho^2$ in §13.

---

## 2. Fixed-percentile precision (item 2)

### 2.1 Large-$N$ limit

Let $K=\mathrm{round}(pN)$. The $K$-th largest score and the $K$-th largest quality both converge in
probability to $z_p$ (quantile consistency). So the average of
$1\{Y_i\ge Y_{(K)}\}1\{X_i\ge X_{(K)}\}$ has the same limit as the average of $1\{Y_i>z_p,X_i>z_p\}$,
which is $P_2(z_p,z_p;\rho)$. Divide by $p$:

$$\mathrm{prec}_\infty(p)=\frac{P_2(z_p,z_p;\rho)}{p}=P(X>z_p\mid Y>z_p),\qquad
\mathrm{swap}(\alpha)=1-\frac{P_2(z_\alpha,z_\alpha;\rho)}{\alpha}.$$

With a fixed quota the count of undeserving accepts equals the count of deserving rejects, so the
swap fraction is also the share of deserving papers that are rejected. On the diagonal,
$P_2(a,a;\rho)=\bar\Phi(a)-2T(a,\sqrt\beta)$ with Owen's $T$ (`analytic.P2_diag`).

This difference cancels when $P_2\ll\bar\Phi(a)$ (tiny $p$, small or negative $\rho$): its relative error is
about $3\times10^{-14}\,\bar\Phi(a)/P_2$. So `P2_diag` uses `log_P2` once $P_2<10^{-3}\bar\Phi(a)$, and
`precision_pct` works in log space. Before this switch, `precision_pct` at $\rho=0.3$ had a relative error of
$-7\times10^{-6}$ at $p=10^{-16}$, $-1.1\times10^{-3}$ at $10^{-20}$ and $+5.7$ at $10^{-30}$; at $10^{-100}$ it was
negative, and at $10^{-300}$ it was 0. Now it agrees with $\exp(\log P_2-\log p)$ to $3\times10^{-13}$ for $p$ from
$10^{-3}$ to $10^{-300}$ and $\rho$ = 0.3, 0.7, 0.9. In the study range ($p\ge10^{-3}$) the values do not change.
$p=0$ gives the limit 0 (1 at $\rho=1$).

### 2.2 Exact finite $N$

The integral of §4.1 with $M=K=\mathrm{round}(pN)$ is exact. It depends on $N$ only through $K$ and
$p_K=K/N$.

### 2.3 Closed-form $O(1/N)$ correction

Write $U=\bar\Phi(X)$, $V=\bar\Phi(Y)$ (uniform) and $H(u,v)=P(U\le u,V\le v)=P_2(\bar\Phi^{-1}(u),\bar\Phi^{-1}(v);\rho)$.
By §4.1, $\mathrm{prec}_{N,K}=(N/K)\,E\,H(\hat U,\hat V)$, where $\hat U$, $\hat V$ are the $K$-th smallest
$U$ and $V$ among the other $n=N-1$ papers. Facts about these order statistics:

* $E\hat U=K/(n+1)=p_K$ exactly.
* $\mathrm{Var}\,\hat U=p_K(1-p_K)/N+O(N^{-2})$ and, by the Bahadur representation,
  $\mathrm{Cov}(\hat U,\hat V)=(H(p_K,p_K)-p_K^2)/N+O(N^{-2})$.

Expand $H$ to second order about $(p_K,p_K)$. The first-order terms vanish because $E\hat U=p_K$.
By symmetry $H_{uu}=H_{vv}$, so

$$E\,H(\hat U,\hat V)=H+H_{uu}\mathrm{Var}\,\hat U+H_{uv}\mathrm{Cov}(\hat U,\hat V)+O(N^{-2}).$$

The derivatives follow from $H_u(u,v)=P(V\le v\mid U=u)=\bar\Phi((y-\rho x)/\tau)$ and $dx/du=-1/\phi(x)$:
$H_{uu}=-(\rho/\tau)\phi((y-\rho x)/\tau)/\phi(x)$, and $H_{uv}$ is the copula density
$\phi_2(x,y)/(\phi(x)\phi(y))$. At $x=y=z=z_{p_K}$, since $(1-\rho)z/\tau=\sqrt\beta z$,
$H_{uu}=-\rho g$ and $H_{uv}=g$ with $g=\phi(\sqrt\beta z)/(\tau\phi(z))=e^{\kappa z^2}/\tau$. Multiply by $N/K=1/p_K$:

$$\boxed{\mathrm{prec}_{N,K}=\frac{H(p_K,p_K)}{p_K}-\frac{(1-p_K)\,g\,(\rho-\varphi_I)}{N}+O(N^{-2}),\qquad
\varphi_I=\frac{H-p_K^2}{p_K(1-p_K)}.}$$

$\varphi_I$ is the correlation of the two selection indicators, and $\varphi_I<\rho$, so the
correction is negative. In relative terms the deficit is $\kappa(p,\rho)/K$ with

$$\kappa(p,\rho)=-\frac{p^2(1-p)\,g\,(\rho-\varphi_I)}{H(p,p)}\ \xrightarrow{p\to0}\ -\frac{\rho}{(1+\rho)^2}.$$

(For the limit: $H\approx\phi_2(z,z)(1+\rho)^2/z^2$ and $p\approx\phi(z)/z$ give $gp/H\to1/(p(1+\rho)^2)$, and
$\varphi_I\to0$.) The $p\to0$ limit equals the large-$K$ expansion of $R_K$ (§4.5), found by a
different route. `analytic.precision_pct_finite` implements the boxed formula.

**Answer to item 2.** The limit has no $N$. The expected precision at finite $N$ depends on $N$
through $K=\mathrm{round}(pN)$ only: a deficit of relative size $\kappa(p,\rho)/K$, between
$-0.25/K$ and $-0.08/K$ for $p\le25$ %. Rounding moves $p$ to $p_K$ by at most $1/(2N)$; use $p_K$
in the formula. The swap fraction has the same correction with the opposite sign.

**Using the $N$-free limit.** The limit overstates the precision of a small top-$K$ set. At $N=10^3$ it exceeds
the exact value by 6–8 % at $K=3$, 4 % at $K=5$, 2 % at $K=10$ and 0.6 % at $K=30$ ($\rho^2$ from 0.3 to 0.85;
the table under "Small $K$" below). The simulator resolves this: at $N=10^3$, $p=0.3$ % ($K=3$), $\rho^2=0.85$ it
gives $0.5091\pm0.0025$ against the limit 0.5395 ($z=-12.1$) and the exact value 0.5075 ($z=+0.64$)
(`results/verify_analytic.csv`; the `limit` rows there have RMS $z$ 4.27 at $N=10^3$, 1.64 at $10^4$, 0.92 at $10^5$ and 0.96 at $10^6$).
So wherever $K=\mathrm{round}(pN)<30$, report `precision_fixed_K(N, K, rho)`, not `precision_pct`, and wherever
fixed-percentile precision is called $N$-free, state the relative deficit $\approx-\rho/((1+\rho)^2K)$. The same holds
for the swap fraction and the disagreement. The docstrings of `precision_pct`, `swap_fraction` and
`disagreement` say this.

**Checks** (`precision_fixed_K` against `precision_pct` and `precision_pct_finite`):

| $\rho$ | $p$ | $K$ | $N$ | exact | $N$-free limit | closed form | closed shift / exact shift | $K(\text{exact}/\text{lim}-1)$ | $\kappa(p,\rho)$ closed |
|---|---|---|---|---|---|---|---|---|---|
| 0.5 | 0.01 | 10 | 1000 | 0.126819 | 0.129392 | 0.126758 | 1.024 | −0.1988 | −0.2036 |
| 0.5 | 0.01 | 200 | 20000 | 0.129261 | 0.129392 | 0.129261 | 1.001 | −0.2033 | −0.2036 |
| 0.7459 | 0.003 | 10 | 3333 | 0.241765 | 0.247284 | 0.241622 | 1.026 | −0.2232 | −0.2290 |
| 0.7459 | 0.01 | 10 | 1000 | 0.306199 | 0.312619 | 0.306013 | 1.029 | −0.2054 | −0.2113 |
| 0.7459 | 0.01 | 50 | 5000 | 0.311305 | 0.312619 | 0.311298 | 1.006 | −0.2101 | −0.2113 |
| 0.7459 | 0.01 | 200 | 20000 | 0.312289 | 0.312619 | 0.312289 | 1.001 | −0.2110 | −0.2113 |
| 0.7459 | 0.05 | 10 | 200 | 0.428605 | 0.436013 | 0.428319 | 1.039 | −0.1699 | −0.1764 |
| 0.7459 | 0.25 | 10 | 40 | 0.626831 | 0.634264 | 0.626279 | 1.074 | −0.1172 | −0.1259 |
| 0.7459 | 0.25 | 200 | 800 | 0.633866 | 0.634264 | 0.633865 | 1.003 | −0.1255 | −0.1259 |
| 0.9 | 0.01 | 10 | 1000 | 0.531722 | 0.541971 | 0.531278 | 1.043 | −0.1891 | −0.1973 |
| 0.9 | 0.25 | 10 | 40 | 0.762377 | 0.772182 | 0.761310 | 1.109 | −0.1270 | −0.1408 |
| 0.9 | 0.25 | 200 | 800 | 0.771641 | 0.772182 | 0.771639 | 1.005 | −0.1401 | −0.1408 |

The closed form captures the finite-$N$ shift to within 2–11 % at $K=10$ and 0.1–0.5 % at $K=200$; its
own error is $O(K^{-2})$ relative. Swap at $\rho=0.9$, $N=1000$, $\alpha=0.1$: exact 0.312449, closed
form 0.312456, $N$-free 0.311351. The repository simulator resolves this shift: notes A measured
$0.31240\pm0.00036$ ($-0.1$ SE from exact, $+2.9$ SE from the $N$-free value), and notes B's
$10^5$-conference runs gave RMS $z=1.05$ against the exact values and 4.5 against the $N$-free
values. §13 adds fresh runs. At $p=10^{-7}$ ($N=10^8$, $K=10$) the closed form agrees with the exact
integral to $6\times10^{-4}$ relative for $\rho\in\{0.3,0.7459,0.9\}$.

**Small $K$.** The remainder is $O(N^{-2})$ at fixed $p$, but its constant is of order $1/p^2$, so the closed
form's own relative error is $O(K^{-2})$. It is negative. Closed form / exact − 1 at $N=10^3$:

| $\rho^2$ | $K=3$ | $K=5$ | $K=10$ | $K=30$ | $K=50$ |
|---|---|---|---|---|---|
| 0.3 | −0.59 % | −0.21 % | −0.050 % | −0.0055 % | −0.0020 % |
| 0.56 | −0.69 % | −0.24 % | −0.061 % | −0.0071 % | −0.0026 % |
| 0.85 | −0.98 % | −0.36 % | −0.091 % | −0.011 % | −0.0043 % |

At $K=3$, $\rho^2=0.85$ (closed form 0.502555, exact 0.507533) the error is detectable by simulation: the run in
`results/verify_analytic.csv` gives $z=+2.62$ against the closed form and $+0.64$ against the exact value, and three
independent runs of 10,000 conferences pooled give $z=+4.48$ against the closed form and $+1.05$ against the exact
value. For $K<10$ use the exact integral; the docstring of `precision_pct_finite` states this limit.

---

## 3. Two-committee disagreement (item 3)

**Derivation.** The two committees' scores of one paper are standard bivariate normal with
correlation $r_{12}$ ($=\rho^2$ with $u$ redrawn). Each committee accepts $A=\alpha N$ papers. This is §2
with $\rho\to r_{12}$:

$$d(\alpha,r_{12})=P(\mathrm{rej}_2\mid\mathrm{acc}_1)=1-\frac{P_2(z_\alpha,z_\alpha;r_{12})}{\alpha},\qquad
I(\alpha,r_{12})=\frac{2(A-\text{both})}{N}=2\big(\alpha-P_2(z_\alpha,z_\alpha;r_{12})\big)=2\alpha\,d.$$

**Inverse map.** Plackett's identity $\partial P_2(a,b;r)/\partial r=\phi_2(a,b;r)>0$ gives
$\partial d/\partial r_{12}=-\phi_2(z_\alpha,z_\alpha;r_{12})/\alpha<0$. So $d$ is strictly decreasing and the
inverse is unique (a bracketing root search on $(-1,1)$). Then $\rho^2=r_{12}$ and
$\sigma_\varepsilon=\sqrt{R(\sigma_q^2/\rho^2-\sigma_q^2-\sigma_u^2)}$. Error propagation:
$\delta r_{12}=-\alpha\,\delta d/\phi_2(z_\alpha,z_\alpha;r_{12})$.

**Closed form at $\alpha=1/2$.** $P_2(0,0;r)=\tfrac14+\arcsin(r)/(2\pi)$ (Sheppard), so
$d=\tfrac12-\arcsin(r_{12})/\pi$ and $r_{12}=\cos(\pi d)$. Random decisions ($r_{12}=0$) give
$d=1-\alpha$ and $I=2\alpha(1-\alpha)$.

**Finite $N$.** The exact disagreement is $1-E\lvert\mathrm{Top}_A(Y_1)\cap\mathrm{Top}_A(Y_2)\rvert/A$, the
§4.1 integral at correlation $r_{12}$. Its $O(1/N)$ shift is §2.3 with $\rho\to r_{12}$.

**Checks.** At $\alpha=1/2$ the closed form matches `disagreement` to $10^{-16}$ for
$r_{12}\in\{0.2,0.5,0.8\}$, and $\cos(\pi d)$ returns $r_{12}$. The inversions ($N$-free law; the first four rows are
`calibrate.EXPERIMENTS`, the last row is the pair of figures quoted in the notes):

| experiment | $\alpha$ | inconsistent share | $d$ | $r_{12}=\rho^2$ | $\rho$ |
|---|---|---|---|---|---|
| NeurIPS 2014, raw table | 0.2620 | 0.2590 | 0.4943 | 0.5265 | 0.7256 |
| NeurIPS 2014, quoted | 0.2250 | 0.2590 | 0.5756 | 0.4362 | 0.6604 |
| NeurIPS 2021, decided papers (`CENTRAL_TARGET`) | 0.2624 | 0.2657 | 0.5062 | 0.5038 | 0.7098 |
| NeurIPS 2021, all 882 | 0.2273 | 0.2302 | 0.5062 | 0.5571 | 0.7464 |
| NeurIPS 2021, quoted (0.227, 23.0 %) | 0.2270 | 0.2302 | 0.5070 | 0.5562 | 0.7458 |

Finite-$N$ bias of the inversion (root search on the exact law at the experiment's $N$ and $A$):

| $N$ | $A$ | $r_{12}$ | exact $d$ | $N$-free $d$ | shift | $r_{12}$ from the exact law |
|---|---|---|---|---|---|---|
| 166 | 44 | 0.5265 | 0.49293 | 0.49177 | +0.00115 | 0.5286 |
| 764 | 200 | 0.5038 | 0.50703 | 0.50679 | +0.00024 | 0.5043 |
| 882 | 200 | 0.5563 | 0.50745 | 0.50718 | +0.00027 | 0.5568 |

The linear propagation $\alpha\,\delta d/\phi_2$ gives $+0.00046$ at $N=882$, as the root search does.
These shifts and the unequal-count effect (R3b) are far below the binomial sampling error of the
experiments. `analytic.disagreement`, `inconsistent_share`, `invert_disagreement` and
`invert_inconsistent` are correct.

---

## 4. Fixed-number precision (item 4)

### 4.1 Exact finite-$N$ formula

Let $M$ be the size of the true set ($M=K$ for precision; $M=2K$, $10K$, $\mathrm{round}(0.01N)$ for the
containment metrics of §6). §9 runs the same integral on two reviews' scores. There $M$ is the size of an
"or Better" set, for example $M_{\rm oob}$, the size of Oral or Better (NeurIPS's Oral count, which includes its
Best Papers; series `oral_or_better` in `results/tier_sizes.csv`, column `M_oral_or_better` in
`results/tier_scaling.csv`). By exchangeability,

$$E\lvert\mathrm{Top}_K(Y)\cap\mathrm{Top}_M(X)\rvert=N\,P(\text{paper 1 has score rank}\le K\text{ and quality rank}\le M).$$

Condition on paper 1's pair $(x,y)$. The other $n=N-1$ papers are iid. Let $a$ be the number of them
with a higher score: $a\sim\mathrm{Bin}(n,\bar\Phi(y))$. Given $a$, those $a$ papers are iid from the law of
$(X,Y)$ given $Y>y$, so each has higher quality with probability $\pi_1=P_2(x,y)/\bar\Phi(y)$. The other
$n-a$ papers have higher quality with probability $\pi_0=(\bar\Phi(x)-P_2(x,y))/\Phi(y)$. The two
counts are independent. Therefore, exactly,

$$\boxed{E\lvert\mathrm{Top}_K(Y)\cap\mathrm{Top}_M(X)\rvert=N\!\iint\!\phi_2(x,y;\rho)\sum_{a=0}^{K-1}\mathrm{Bin}(a;n,\bar\Phi(y))\!\!\sum_{j=0}^{\min(a,M-1)}\!\!\mathrm{Bin}(j;a,\pi_1)\,F_{\rm Bin}(M-1-j;\,n-a,\,\pi_0)\,dx\,dy,}$$

and $\mathrm{prec}_{N,K}$ is this with $M=K$, divided by $K$. Notes A write the same quantity as
$(N/K)E[P_2(T_X,T_Y)]$, with $T_X$, $T_Y$ the $K$-th largest quality and score among the other papers;
summing the concomitant terms $P(X_{[i]}\ge X_{(K)})$, $i\le K$, gives it too. The three forms are
the same integral.

**Evaluation** (`_count_topK_topM`). The substitution $u=\bar\Phi(x)$, $v=\bar\Phi(y)$ turns $\phi_2\,dx\,dy$
into $c(u,v)\,du\,dv$ with the Gaussian copula density
$\log c=-\log\tau+\kappa(x^2+y^2)/2-\rho(x-y)^2/(2\tau^2)$. The integrand switches on where $nu$ and $nv$
fall below $M$ and $K$. The quadrature uses composite Gauss–Legendre panels in $t=\log(nu)$:
breakpoints at the counts $M+k\sqrt M$, transition panels at most 0.6 wide, and 55 e-folds of tail.
For $u>1/2$ it switches to panels in $x$. The orthant cells $P_2$, $\bar\Phi(x)-P_2$, $\bar\Phi(y)-P_2$ come
from `log_P2`, which is accurate in relative terms far in the tail: it integrates the conditional
tail of the larger threshold, $P_2=\frac{\phi(h)}h\int_0^\infty e^{-w-w^2/2h^2}\bar\Phi\big(\frac{k-\rho(h+w/h)}{\tau}\big)dw$,
and uses Owen's $T$ only when both thresholds are below 3. Binomial pmfs use
$\log\binom ni=\sum_{l<i}\log(n-l)-\log i!$, stable for $n$ up to $10^{300}$. The inner sums use
exact recursions in $a$ (no exponentials in the loop); for $M>3000$ the quality cdf uses the
regularised incomplete beta function.

**$\rho$ near $\pm1$.** The copula density is a ridge of width $\tau$ along $x=\rho y$. The panels of the product
grid follow the binomial windows, not $\tau$. So for $|\rho|$ near 1 the old code returned values above 1 and raised
no error: `precision_fixed_K(1000, 10, ρ)` was 1.0838, 2.594 and 8.136 at $\rho$ = 0.9999, 0.99999, 0.999999, and NaN
at $\rho=1$; at $N=2$ its error was $5\times10^{-5}$ at $\rho=0.99$ and $3.6\times10^{-3}$ at 0.995. For $|\rho|>0.95$ the
code now integrates the inner variable in the rotated coordinate $w=(x-\rho y)/\tau$, with
$\phi_2\,dx\,dy=dv\,\phi(w)\,dw$: unit panels in $w$ on $[-12,12]$, plus the quality-axis breakpoints mapped into
$w$, so that the quality-count switch stays resolved (`_grid_blocks`). For $|\rho|\le0.95$ the product grid is kept,
so no value in the study range changes. At $|\rho|=1$ the code returns the closed values: $\min(K,M)$ at $\rho=1$ and
$\max(0,K+M-N)$ at $\rho=-1$; $P_{\rm best}$ is 1 at $\rho=1$ and 0 at $\rho=-1$ ($K<N$). `log_P2` refines its panels
where the integrand has a step narrower than its panels (width $h\tau/|\rho|$, at $|\rho|$ near 1) or a fast decay
(strongly negative $\rho$), and it uses the tail integral instead of Owen's $T$ when $\rho<0$ and $P_2<10^{-7}$.

**Checks of the exact formula.**

* $N=2$, $K=1$: $\mathrm{prec}=\tfrac12+\arcsin(\rho)/\pi$; agreement to $10^{-13}$.
* $N=3$: $\mathrm{prec}_1=3P(X_1>X_{2,3},Y_1>Y_{2,3})$, a 4-D orthant (Genz): agreement to $10^{-9}$. The
  identity $\mathrm{prec}_2(3)=(1+\mathrm{prec}_1(3))/2$ holds to $10^{-10}$.
* $\rho=0$: the exact answer is $KM/N$; agreement to $10^{-9}$ for $(N,K,M)$ from $(10,3,3)$ to $(10^{50},3,3)$.
* Own Monte Carlo at $N\le50$: 59 comparisons, RMS $z=0.97$, largest $|z|=2.58$.
* Grid refinement: changes below $4\times10^{-11}$.
* $\rho$ near 1 (ridge grid). For $\rho$ from 0.951 to 0.999999 (and $-0.96$, $-0.999$): the $N=2$ closed form holds to
  $10^{-13}$ for precision and $P_{\rm best}$, and the $N=3$ identity to $10^{-14}$. 8 against 16 nodes: changes below
  $1.4\times10^{-12}$ for $\rho$ from 0.96 to 0.999999, $N$ from 2 to $10^{300}$, $(K,M)$ = (1,1), (10,10), (10,100), (30,30),
  $(5,0.25N)$. Where both grids apply ($\rho$ = 0.9, 0.95) the two agree to $3\times10^{-11}$, the product grid's own error
  there. Precision and $P_{\rm best}$ increase with $\rho$ and stay at most 1 (to $10^{-14}$): `precision_fixed_K(1000, 10, ρ)` = 0.8373,
  0.9426, 0.9802, 0.9935, 0.9979 at $\rho$ = 0.99, 0.999, 0.9999, 0.99999, 0.999999. Own Monte Carlo: $\rho=0.999$, $N=30$,
  $K=3$ (200,000 conferences), $z=-0.80$ (precision) and $+1.13$ ($P_{\rm best}$); $\rho=0.99$, $N=200$, $K=5$ (50,000),
  $z=+0.93$ and $+1.12$; $\rho=0.9999$, $N=100$, $K=10$ (50,000), $z=-1.37$ (precision).
  `scripts/make_R_needed.py` brackets its root search up to $\rho=0.9999$; every root is below $\rho=0.89$, in the
  unchanged product-grid range. A rerun gives the roots of `results/analytic_R_needed.csv` within the search tolerance
  ($\rho^2$ to $5\times10^{-7}$, $R$ to $2\times10^{-5}$); only the path of the root search changed.
* Every tabulated exact value in notes A and notes B is reproduced to their rounding ($10^{-5}$).
* The repository simulator: §13.

### 4.2 The point-process limit

Fix $K$ and $M$ and let $N\to\infty$. Put $x=b_N+\xi/a_N$, $y=b_N+\eta/a_N$.

*Margins.* With the hazard $h=\phi/\bar\Phi$, $h(b_N)=a_N$ and $h'=h(h-b)$:
$N\bar\Phi(b_N+\xi/a_N)=e^{-\xi}\big(1-\xi^2/(2b_N^2)+O(b_N^{-4})\big)$. So the top qualities form a Poisson
process with intensity $e^{-\xi}d\xi$; the same holds for the scores.

*Joint intensity (exact).* Expand the exponent:
$x^2-2\rho xy+y^2=2(1-\rho)b^2+2(1-\rho)\frac ba(\xi+\eta)+(\xi^2-2\rho\xi\eta+\eta^2)/a^2$. Divide by
$2\tau^2$ and use $dx\,dy=d\xi\,d\eta/a^2$ and $a_N^2=N^2e^{-b_N^2}/(2\pi)$:

$$N\phi_2(x,y)\,dx\,dy=\varepsilon_N\,e^{-c\frac{b_N}{a_N}(\xi+\eta)}\,e^{-\frac{\xi^2-2\rho\xi\eta+\eta^2}{2\tau^2a_N^2}}\,d\xi\,d\eta,\qquad\varepsilon_N=\frac{e^{\kappa b_N^2}}{N\tau}.$$

Since $e^{b_N^2/2}\approx N/(\sqrt{2\pi}b_N)$, $\varepsilon_N\approx N^{-\beta}(2\pi b_N^2)^{-\kappa}/\tau\to0$. Only a
vanishing number of papers are extreme in both coordinates: the bivariate normal is tail
independent, with Ledford–Tawn coefficient $\eta_{LT}=(1+\rho)/2$ and $\beta=1/\eta_{LT}-1$.

*Counting.* A paper at $(\xi,\eta)$ is in $\mathrm{Top}_M(X)$ if fewer than $M$ other papers lie above
$\xi$ (a Poisson($e^{-\xi}$) count), and in $\mathrm{Top}_K(Y)$ if fewer than $K$ lie above $\eta$. The two
counts share only the papers above in both coordinates, whose mean is $O(\varepsilon_N)$. To leading
order they are independent:

$$E\lvert\mathrm{Top}_K(Y)\cap\mathrm{Top}_M(X)\rvert\simeq\varepsilon_N\iint e^{-c(\xi+\eta)}F_M(e^{-\xi})F_K(e^{-\eta})\,d\xi\,d\eta.$$

*The integral.* With $\lambda=e^{-\xi}$ and $F_n(\lambda)=P(G_n>\lambda)$, $G_n\sim\mathrm{Gamma}(n,1)$:
$\int e^{-c\xi}F_n(e^{-\xi})d\xi=\int_0^\infty\lambda^{c-1}P(G_n>\lambda)d\lambda=E[G_n^c]/c=I_n$.

### 4.3 The leading law, with its prefactor

$$\boxed{E\lvert\mathrm{Top}_K(Y)\cap\mathrm{Top}_M(X)\rvert\sim\varepsilon_NI_KI_M,\qquad
\mathrm{prec}_{N,K}\sim\frac{\varepsilon_NI_K^2}{K}=\frac{(1+\rho)^2}{\tau K}\Big[\frac{\Gamma(K+c)}{\Gamma(K)}\Big]^2\frac{e^{\kappa b_N^2}}{N}.}$$

From $N\bar\Phi(b_N)=1$: $b_N^2=2L-\log(4\pi L)+(\log(4\pi L)-2)/(2L)+\dots$ with $L=\log N$. Hence
$e^{\kappa b_N^2}/N=N^{-\beta}(4\pi L)^{-\kappa}(1+O(\log L/L))$, and

$$\boxed{\mathrm{prec}_{N,K}\sim C_K(\rho)\,N^{-\frac{1-\rho}{1+\rho}}\,(4\pi\log N)^{-\frac{\rho}{1+\rho}},\qquad
C_K(\rho)=\frac{(1+\rho)^2}{\tau\,K}\Big[\frac{\Gamma(K+\frac1{1+\rho})}{\Gamma(K)}\Big]^2.}$$

* **Limit:** 0 for every $\rho<1$ and every fixed $K$.
* **Rate:** the power $N^{-\beta}$, $\beta=(1-\rho)/(1+\rho)=(1-\sqrt r)/(1+\sqrt r)$ with $r=\rho^2$, times
  the slowly varying $(\log N)^{-\kappa}$. $\beta$ falls from 1 at $\rho=0$ to 0 as $\rho\to1$.
  At $\rho=0.7459$, $\beta=0.1455$; at $\rho=0.7098$, $\beta=0.1697$.
* **Sanity checks:** $\rho=0$ gives $c=1$, $C_K=K$ and $\mathrm{prec}=K/N$, exact for random selection.
  $K=1$ gives $C_1=\Gamma(1+c)^2(1+\rho)^2/\tau=\Gamma(c)^2/\tau$, the best-paper constant of §7.
  For large $K$, $C_K\approx(1+\rho)^2K^{\beta}/\tau$, so $\mathrm{prec}\approx\mathrm{const}\,(K/N)^\beta(\log N)^{-\kappa}$.
* **A wrong prefactor to avoid** (notes A). "A selected paper has quality $N(\rho z,\tau^2)$ and must
  exceed $z=\bar\Phi^{-1}(K/N)$" gives $\bar\Phi(\sqrt\beta z)$. It has the right exponents but a constant
  too small by $(1+\rho)R_K$: it puts the selected score at the threshold instead of above it (the
  factor $1+\rho$) and ignores the random thresholds (the factor $R_K$).

Prefactors ($C_K$ multiplies $N^{-\beta}(4\pi\log N)^{-\kappa}$; notes B's constant is $(4\pi)^{-\kappa}C_K$ and
multiplies $(\log N)^{-\kappa}N^{-\beta}$):

| $\rho$ | $\beta$ | $\kappa$ | $C_1$ | $C_5$ | $C_{10}$ | $C_{30}$ | $C_{100}$ |
|---|---|---|---|---|---|---|---|
| 0.5 | 0.3333 | 0.3333 | 2.1173 | 4.2519 | 5.4751 | 8.0134 | 12.0324 |
| 0.7459 | 0.1455 | 0.4272 | 3.6310 | 5.5098 | 6.2441 | 7.4468 | 8.9237 |
| 0.9 | 0.0526 | 0.4737 | 6.5213 | 8.5770 | 9.1190 | 9.8235 | 10.5272 |

### 4.4 The next corrections

There are two, of different kinds. I derived both for general $(K,M)$.

**(a) The $1/b_N^2$ (that is, $1/\log N$) correction.** Keep the next terms of §4.2:
$b_N/a_N=1-b_N^{-2}+O(b_N^{-4})$, so $e^{-c\frac ba(\xi+\eta)}=e^{-c(\xi+\eta)}(1+c(\xi+\eta)/b^2)$; the quadratic
factor $1-(\xi^2-2\rho\xi\eta+\eta^2)/(2\tau^2b^2)$; and the margin correction
$F_n\big(e^{-\xi}(1-\xi^2/2b^2)\big)=F_n(e^{-\xi})+\frac{\xi^2}{2b^2}e^{-\xi}\pi_{n-1}(e^{-\xi})$. Under the weight
$e^{-c\xi}F_n(e^{-\xi})/I_n$ the moments are derivatives of $\log I_n$ in $c$: $E\xi=-D_n$,
$E\xi^2=D_n^2+P_n+(1+\rho)^2$, and $\int\xi^2e^{-(1+c)\xi}\pi_{n-1}(e^{-\xi})d\xi=\frac{\Gamma(n+c)}{\Gamma(n)}\big(\psi(n+c)^2+P_n\big)$,
with $D_n=\psi(n+c)-(1+\rho)$ and $P_n=\psi'(n+c)$. Collecting the three pieces gives notes B's
expression. With $\psi(n+c)=D_n+1/c$ and $c\tau^2=1-\rho$, it simplifies to

$$\boxed{\beta_{K,M}=\kappa(D_K+D_M)-\frac{\rho}{2\tau^2}\Big[(D_K-D_M)^2+P_K+P_M+2(1+\rho)^2\Big],}$$

and for $M=K$

$$\beta_K=2\kappa\,\psi(K+c)-\frac{\rho(3-\rho)}{1-\rho}-\frac{\rho\,\psi'(K+c)}{1-\rho^2}.$$

$\beta_K=0$ at $\rho=0$, as it must. For $M\ne K$ the term $(D_K-D_M)^2\approx\log^2(M/K)$ survives;
for $M=K$ the $\log^2K$ terms cancel. My form and notes B's form agree to $10^{-15}$ at
$(K,M,\rho)=(1,1,0.5)$, $(10,20,0.75)$, $(10,100,0.7459)$, $(3,1000,0.9)$.

**Relation to notes A's correction.** Notes A expand about the re-centred level
$B_\ast=\bar\Phi^{-1}(a_\ast/N)$, $\log a_\ast=D_K$, and find $\mathrm{prec}\approx C_K^Aa_\ast^{2\kappa}e^{\kappa B_\ast^2}N^{-1}\big(1-\rho\sigma_K^2/(\tau^2B_\ast^2)\big)$
with $\sigma_K^2=P_K+(1+\rho)^2$. From §4.2, $B_\ast=b+\xi_\ast/a$ with $\xi_\ast=-D_K-D_K^2/(2b^2)+\dots$, so
$a_\ast^{2\kappa}e^{\kappa B_\ast^2}=e^{\kappa b^2}(1+2\kappa D_K/b^2+O(b^{-4}))$. Hence A's form equals B's form with
$\beta_K=2\kappa D_K-\rho\sigma_K^2/\tau^2$, which is the boxed $\beta_{K,K}$. The two coefficient sets differ
only through the reference level. Values:

| $\rho$ | quantity | $K=1$ | 5 | 10 | 30 | 100 |
|---|---|---|---|---|---|---|
| 0.5 | $\beta_K$ (about $b_N$) | −2.921 | −1.533 | −1.019 | −0.251 | +0.565 |
| 0.5 | $-\rho\sigma_K^2/\tau^2$ (about $B_\ast$) | −2.043 | −1.629 | −1.566 | −1.522 | −1.507 |
| 0.7459 | $\beta_K$ | −8.006 | −5.558 | −4.810 | −3.764 | −2.698 |
| 0.7459 | $-\rho\sigma_K^2/\tau^2$ | −6.601 | −5.455 | −5.292 | −5.181 | −5.142 |
| 0.9 | $\beta_K$ | −23.169 | −18.308 | −17.188 | −15.835 | −14.584 |
| 0.9 | $-\rho\sigma_K^2/\tau^2$ | −21.427 | −18.039 | −17.572 | −17.258 | −17.147 |

**(b) The joint-exceedance correction, relative size $O(\varepsilon_N)$.** The papers above in both
coordinates (mean $\mu_{11}=\varepsilon_Ne^{-c(\xi+\eta)}/c^2$) enter both counts. Write the counts as
$n_{11}+n_{10}$ and $n_{11}+n_{01}$ with independent Poisson cells of means $\mu_{11}$, $e^{-\xi}-\mu_{11}$,
$e^{-\eta}-\mu_{11}$. To first order in $\mu_{11}$, with $F_{M-1}=F_M-\pi_{M-1}$, all terms but one cancel:
$P(\cdot)=F_MF_K+\mu_{11}\pi_{M-1}\pi_{K-1}$. Integrating with $\int\lambda^{2c-1}\pi_{M-1}(\lambda)d\lambda=\Gamma(M+\beta)/\Gamma(M)$:

$$\omega_{K,M}=(1+\rho)^2\frac{\Gamma(K+\beta)\Gamma(M+\beta)}{\Gamma(K)\Gamma(M)I_KI_M},\qquad
\omega_K=\omega_{K,K}=\Big[\frac{\Gamma(K+\beta)}{\Gamma(K+c)}\Big]^2>0.$$

It is positive: the shared papers make the two events likelier together. It is a power of $N$
smaller than (a), so (a) dominates asymptotically. Binomial against Poisson counts add a relative
$O(K/N)$.

**The final law with its next correction:**

$$\boxed{\mathrm{prec}_{N,K}=\frac{\varepsilon_NI_K^2}{K}\Big[1+\frac{\beta_K}{b_N^2}+\omega_K\,\varepsilon_N+O(b_N^{-4})\Big].}$$

In the pure $\log N$ form the bracket is
$1+[\kappa\log(4\pi L)+\beta_K-2\kappa]/(2L)+\omega_K\varepsilon_N+O((\log L)^2/L^2)$, $L=\log N$
(`precision_fixed_K_asymptotic(..., order=1, form="logN")`).

**Size of the next correction in the range of interest.** $b_N^2=9.55$ at $N=10^3$ and $22.6$ at
$10^6$. At $\rho=0.7459$, $K=1$, $\beta_K/b_N^2=-0.84$ and $-0.35$. The real expansion parameter is
$1/(\beta b_N^2)$, the inverse squared gap in conditional-SD units: 0.30 at $\rho=0.7459$, $N=10^6$, and
0.84 at $\rho=0.9$. The second-order coefficients are large (fitted $\gamma_K\approx34$, 190, 1360 at
$\rho=0.5$, 0.7459, 0.9, $K=1$). So the series is asymptotic only: the first-order law is worse than
the leading law in the range for $\rho\ge0.75$, and it turns negative at $N=10^3$, $\rho=0.9$.
$\omega_K\varepsilon_N$ is 2.6 % at $\rho=0.7459$, $K=1$, $N=10^6$, and 12 % at $\rho=0.9$.

**Checks.** The exact integral works at any $N$, so I test the expansions far beyond the range.
Ratios exact / approximation (`precision_fixed_K`, `precision_fixed_K_asymptotic`):

| $\rho$ | $K$ | form | $10^3$ | $10^6$ | $10^{12}$ | $10^{30}$ | $10^{100}$ | $10^{300}$ |
|---|---|---|---|---|---|---|---|---|
| 0.5 | 1 | leading ($b_N$) | 0.8673 | 0.9127 | 0.9516 | 0.9795 | 0.9937 | 0.9979 |
| 0.5 | 1 | first order | 1.2023 | 1.0457 | 1.0112 | 1.0018 | 1.0002 | 1.0000 |
| 0.5 | 1 | pure ($\log N$) | 0.9263 | 0.9502 | 0.9746 | 0.9910 | 0.9980 | 0.9996 |
| 0.5 | 100 | leading | 1.1147 | 1.0357 | 1.0139 | 1.0047 | 1.0013 | 1.0004 |
| 0.5 | 100 | first order | 1.0512 | 1.0103 | 1.0025 | 1.0004 | 1.0000 | 1.0000 |
| 0.7459 | 1 | leading | 0.7616 | 0.8258 | 0.8875 | 0.9478 | 0.9832 | 0.9943 |
| 0.7459 | 1 | first order | 2.9360 | 1.2299 | 1.0557 | 1.0093 | 1.0009 | 1.0001 |
| 0.7459 | 1 | pure | 0.8288 | 0.8696 | 0.9152 | 0.9621 | 0.9887 | 0.9964 |
| 0.7459 | 10 | leading | 0.8292 | 0.8860 | 0.9311 | 0.9686 | 0.9899 | 0.9966 |
| 0.7459 | 10 | first order | 1.6294 | 1.1209 | 1.0310 | 1.0053 | 1.0005 | 1.0001 |
| 0.7459 | 100 | leading | 0.9623 | 0.9503 | 0.9655 | 0.9831 | 0.9944 | 0.9981 |
| 0.9 | 1 | leading | 0.6233 | 0.7118 | 0.7873 | 0.8761 | 0.9545 | 0.9838 |
| 0.9 | 1 | first order | −0.5317 | 7.3307 | 1.3729 | 1.0598 | 1.0060 | 1.0007 |
| 0.9 | 10 | leading | 0.6327 | 0.7331 | 0.8203 | 0.9056 | 0.9662 | 0.9880 |
| 0.9 | 100 | leading | 0.7087 | 0.7764 | 0.8481 | 0.9203 | 0.9714 | 0.9898 |

Every ratio tends to 1: the leading law and its prefactor are right. The first-order law converges
much faster once $N\gtrsim10^{12}$. Coefficient tests: let $y_N=b_N^2\big(\text{exact}/(\text{lead}(1+\omega_K\varepsilon_N))-1\big)$
and fit $y_N=\beta+\gamma/b^2+\delta/b^4$ on $N=10^{100},10^{200},10^{300}$; do the same about $B_\ast$:

| $\rho$, $K$ | fitted $\beta$ | $\beta_K$ formula | fitted A-coefficient | $-\rho\sigma_K^2/\tau^2$ |
|---|---|---|---|---|
| 0.5, 1 | −2.921 | −2.921 | −2.043 | −2.043 |
| 0.5, 100 | 0.565 | 0.565 | −1.507 | −1.507 |
| 0.7459, 1 | −8.005 | −8.006 | −6.601 | −6.601 |
| 0.7459, 10 | −4.809 | −4.810 | −5.292 | −5.292 |
| 0.7459, 100 | −2.698 | −2.698 | −5.142 | −5.142 |
| 0.9, 1 | −23.151 | −23.169 | −21.411 | −21.427 |
| 0.9, 100 | −14.573 | −14.584 | −17.134 | −17.147 |

The joint-exceedance term: notes B's exact/indep − 1 against $\omega_K\varepsilon_N$ is $2.39\times10^{-2}$
against $2.57\times10^{-2}$ at $N=10^6$ and $3.91\times10^{-6}$ against $4.01\times10^{-6}$ at $10^{30}$ ($\rho=0.7459$,
$K=1$); the ratio tends to 1 at the expected $1/b^2$ rate. `tests/test_analytic.py` re-checks the
law, the first-order law and $\beta_K$ at $N=10^{200}$.

### 4.5 The practical formula: fixed-percentile formula times $R_K$

Replace each Poisson count of §4.2 by its mean, that is $F_K(e^{-\eta})$ by $1\{e^{-\eta}<K\}$. Then
$\int e^{-c\eta}1\{e^{-\eta}<K\}d\eta=K^c/c$ in place of $I_K$. This is the fixed-percentile formula at
$p=K/N$ (deterministic thresholds): as $z\to\infty$, $P_2(z,z;\rho)\sim\phi_2(z,z)(1+\rho)^2/z^2$, which gives
$\mathrm{prec}_\infty(K/N)\sim\varepsilon_N(K^c/c)^2/K$. Hence

$$\boxed{\lim_{N\to\infty}\frac{\mathrm{prec}_{N,K}}{P_2(z,z;\rho)/(K/N)}=R_K=\Big[\frac{E[G_K^c]}{(EG_K)^c}\Big]^2=\Big[\frac{\Gamma(K+c)}{\Gamma(K)K^c}\Big]^2=1-\frac{\rho}{(1+\rho)^2K}+O(K^{-2}),\quad z=\bar\Phi^{-1}(K/N).}$$

$R_K<1$ by Jensen's inequality ($v\mapsto v^c$ is concave and the $K$-th arrival $G_K$ is random).
$R_K$ = 0.81, 0.95, 0.976, 0.992, 0.998 for $K$ = 1, 5, 10, 30, 100, nearly free of $\rho$.
The product $R_K\,P_2(z,z;\rho)/(K/N)$ keeps the exact Gaussian tail, so it avoids error (a)
(`precision_fixed_K_hybrid`, with a tail-accurate $P_2$). Ratios exact / hybrid:

| $\rho$ | $K$ | $10^3$ | $10^6$ | $10^{12}$ | $10^{30}$ | $10^{100}$ | $10^{300}$ |
|---|---|---|---|---|---|---|---|
| 0.5 | 1 | 1.0018 | 0.9887 | 0.9929 | 0.9970 | 0.9991 | 0.9997 |
| 0.5 | 10 | 1.0020 | 0.9984 | 0.9990 | 0.9996 | 0.9999 | 1.0000 |
| 0.7459 | 1 | 1.0250 | 0.9863 | 0.9814 | 0.9907 | 0.9971 | 0.9990 |
| 0.7459 | 10 | 1.0037 | 0.9981 | 0.9976 | 0.9989 | 0.9997 | 0.9999 |
| 0.7459 | 100 | 1.0009 | 0.9999 | 0.9997 | 0.9999 | 1.0000 | 1.0000 |
| 0.9 | 1 | 1.0796 | 1.0215 | 0.9856 | 0.9779 | 0.9914 | 0.9970 |
| 0.9 | 10 | 1.0058 | 1.0005 | 0.9975 | 0.9973 | 0.9990 | 0.9997 |
| 0.9 | 100 | 1.0009 | 1.0001 | 0.9998 | 0.9997 | 0.9999 | 1.0000 |

Over $N=10^3$–$10^6$ the hybrid is within 2.5 % ($K=1$, $\rho\le0.75$), 8 % ($K=1$, $\rho=0.9$, $N=10^3$, where
$\omega_1\varepsilon_N$ is 25 %), and 0.6 % for $K\ge10$. It is the recommended closed form in the range.
For numbers, use the exact integral; it is cheap.

### 4.6 Local log-log slope against the asymptotic slope

From the $b_N$ form, $db_N/d\log N=1/a_N$, so $d\log\varepsilon_N/d\log N=2\kappa b_N/a_N-1$ and

$$\frac{d\log\mathrm{prec}_{N,K}}{d\log N}=-\beta-2\kappa\Big(1-\frac{b_N}{a_N}\Big)-\frac{2\beta_K}{a_Nb_N^3}+\dots\approx-\beta-\frac{2\kappa}{b_N^2}.$$

The local slope is steeper than $-\beta$ and approaches it only like $1/\log N$.
`local_loglog_slope` gives the exact slope (a centred difference of the exact integral, step 0.02 in
$\log N$) or this leading form.

**The requested table.** $\rho^2\in\{0.3,0.45,0.56,0.7,0.85\}$, $K\in\{1,5,10,30,100\}$. "Secant" is
$\log(\mathrm{prec}(10^6)/\mathrm{prec}(10^3))/\log(10^3)$; "local" is the exact derivative at the stated $N$.

| $\rho^2$ | $\rho$ | $K$ | prec $10^3$ | prec $10^6$ | secant $10^3\to10^6$ | local $10^3$ | local $10^{4.5}$ | local $10^6$ | asymptotic $-\beta$ | secant / $(-\beta)$ | secant $10^{30}\to10^{100}$ |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0.3 | 0.5477 | 1 | 0.0578 | 0.0062 | −0.3236 | −0.3394 | −0.3220 | −0.3143 | −0.2922 | 1.11 | −0.2948 |
| 0.3 | 0.5477 | 5 | 0.1171 | 0.0123 | −0.3267 | −0.3431 | −0.3252 | −0.3168 | −0.2922 | 1.12 | −0.2949 |
| 0.3 | 0.5477 | 10 | 0.1518 | 0.0156 | −0.3290 | −0.3474 | −0.3272 | −0.3180 | −0.2922 | 1.13 | −0.2949 |
| 0.3 | 0.5477 | 30 | 0.2265 | 0.0226 | −0.3338 | −0.3580 | −0.3313 | −0.3203 | −0.2922 | 1.14 | −0.2949 |
| 0.3 | 0.5477 | 100 | 0.3539 | 0.0335 | −0.3414 | −0.3787 | −0.3374 | −0.3233 | −0.2922 | 1.17 | −0.2949 |
| 0.45 | 0.6708 | 1 | 0.1112 | 0.0224 | −0.2317 | −0.2483 | −0.2302 | −0.2215 | −0.1970 | 1.18 | −0.1999 |
| 0.45 | 0.6708 | 5 | 0.1942 | 0.0388 | −0.2333 | −0.2495 | −0.2319 | −0.2233 | −0.1970 | 1.18 | −0.2000 |
| 0.45 | 0.6708 | 10 | 0.2361 | 0.0464 | −0.2354 | −0.2535 | −0.2338 | −0.2244 | −0.1970 | 1.19 | −0.2000 |
| 0.45 | 0.6708 | 30 | 0.3178 | 0.0605 | −0.2400 | −0.2638 | −0.2377 | −0.2267 | −0.1970 | 1.22 | −0.2000 |
| 0.45 | 0.6708 | 100 | 0.4430 | 0.0801 | −0.2475 | −0.2838 | −0.2437 | −0.2296 | −0.1970 | 1.26 | −0.2000 |
| 0.56 | 0.7483 | 1 | 0.1656 | 0.0478 | −0.1799 | −0.1961 | −0.1785 | −0.1696 | −0.1439 | 1.25 | −0.1470 |
| 0.56 | 0.7483 | 5 | 0.2639 | 0.0760 | −0.1801 | −0.1954 | −0.1788 | −0.1704 | −0.1439 | 1.25 | −0.1470 |
| 0.56 | 0.7483 | 10 | 0.3088 | 0.0879 | −0.1820 | −0.1991 | −0.1804 | −0.1715 | −0.1439 | 1.26 | −0.1471 |
| 0.56 | 0.7483 | 30 | 0.3912 | 0.1080 | −0.1863 | −0.2086 | −0.1841 | −0.1735 | −0.1439 | 1.29 | −0.1471 |
| 0.56 | 0.7483 | 100 | 0.5101 | 0.1342 | −0.1933 | −0.2273 | −0.1898 | −0.1764 | −0.1439 | 1.34 | −0.1471 |
| 0.7 | 0.8367 | 1 | 0.2624 | 0.1108 | −0.1248 | −0.1393 | −0.1236 | −0.1152 | −0.0889 | 1.40 | −0.0920 |
| 0.7 | 0.8367 | 5 | 0.3745 | 0.1601 | −0.1230 | −0.1364 | −0.1219 | −0.1144 | −0.0889 | 1.38 | −0.0921 |
| 0.7 | 0.8367 | 10 | 0.4202 | 0.1778 | −0.1245 | −0.1394 | −0.1232 | −0.1152 | −0.0889 | 1.40 | −0.0922 |
| 0.7 | 0.8367 | 30 | 0.4981 | 0.2055 | −0.1282 | −0.1477 | −0.1264 | −0.1170 | −0.0889 | 1.44 | −0.0922 |
| 0.7 | 0.8367 | 100 | 0.6027 | 0.2383 | −0.1343 | −0.1638 | −0.1313 | −0.1195 | −0.0889 | 1.51 | −0.0922 |
| 0.85 | 0.9220 | 1 | 0.4291 | 0.2600 | −0.0725 | −0.0834 | −0.0717 | −0.0651 | −0.0406 | 1.79 | −0.0436 |
| 0.85 | 0.9220 | 5 | 0.5402 | 0.3356 | −0.0689 | −0.0789 | −0.0681 | −0.0624 | −0.0406 | 1.70 | −0.0437 |
| 0.85 | 0.9220 | 10 | 0.5811 | 0.3586 | −0.0699 | −0.0810 | −0.0689 | −0.0628 | −0.0406 | 1.72 | −0.0438 |
| 0.85 | 0.9220 | 30 | 0.6447 | 0.3905 | −0.0726 | −0.0871 | −0.0712 | −0.0641 | −0.0406 | 1.79 | −0.0438 |
| 0.85 | 0.9220 | 100 | 0.7234 | 0.4246 | −0.0771 | −0.0990 | −0.0749 | −0.0660 | −0.0406 | 1.90 | −0.0438 |

The leading-form slope $-\beta-2\kappa(1-b_N/a_N)$ at $N=10^3$, $10^{4.5}$, $10^6$ is $-0.350$, $-0.330$, $-0.320$
($\rho^2=0.3$); $-0.263$, $-0.240$, $-0.229$ (0.45); $-0.214$, $-0.190$, $-0.178$ (0.56); $-0.164$, $-0.138$, $-0.125$ (0.7);
$-0.120$, $-0.092$, $-0.078$ (0.85). It is steeper than the exact slope at $K=1$–$10$ by 0.003 to 0.037; the gap is largest at $\rho^2=0.85$, $N=10^3$, where the $\beta_K/b_N^2$ term is large.

**Reading the table.** A power law fitted over $10^3$–$10^6$ overstates the asymptotic decay rate by
11–17 % at $\rho^2=0.3$, 25–34 % at $\rho^2=0.56$, and 70–90 % at $\rho^2=0.85$. Larger $K$ gives a
steeper slope at small $N$. Even from $10^{30}$ to $10^{100}$ the secant is 1–8 % steeper than $-\beta$.
The slope approaches $-\beta$ from below, so the range-of-interest decline is faster than the
asymptotic law suggests. Notes A and notes B report the same pattern at their $\rho$ values (for
example, secant/asymptote 1.25–1.35 at $\rho=0.75$, and 1.25–1.34 at $\rho=0.7459$).

---

## 5. The mechanism (item 5)

Three facts carry the account.

1. **Quality given score.** $X\mid Y=y\sim N(\rho y,\tau^2)$ for every $y$. So the concomitant of the $i$-th
   largest score is $X_{[i]}=\rho Y_{(i)}+\tau W_i$ with $W_i$ iid $N(0,1)$, independent of the scores. Its mean
   is $\rho\,EY_{(i)}$ and its variance is $\tau^2+\rho^2\mathrm{Var}\,Y_{(i)}\approx\tau^2$, since
   $\mathrm{Var}\,Y_{(1)}\approx\pi^2/(6b_N^2)\to0$. The spread of quality at a given score never shrinks.
2. **Where the tops sit.** $EY_{(1)}=b_N+\gamma_E/a_N+\dots\approx\sqrt{2\log N}$. The true top-$K$ bar
   $X_{(K)}$ has the law of $Y_{(K)}$, so $EX_{(K)}\approx b_N-\log K/b_N$ also grows like $\sqrt{2\log N}$.
3. **The gap.** The top-scored paper's expected quality is $\rho\,EY_{(1)}$. It falls short of the true
   top level by about $(1-\rho)b_N$, which grows without bound, while the conditional SD $\tau$ stays
   fixed. In SD units the shortfall is $(1-\rho)b_N/\tau=\sqrt\beta\,b_N$. The chance to bridge it is a
   Gaussian tail, $\bar\Phi(\sqrt\beta b_N)\approx e^{-\beta b_N^2/2}\approx N^{-\beta}$ up to logarithms: the
   exponent of §4. The reverse view gives the same number: a truly top paper has quality near $b_N$ and
   score $\rho b_N\pm\tau$, so it reaches the score bar only with noise of about $\sqrt\beta b_N$ SDs.

**Laplace view of the exponent.** A paper in both tops needs $x\gtrsim b_N$ and $y\gtrsim b_N$. The cheapest such
point is $x=y=b_N$, where $\phi_2\propto e^{-b_N^2/(1+\rho)}=N^{-2/(1+\rho)}\times$ logs. $N$ papers times this,
divided by $K$, give $N^{1-2/(1+\rho)}=N^{-\beta}$.

**What is selected instead.** The selected papers have quality about $\rho b_N\pm\tau$: very good (true
percentile $1-O(N^{-\rho^2})$), but not the best (true rank about $N^{1-\rho^2}$, §8). This is the
optimizer's curse: the top-scored paper is over-rated by $EY_{(1)}-EX_{[1]}=(1-\rho)EY_{(1)}$ standardised
units, which grows like $\sqrt{\log N}$. Meanwhile the spacing of the top qualities shrinks like $1/b_N$
(0.287 at $N=10^3$, 0.198 at $10^6$), so the selection must find the best few in a growing crowd of
near-ties with a fixed resolution $\tau$.

**Fixed percentile.** Both bars stay at $z_p$. A paper at the bar has expected quality $\rho z_p$, so the
shortfall $(1-\rho)z_p/\tau=\sqrt\beta z_p$ is constant. Nothing grows with $N$, so precision is $N$-free (§2).

**Checks** (`expected_kth_best`, `conditional_quality_mean`, `conditional_quality_sd`,
`true_topK_threshold`, `mechanism_gap`; exact order-statistic integrals):

| $\rho$ | $N$ | $EY_{(1)}$ | $\rho EY_{(1)}$ | $EX_{(10)}$ (bar for the true top 10) | $(EX_{(10)}-\rho EY_{(1)})/\tau$ | $(1-\rho)EY_{(10)}/\tau$ | exact $\mathrm{prec}_{N,10}$ |
|---|---|---|---|---|---|---|---|
| 0.7459 | $10^3$ | 3.2414 | 2.4178 | 2.3431 | −0.11 | 0.89 | 0.3062 |
| 0.7459 | $10^4$ | 3.8516 | 2.8729 | 3.1041 | 0.35 | 1.18 | 0.1964 |
| 0.7459 | $10^5$ | 4.3843 | 3.2703 | 3.7310 | 0.69 | 1.42 | 0.1291 |
| 0.7459 | $10^6$ | 4.8629 | 3.6272 | 4.2757 | 0.97 | 1.63 | 0.0862 |
| 0.7459 | $10^{12}$ | 7.1125 | 5.3052 | 6.7133 | 2.11 | 2.56 | 0.0088 |
| 0.6 | $10^6$ | 4.8629 | 2.9177 | 4.2757 | 1.70 | 2.14 | 0.0252 |
| 0.9 | $10^6$ | 4.8629 | 4.3766 | 4.2757 | −0.23 | 0.98 | 0.2974 |

The quantile bar $\bar\Phi^{-1}(10/N)$ is 2.3263, 3.0902, 3.7190, 4.2649 for $N=10^3$–$10^6$, close to $EX_{(10)}$.
Fixed percentile at $\rho=0.7459$: the gap is $0.887\tau$ ($p=1$ %), $0.628\tau$ (5 %), $0.257\tau$ (25 %), for every
$N$. Both notes report the same numbers in other summary forms (R5). Notes A's simulator check
($\rho=0.75$, $N=10^4$, 2000 conferences): mean quality of the top-scored paper $2.884\pm0.016$ against
$\rho EY_{(1)}=2.889$, and SD 0.714 against $\sqrt{\tau^2+\rho^2\mathrm{Var}\,Y_{(1)}}\approx0.70$.

---

## 6. Containment in a fixed top percentile (item 6)

**Exact value.** For any function $g$ of the score, exchangeability gives
$E\sum_{i\in\mathrm{Top}_K(Y)}g(Y_i)=N\int\phi(y)P(\mathrm{Bin}(N-1,\bar\Phi(y))\le K-1)g(y)\,dy$. With the population
bar $z_p$ and $g(y)=P(X>z_p\mid Y=y)=\Phi((\rho y-z_p)/\tau)$:

$$C_{N,K}(p)=\frac NK\int_0^1F_{\rm Bin}(K-1;N-1,v)\,\Phi\Big(\frac{\rho\bar\Phi^{-1}(v)-z_p}{\tau}\Big)dv$$

(`containment_limit(K, p, rho, N)`).

The empirical bar (the true top $\mathrm{round}(pN)$) is the §4.1 formula with $M=\mathrm{round}(pN)$
(`containment_fixed_K`). The two differ by $2\times10^{-3}$ at $N=10^3$ and by $10^{-4}$ or less at $N\ge10^4$.
`containment_miss` returns $1-C_{N,K}(p)$ directly, with no cancellation, for miss rates down to $10^{-40}$.

**Limit.** The selected scores grow like $b_N$, so their qualities $\rho b_N+\tau W$ pass any fixed $z_p$:

$$\lim_{N\to\infty}C_{N,K}(p)=1\qquad(\rho>0,\ \text{any fixed }p\text{ and }K).$$

**Rate.** Put $Y_{(j)}=b_N+x_j/a_N$ and $w_N=(\rho b_N-z_p)/\tau$. The Mills-ratio step
$\bar\Phi(w+\delta)\approx\bar\Phi(w)e^{-w\delta}$ with $\delta=\rho x_j/(a_N\tau)$ gives
$P(X_{[j]}<z_p)\approx\bar\Phi(w_N)e^{-\gamma_Nx_j}$, $\gamma_N=\rho w_N/(a_N\tau)\to\rho^2/\tau^2$. For the Poisson
process $e^{-x_j}\sim\mathrm{Gamma}(j,1)$, so $E e^{-\gamma x_j}=\Gamma(j+\gamma)/\Gamma(j)$, and
$\sum_{j\le K}\Gamma(j+\gamma)/\Gamma(j)=\Gamma(K+1+\gamma)/((1+\gamma)\Gamma(K))$. Hence

$$\boxed{1-C_{N,K}(p)\approx\bar\Phi(w_N)\,\frac{\Gamma(K+1+\gamma_N)}{(1+\gamma_N)\,\Gamma(K+1)},\qquad
\bar\Phi(w_N)=N^{-\rho^2/\tau^2}\,e^{(\rho z_p/\tau^2)\sqrt{2\log N}}\times(\text{powers of }\log N).}$$

The factor $e^{(\rho z_p/\tau^2)\sqrt{2\log N}}$ grows faster than any power of $\log N$, so convergence is slow
in practice (`containment_miss_asymptotic`).

**Fixed multiple instead of a fixed fraction.** For the true top $M$ with $M$ fixed (for example
$M=2K$ or $10K$), §4.3 gives $E\lvert\mathrm{Top}_K(Y)\cap\mathrm{Top}_M(X)\rvert/K\sim\varepsilon_NI_KI_M/K\to0$, at the rate of
the precision, with the correction $\beta_{K,M}/b_N^2+\omega_{K,M}\varepsilon_N$ of §4.4
(`containment_fixed_K_asymptotic`). The dividing line is $M\asymp N^{1-\rho^2}$, the typical true rank
of a selected paper (§8): containment tends to 1 if $M/N^{1-\rho^2}\to\infty$ and to 0 if $M$ is fixed.

**Mean true percentile.** $E[\Phi(X)\mid Y=y]=P(X'<\rho y+\tau Z)=\Phi(\rho y/\sqrt{2-\rho^2})$ for an independent copy
$X'$. So the mean percentile of $\mathrm{Top}_K(Y)$ is exactly the integral above with
$g(y)=\Phi(\rho y/\sqrt{2-\rho^2})$ (`mean_true_percentile`), and $1-\mathrm{pctl}\asymp N^{-\rho^2/(2-\rho^2)}$.

**Checks** ($p=1$ %; exact = `containment_fixed_K` with $M=\mathrm{round}(0.01N)$, computed for $N\le10^6$;
population bar = `containment_limit(..., N)`; miss = `containment_miss`; asymptotic = boxed formula):

| $\rho$ | $N$ | $K=1$: exact | population bar | miss | asymptotic miss | $K=10$: exact | population bar | miss | asymptotic miss |
|---|---|---|---|---|---|---|---|---|---|
| 0.5 | $10^3$ | 0.2111 | 0.2121 | 0.788 | 0.912 | 0.1268 | 0.1277 | 0.872 | 0.672 |
| 0.5 | $10^6$ | 0.5476 | 0.5476 | 0.452 | 0.475 | 0.4576 | 0.4576 | 0.542 | 0.481 |
| 0.5 | $10^{12}$ | | 0.9212 | 7.88e-2 | 8.01e-2 | | 0.8961 | 1.04e-1 | 9.88e-2 |
| 0.5 | $10^{20}$ | | 0.9964 | 3.59e-3 | 3.61e-3 | | 0.9949 | 5.06e-3 | 4.92e-3 |
| 0.7459 | $10^3$ | 0.5507 | 0.5485 | 0.452 | 0.516 | 0.3062 | 0.3071 | 0.693 | 0.506 |
| 0.7459 | $10^4$ | 0.7815 | 0.7811 | 0.219 | 0.231 | 0.5972 | 0.5969 | 0.403 | 0.330 |
| 0.7459 | $10^6$ | 0.9706 | 0.9706 | 2.94e-2 | 2.98e-2 | 0.9295 | 0.9295 | 7.05e-2 | 6.34e-2 |
| 0.7459 | $10^{12}$ | | 1.0000 | 5.27e-6 | 5.25e-6 | | 1.0000 | 1.83e-5 | 1.76e-5 |
| 0.9 | $10^3$ | 0.8743 | 0.8666 | 0.133 | 0.133 | 0.5317 | 0.5291 | 0.471 | 0.415 |
| 0.9 | $10^6$ | 1.0000 | 1.0000 | 6.84e-6 | 6.71e-6 | 0.9999 | 0.9999 | 1.18e-4 | 1.25e-4 |
| 0.9 | $10^{12}$ | | 1.0000 | 7.95e-20 | 7.88e-20 | | 1.0000 | 3.71e-18 | 3.78e-18 |
| 0.9 | $10^{20}$ | | 1.0000 | 9.64e-43 | 9.57e-43 | | 1.0000 | 7.12e-41 | 7.14e-41 |

At $K=1$ the asymptotic miss rate is accurate to 1–3 % once the miss is small (from $N=10^6$ at
$\rho=0.7459$, and from $10^{8}$ at $\rho=0.5$). At $K=10$ it is 4–10 % low over the same range and
approaches slowly (2–3 % at $N=10^{20}$). The reason: the step $\bar\Phi(w+\delta)\approx\bar\Phi(w)e^{-w\delta}$ drops
$-\delta^2/2-\log(1+\delta/w)$ in the exponent, which matters for $j$ near $K$ ($x_j\approx-\log j$) while $w_N$
is still small ($w_N=1.8$ at $N=10^6$, $\rho=0.7459$). These values match notes B's Table 6 and notes A's §6 table to their
rounding. Top-$M$ law at $\rho=0.75$, exact / leading law: $(K,M)=(10,20)$: 0.8798, 0.9281, 0.9673, 0.9895,
0.9946 at $N=10^6,10^{12},10^{30},10^{100},10^{200}$; with the $\beta_{K,M}$ and $\omega_{K,M}$ correction: 1.1268,
1.0323, 1.0056, 1.00053, 1.00014. The residual falls by a factor 3.9 from $10^{100}$ to $10^{200}$, as an
$O(b_N^{-4})$ remainder must (a factor 4.1); a wrong $\beta_{K,M}$ would leave an $O(b_N^{-2})$ remainder (a
factor 2). The same holds for $(10,100)$, $(1,10)$ and $(5,1000)$, where $\beta_{K,M}=-8.40$, $-10.74$, $-27.18$.
The simulator checks of `c1pct`, `c5pct`, `c2x`, `c10x`, `cA` and `pctl` are in §13.

---

## 7. Best-paper probability (item 7)

Here "the best paper" is the single truly best submission, quality rank 1. It is not the Best Papers
tier, which is the first three papers of the award ordering.

**Exact formula.** Let $m$ be the best paper's quality, with density $N\phi(m)\Phi(m)^{N-1}$, and $y$ its score,
$y\mid m\sim N(\rho m,\tau^2)$. The other $N-1$ papers are iid given $X<m$. Each out-scores the best paper with
probability

$$\pi(m,y)=P(Y>y\mid X<m)=\frac{\bar\Phi(y)-P_2(m,y;\rho)}{\Phi(m)}.$$

The best paper is in $\mathrm{Top}_K(Y)$ if and only if at most $K-1$ others out-score it:

$$\boxed{P_{\rm best}(N,K)=\iint N\phi(m)\Phi(m)^{N-1}\,\frac{\phi\big((y-\rho m)/\tau\big)}{\tau}\,F_{\rm Bin}\big(K-1;N-1,\pi(m,y)\big)\,dy\,dm.}$$

`best_paper_prob(N, K, rho)` evaluates it in the copula variables of §4.1. The handoff's semi-analytic
route replaces the binomial by Poisson($\lambda$), $\lambda=(N-1)\pi$ (`method="poisson"`); that changes the
answer by a relative $O(K/N)$. For $K=1$ the event is $\{\arg\max Y=\arg\max X\}$, so
$P_{\rm best}(N,1)=\mathrm{prec}_{N,1}$; the two integrands coincide algebraically at $K=1$.

**Leading law.** Put $m=b_N+\xi/a_N$ ($\xi$ Gumbel, density $e^{-\xi}e^{-e^{-\xi}}$) and $y=b_N+\eta/a_N$. Then
$(y-\rho m)/\tau=\sqrt\beta b_N+(\eta-\rho\xi)/(a_N\tau)$, and since $(1-\rho)/\tau^2=c$,
$\phi((y-\rho m)/\tau)\approx\phi(\sqrt\beta b_N)e^{-c(\eta-\rho\xi)}$. The count of out-scorers is Poisson($e^{-\eta}$) to
leading order. With $E[e^{\theta\xi}]=\Gamma(1-\theta)$ for a Gumbel variable ($\theta=c\rho=\kappa$) and
$\phi(\sqrt\beta b_N)/(\tau a_N)=\varepsilon_N$:

$$\boxed{P_{\rm best}(N,K)\sim\varepsilon_N\,\Gamma(c)\,I_K=\frac{(1+\rho)\,\Gamma(\frac1{1+\rho})\,\Gamma(K+\frac1{1+\rho})}{\tau\,\Gamma(K)}\,\frac{e^{\kappa b_N^2}}N\sim\frac{(1+\rho)\Gamma(c)\Gamma(K+c)}{\tau\,\Gamma(K)}\,N^{-\beta}(4\pi\log N)^{-\kappa}.}$$

* The rate is the same as for precision. At $K=1$ the constant equals $C_1$, since $\Gamma(c)=\Gamma(1+c)/c$.
* In $K$: $P_{\rm best}\propto\Gamma(K+c)/\Gamma(K)\approx K^{c}=K^{1/(1+\rho)}$, until $K$ nears $N^{1-\rho^2}$ (then it tends to 1, §8).
* $P_{\rm best}(N,K)/\mathrm{prec}_{N,K}\to\Gamma(1+c)\Gamma(K+1)/\Gamma(K+c)\approx\Gamma(1+c)K^{\kappa}$: widening the selected set from 1
  to $K$ raises the chance to include the best paper roughly like $K^{\rho/(1+\rho)}$ relative to precision.
**The first correction.** The best paper is the true top 1. So, exactly,
$P_{\rm best}(N,K)=E\lvert\mathrm{Top}_K(Y)\cap\mathrm{Top}_1(X)\rvert$: the §4.1 count with $M=1$. The code agrees:
`best_paper_prob` / ($K\cdot$`containment_fixed_K(N, K, 1, rho)`) − 1 is below $4\times10^{-13}$ for $\rho$ = 0.5, 0.7459, 0.9,
$K\le30$, $N=10^3$ and $10^{100}$. The leading law is §4.3 with $M=1$, $\varepsilon_NI_KI_1$, and $I_1=\Gamma(c)$. §4.4 with
$M=1$ gives the next terms:

$$\boxed{P_{\rm best}(N,K)=\varepsilon_N\,\Gamma(c)\,I_K\Big[1+\frac{\beta_{K,1}}{b_N^2}+\omega_{K,1}\,\varepsilon_N+O(b_N^{-4})\Big].}$$

The first correction is $O(1/\log N)$ in the $b_N$ form and $O(\log\log N/\log N)$ in the pure $\log N$ form (R4e).
For $K>1$ the term $(D_K-D_1)^2\approx\log^2K$ of $\beta_{K,1}$ does not cancel, so $\beta_{K,1}$ is more negative
than $\beta_K$ and the correction is larger than for precision. `best_paper_prob_asymptotic(..., order=1)`
implements the bracket. Ratios exact / leading law and exact / first-order law:

| $\rho$ | $K$ | $\beta_{K,1}$ | $\beta_K$ | $\omega_{K,1}$ | law | $10^3$ | $10^6$ | $10^{12}$ | $10^{30}$ | $10^{100}$ | $10^{300}$ |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0.5 | 1 | −2.921 | −2.921 | 0.979 | leading | 0.8673 | 0.9127 | 0.9516 | 0.9795 | 0.9937 | 0.9979 |
| 0.5 | 1 | | | | first order | 1.2023 | 1.0457 | 1.0112 | 1.0018 | 1.00016 | 1.00002 |
| 0.5 | 5 | −2.940 | −1.533 | 0.578 | leading | 0.8523 | 0.9101 | 0.9509 | 0.9793 | 0.9937 | 0.9979 |
| 0.5 | 5 | | | | first order | 1.2033 | 1.0447 | 1.0109 | 1.0017 | 1.00016 | 1.00002 |
| 0.5 | 30 | −5.053 | −0.251 | 0.318 | leading | 0.7055 | 0.8378 | 0.9139 | 0.9642 | 0.9891 | 0.9963 |
| 0.5 | 30 | | | | first order | 1.4706 | 1.0782 | 1.0178 | 1.0028 | 1.00024 | 1.00003 |
| 0.7459 | 1 | −8.006 | −8.006 | 1.101 | leading | 0.7616 | 0.8258 | 0.8875 | 0.9478 | 0.9832 | 0.9943 |
| 0.7459 | 1 | | | | first order | 2.9360 | 1.2299 | 1.0557 | 1.0093 | 1.00087 | 1.00010 |
| 0.7459 | 10 | −10.505 | −4.810 | 0.395 | leading | 0.6185 | 0.7524 | 0.8506 | 0.9316 | 0.9779 | 0.9925 |
| 0.7459 | 10 | | | | first order | −9.5058 | 1.3823 | 1.0787 | 1.0125 | 1.00116 | 1.00013 |
| 0.9 | 5 | −26.469 | −18.308 | 0.521 | leading | 0.4856 | 0.6212 | 0.7385 | 0.8577 | 0.9482 | 0.9815 |
| 0.9 | 5 | | | | first order | −0.2923 | −5.2524 | 1.5285 | 1.0722 | 1.00709 | 1.00083 |
| 0.9 | 30 | −45.944 | −15.835 | 0.220 | leading | 0.2421 | 0.3959 | 0.5676 | 0.7612 | 0.9113 | 0.9681 |
| 0.9 | 30 | | | | first order | −0.0643 | −0.3916 | 7.1702 | 1.1693 | 1.01424 | 1.00162 |

At $K=1$, $\beta_{1,1}=\beta_1$, $\omega_{1,1}=\omega_1$ and the rows equal those of §4.4, since $P_{\rm best}(N,1)=\mathrm{prec}_{N,1}$.
For all 12 cells ($\rho$ = 0.5, 0.7459, 0.9; $K$ = 1, 5, 10, 30) the residual of the first-order law falls by a factor
8.5 to 9.1 from $N=10^{100}$ to $10^{300}$, as an $O(b_N^{-4})$ remainder must (a factor 9.2); a wrong $\beta_{K,1}$ would
leave an $O(b_N^{-2})$ remainder (a factor 3.0). In the range the series is asymptotic only, as for precision
(§4.4): for $\rho\ge0.75$ the first-order law is worse than the leading law at $N\le10^6$, and it is negative at
$\rho=0.9$, $N=10^6$, $K\ge5$ (the first-order value is $-0.088$ at $K=5$) and at $\rho=0.7459$, $N=10^3$, $K\ge10$. Use
`best_paper_prob` for numbers.

**Checks** (`best_paper_prob`, `best_paper_prob_asymptotic`):

| $\rho$ | $N$ | $K=1$ exact | Poisson/exact − 1 | exact/lead | $K=10$ exact | Poisson/exact − 1 | exact/lead | $K=30$ exact | exact/lead |
|---|---|---|---|---|---|---|---|---|---|
| 0.5 | $10^3$ | 0.044297 | 5.5e-4 | 0.867 | 0.211147 | 4.2e-4 | 0.813 | 0.383949 | 0.706 |
| 0.5 | $10^6$ | 0.0036065 | 5.6e-7 | 0.913 | 0.017907 | 4.9e-7 | 0.891 | 0.035276 | 0.838 |
| 0.5 | $10^{100}$ | 6.8831e-35 | 2e-16 | 0.994 | 3.4958e-34 | 7e-15 | 0.993 | 7.3002e-34 | 0.989 |
| 0.7459 | $10^3$ | 0.163542 | 4.0e-4 | 0.762 | 0.550737 | 1.9e-4 | 0.619 | 0.774718 | 0.460 |
| 0.7459 | $10^6$ | 0.0466955 | 4.3e-7 | 0.826 | 0.176414 | 3.1e-7 | 0.752 | 0.287200 | 0.648 |
| 0.7459 | $10^{12}$ | 0.0048937 | 4.4e-13 | 0.888 | 0.019450 | 3.7e-13 | 0.851 | 0.034077 | 0.788 |
| 0.7459 | $10^{100}$ | 3.3278e-16 | 0 | 0.983 | 1.3726e-15 | 5e-15 | 0.978 | 2.5711e-15 | 0.968 |
| 0.9 | $10^3$ | 0.374601 | 2.6e-4 | 0.623 | 0.874339 | 3.1e-5 | 0.389 | 0.978058 | 0.242 |
| 0.9 | $10^6$ | 0.206486 | 3.2e-7 | 0.712 | 0.587843 | 1.4e-7 | 0.542 | 0.772034 | 0.396 |
| 0.9 | $10^{100}$ | 7.8348e-7 | 0 | 0.955 | 2.8771e-6 | 4e-15 | 0.937 | 5.0282e-6 | 0.911 |

Small $N$: $N=2$ gives $\tfrac12+\arcsin(\rho)/\pi$ to $10^{-10}$; $N=3$, $K=2$ gives
$1-3P(X_1>X_{2,3},Y_1<Y_{2,3})$ (a 4-D orthant) to $2\times10^{-7}$ (the Genz tolerance). Own Monte Carlo at
$N=40$ (60,000 conferences, $K=1,5$) agrees within 4 SE in the test suite. Both notes' tables are
reproduced to their rounding (R7). The law holds but converges slowly; use the exact integral for
numbers. Simulator checks: notes B's pooled runs (up to 50,000 conferences per cell; 48 cells, all
within $|z|\le1.4$ after a rerun of one cell), notes A's runs at $\rho=0.75$ (all within 1.5 SE), and §13.

At $\rho=0.7459$: $P_{\rm best}$ for $K=1,5,10,30$ is 0.164, 0.411, 0.551, 0.775 at $N=10^3$ and 0.047, 0.124,
0.176, 0.287 at $N=10^6$.

---

## 8. Rank of the winner (item 8)

Let $W$ be the true rank (1 = best) of the top-scored paper.

**Exact identity.** $(X_i,Y_i)_{i\le N}$ has the same joint law as $(Y_i,X_i)_{i\le N}$ (equal variances, one
correlation). The event "the top-$Y$ paper is in $\mathrm{Top}_r(X)$" maps under the swap to "the top-$X$ paper
is in $\mathrm{Top}_r(Y)$". Hence, for every $r$ and $N$,

$$\boxed{P(W\le r)=P_{\rm best}(N,r).}$$

So §7 gives the whole distribution (`winner_rank_cdf`). The median is the smallest $r$ with
$P_{\rm best}(N,r)\ge\tfrac12$ (`winner_rank_quantile`, an integer search on the exact cdf). Notes A's direct
formula (condition on the winner's score $y$ and quality $\rho y+\tau w$; the others beat it in quality with
probability $\theta=(\bar\Phi(x)-P_2(x,y))/\Phi(y)$) is the same integral after the swap.

**Asymptotics.** Given $Y_{(1)}=s$ and $X_{[1]}=q$, $W-1\sim\mathrm{Bin}(N-1,P(X>q\mid Y<s))\approx\mathrm{Pois}(N\bar\Phi(q))$. When
$N\bar\Phi(q)$ is large the Poisson noise is negligible, so $W\approx N\bar\Phi(X_{[1]})$, a decreasing function of
$X_{[1]}=\rho Y_{(1)}+\tau Z$. The $u$-quantile of $W$ is then $N\bar\Phi(m_{1-u})$, with $m_v$ the $v$-quantile of
$\rho Y_{(1)}+\tau Z$. With $Y_{(1)}=b_N+G/a_N$, $G$ Gumbel, a small perturbation of the symmetric $\tau Z$ moves
its median by the mean of the perturbation, $\rho\gamma_E/a_N$. So

$$\boxed{\mathrm{median}(W)\approx N\bar\Phi\big(\rho b_N+\rho\gamma_E/a_N\big)\approx\frac{e^{-\gamma_E\rho^2}}{\rho}\Big(\frac{N}{\sqrt{2\pi}\,b_N}\Big)^{1-\rho^2}\approx\frac{e^{-\gamma_E\rho^2}}{\rho}\Big(\frac{N}{\sqrt{4\pi\log N}}\Big)^{1-\rho^2}.}$$

The second step uses $\bar\Phi(t)\approx\phi(t)/t$ and $e^{-b_N^2/2}\approx\sqrt{2\pi}b_N/N$. The median grows like
$N^{1-\rho^2}$ times $(\log N)^{-(1-\rho^2)/2}$, while the winner's true percentile tends to 1 ($W/N\asymp N^{-\rho^2}$).
The factor $e^{-\gamma_E\rho^2}$ (0.87, 0.73, 0.63 at $\rho$ = 0.5, 0.7459, 0.9) is easy to lose.

**Spread.** $\log W\approx\log N\bar\Phi(\rho b_N)-\rho b_N(\tau Z+\rho G/a_N)$, so $\log W$ is close to normal with
SD about $\sqrt{\rho^2\tau^2b_N^2+\pi^2\rho^4/6}$ (notes A; the second term is the Gumbel part). Notes B keep
only $\rho\tau b_N$. Both understate the spread, because they drop the curvature of $\log\bar\Phi$; the exact
cdf is cheap.

**Mean.** $E\bar\Phi(\rho y+\tau Z)=\bar\Phi(\rho y/\sqrt{2-\rho^2})$, so the mean rank grows like
$N^{1-\rho^2/(2-\rho^2)}=N^{2(1-\rho^2)/(2-\rho^2)}$, faster than the median: unlucky draws ($Z\ll0$) dominate it.

**Checks** (`winner_rank_quantile`, `winner_rank_median_asymptotic`):

| $\rho$ | $N$ | $W_{25}$ | median | $W_{75}$ | semi-asymptotic median | power form ($\sqrt{2\pi}b_N$) |
|---|---|---|---|---|---|---|
| 0.5 | $10^3$ | 14 | 53 | 153 | 51.5 | 66.3 |
| 0.5 | $10^6$ | 1259 | 7528 | 32797 | 7445 | 8537 |
| 0.5 | $10^{12}$ | 17,122,535 | 188,214,240 | 1,493,513,779 | 187,210,397 | 201,195,366 |
| 0.7459 | $10^3$ | 2 | 8 | 27 | 7.5 | 8.4 |
| 0.7459 | $10^4$ | 5 | 21 | 83 | 19.7 | 21.5 |
| 0.7459 | $10^5$ | 10 | 55 | 256 | 52.4 | 56.2 |
| 0.7459 | $10^6$ | 22 | 145 | 788 | 140.3 | 148.7 |
| 0.7459 | $10^{12}$ | 4147 | 56530 | 626444 | 55704 | 57351 |
| 0.9 | $10^3$ | 1 | 2 | 6 | 1.7 | 1.8 |
| 0.9 | $10^6$ | 2 | 7 | 26 | 5.9 | 6.0 |
| 0.9 | $10^{12}$ | 10 | 79 | 573 | 75.9 | 76.9 |

Every exact quantile equals notes B's Table 8a, including $N=10^{12}$ (notes B used a Poisson route there;
here the binomial cdf uses the incomplete beta function, which stays accurate at $n=10^{12}$ where scipy's
`bdtr` fails). The semi-asymptotic median is within 1–7 % for $\rho\le0.75$ and $N\ge10^3$, and 0.5–1.5 % at
$10^{12}$. At $\rho=0.9$ the rank is small, the dropped Poisson noise matters, and it is 15–25 % low over
$N=10^3$–$10^6$. The power form is 13–25 % high at $\rho=0.5$ and 2–5 % high at $\rho=0.7459$ over
$N=10^3$–$10^6$; notes B's $\log N$ form is 5–9 % high and 2–4 % low there. Spread at $\rho=0.7459$: exact $W_{75}/W_{25}$ = 13.5, 35.8,
151 at $N=10^3,10^6,10^{12}$; $e^{1.349\,\mathrm{SD}}$ gives 9.8, 27.9, 123 with A's SD and 7.9, 24.2, 112 with B's.
Simulator: the exact cdf at the simulator's per-run quartiles is 0.24–0.28, 0.49–0.54, 0.70–0.77
(targets 0.25, 0.50, 0.75; 12 runs at $N=10^3$–$10^5$, §13); notes B found 47 of 48 simulated medians
inside 2 SE of the exact law. Own Monte Carlo at $N=40$ confirms the cdf at $r=1,3,8$ and the median
(test suite).

---

## 9. Two-committee top-$K$ overlap (item 9)

**Derivation.** The committee scores $(Y_{1i},Y_{2i})$ are iid over papers and standard bivariate normal with
correlation $r_{12}=\rho^2$ ($u$ redrawn). $\lvert\mathrm{Top}_K(Y_1)\cap\mathrm{Top}_K(Y_2)\rvert$ is the §4 problem with the pair
$(Y_1,Y_2)$ in place of $(X,Y)$. So, exactly, at every $N$ and $K$,

$$\boxed{\mathrm{ovl}(N,K,\rho)=\mathrm{prec}(N,K,\rho^2)\sim C_K(\rho^2)\,N^{-\frac{1-\rho^2}{1+\rho^2}}(4\pi\log N)^{-\frac{\rho^2}{1+\rho^2}},}$$

with every correction of §4 at $\rho^2$, the practical form $R_K(\rho^2)P_2(z,z;\rho^2)/(K/N)$, and the
fixed-percentile version $P_2(z_p,z_p;\rho^2)/p$ (§3 is its $p=\alpha$ case). The rejection of a top-$K$ paper by
the second committee at rate $\alpha$ is $\mathrm{rej}_2=1-E\lvert\mathrm{Top}_K(Y_1)\cap\mathrm{Top}_A(Y_2)\rvert/K$, $A=\mathrm{round}(\alpha N)$:
the §4.1 integral with $M=A$ at correlation $\rho^2$ (`rejected_given_top`).

Since $\rho^2<\rho$, the overlap is below the precision and decays faster: exponent 0.285 against 0.146 at
$\rho=0.7459$. The overlap is observable without knowing quality, so it is the field-testable proxy for
precision; at fixed $(N,K)$ the map between them is monotone through $\rho$. If $u$ were shared,
$r_{12}>\rho^2$ and the overlap would overstate the reliability that matters.

**The tier sets** (`scripts/make_tier_scaling.py`, `results/tier_scaling.csv`). The closed form of the tiers
uses continuous scores and no chair noise, so the award ordering is the score. The tiers are separate. A
top-$M$ set of the award ordering holds a tier and every tier above it, so it is an "or Better" set:

| $M$ | the top-$M$ set |
|---|---|
| 3 | the Best Papers |
| $M_{\rm oob}$ (§4.1), fitted to series `oral_or_better` of `results/tier_sizes.csv` | Oral or Better (column `M_oral_or_better`; NeurIPS counts its Best Papers among its Orals) |
| $M_{\rm oob}+M_{\rm spot}$, with $M_{\rm spot}$ the Spotlight count (series `spot`, Spotlights only) | Spotlight or Better (column `M_spot_or_better`) |
| $A=\mathrm{round}(0.25N)$ | Accepted or Better |

$E\lvert\mathrm{Top}_3(Y_1)\cap\mathrm{Top}_M(Y_2)\rvert/3$ at correlation $\rho^2$ (`containment_fixed_K(N, 3, M, rho2)`) is
the probability that a second review puts one of the first review's Best Papers in that set: `p2_best`,
`p2_oral_or_better`, `p2_spot_or_better`, `p2_accept_or_better`. $\mathrm{ovl}(N,M,\rho)$ with $M=M_{\rm oob}$ is the
overlap of Oral or Better (`ovl_oral_or_better`); the same holds for the other two sets. A separate tier is the
gap between two consecutive sets, so its probability is a difference: `p2_oral` $=$ `p2_oral_or_better` $-$ `p2_best`.
`p2_reject` is $\mathrm{rej}_2$ above at $K=3$: 1 minus `p2_accept_or_better`.

**Values** ($K=10$, $N=10^3,10^4,10^5,10^6$): at $\rho=0.7459$, overlap 0.157, 0.073, 0.035, 0.017 against
precision 0.306, 0.196, 0.129, 0.086; at the repository's central $\rho=0.7098$, overlap 0.129, 0.054,
0.024, 0.010 against precision 0.270, 0.164, 0.102, 0.064.

**Checks.** The identity is exact, so the checks are those of §4 plus the simulator. Notes B's open item
(a low simulated overlap at $N=10^6$) is settled in §13.2: 24,000 fresh conferences at each of
$\rho=0.7459$ and $\rho=0.5$ agree with the exact values at every $K$.

---

## 10. Tails (item 10)

### 10.1 The principle

Write $S=Q+E$ on the original scale ($E$ = the per-paper noise, the mean of $R$ errors). Fixed-$K$ selection at
large $N$ looks only at the extreme upper corner of the (quality, score) pair: precision is
$(N/K)P(\text{a paper is in both tops})$, decided by the copula near $(1,1)$ at levels exceeded by $O(1)$ papers.
Let $\chi=\lim_{u\to1}P(F_S(S)>u\mid F_Q(Q)>u)$ be the upper tail-dependence coefficient.

* $\chi=0$ (asymptotic independence): precision $\to0$, like $N^{1-1/\eta_{LT}}$ times a slowly varying
  factor (Ledford–Tawn $\eta_{LT}\in[\tfrac12,1)$). The Gaussian pair has $\eta_{LT}=(1+\rho)/2$, which gives
  §4. $\eta_{LT}=\tfrac12$ gives about $K/N$, which is random selection.
* $0<\chi<1$: the point process of the top (quality, score) pairs has a non-degenerate limit, so
  precision tends to a positive plateau that depends on $K$ and tends to $\chi$ as $K$ grows (with $K/N\to0$).
* $\chi=1$ with noise negligible against the top quality spacings: precision $\to1$.

**Operational rule.** Two comparisons decide the case.
1. *Noise tail against quality tail.* If $P(E>x)/P(Q>x)\to\infty$, the top scores are noise extremes with
   near-typical quality, so $\chi=0$ and precision collapses to about $K/N$.
2. *Noise scale against the top quality spacing $a_Q(N)$* (the auxiliary function of the quality's
   extreme-value limit), when the noise tail is lighter: $a_Q/\sigma_E\to\infty$ gives precision $\to1$; a
   constant gives a plateau; $a_Q\to0$ gives decay.

| quality | top spacing $a_Q(N)$ | Gaussian noise | $t_3$ noise |
|---|---|---|---|
| Gaussian | $\sigma_q/\sqrt{2\log N}\to0$ | $\chi=0$: decay $N^{-\beta}(\log N)^{-\kappa}$ (§4) | noise heavier: collapse to $\approx K/N$ |
| exponential | $\sigma_q$ (constant) | $\chi=2\bar\Phi(\sigma/2)$, $\sigma=\sigma_E/\sigma_q$: **plateau** (10.2) | noise heavier: collapse |
| lognormal | grows slowly ($\propto x_N/\log x_N$) | $\chi=1$: $\to1$, very slowly | noise heavier: collapse |
| Student-$t_3$ | $\propto N^{1/3}$ | $\chi=1$: **rise to 1**, deficit $\propto(K/N)^{1/3}$ (10.3) | equal index: **plateau $w$** (10.4) |
| bounded Beta$(a,a)$ | $\propto N^{-1/a}\to0$ | noise heavier: decay $\propto(K/N)(\log N)^{a/2}$ (10.5) | collapse |

### 10.2 Exponential quality, Gaussian noise: a plateau

Work in units of $\sigma_q$ with $\sigma=\sigma_E/\sigma_q$. After a shift by $\log N$, the top qualities form a Poisson
process with intensity $e^{-x}dx$, exactly (the exponential tail has no slowly varying correction). Each
point carries an independent mark $e=\sigma Z$ and the score $x+e$. For a tagged point at $(x,x+e)$ the
Mecke formula makes the three region counts independent Poisson variables with means
$\mu_Q=\lambda$ (higher quality), $\mu_S=\lambda e^{\sigma^2/2-e}$ (higher score) and
$\mu_{11}=\lambda\big[\bar\Phi(e/\sigma)+e^{\sigma^2/2-e}\bar\Phi((\sigma^2-e)/\sigma)\big]$ (both), $\lambda=e^{-x}$. So

$$\lim_{N\to\infty}\mathrm{prec}_{N,K}=\frac1K\int_0^\infty d\lambda\;E_Z\Big[\sum_{m<K}\mathrm{Pois}(m;\mu_{11})F_{K-m}(\mu_Q-\mu_{11})F_{K-m}(\mu_S-\mu_{11})\Big],$$

and for $K=1$, $\int\phi(z)\big/\big(\Phi(z)+e^{\sigma^2/2-\sigma z}\bar\Phi(z-\sigma)\big)dz$. The limit is free of $N$ and strictly
between 0 and 1. Tail dependence: $P(S>s)=e^{\sigma^2/2}e^{-s}$ gives
$\chi=\int_0^\infty e^{-t}\bar\Phi((\sigma^2/2-t)/\sigma)dt=2\bar\Phi(\sigma/2)$.

### 10.3 $t_3$ quality, Gaussian noise: precision rises to 1

$P(Q>x)\sim c_Qx^{-3}$ with $c_Q=2\sigma_q^3/(3\pi)$ (the standardised $t_3$). The top qualities sit at scale
$(Nc_Q)^{1/3}$ and their spacings grow at that rate, while the noise stays $O(\sigma_E)$. To first order in
$\sigma_E/a_Q$ only the pair $(K,K+1)$ can swap; it swaps when the noise difference $D$ (SD $\sigma_E\sqrt2$) exceeds
the gap $G_K=Q_{(K)}-Q_{(K+1)}$. With $E[D^+]=\sigma_E/\sqrt\pi$ and, for the Poisson process,
$f_{G_K}(0)=\int\lambda^2e^{-\Lambda}\Lambda^{K-1}/(K-1)!\,dx=3(Nc_Q)^{-1/3}\Gamma(K+4/3)/\Gamma(K)$:

$$1-\mathrm{prec}_{N,K}\approx\frac1Kf_{G_K}(0)E[D^+]=\frac{\sigma_E}{\sigma_q}\,\frac{3\,\Gamma(K+4/3)}{K\sqrt\pi\,\Gamma(K)}\Big(\frac{3\pi}{2N}\Big)^{1/3}\propto\Big(\frac KN\Big)^{1/3}.$$

The same argument gives $1-\sigma/\sqrt\pi$ for the exponential at small $\sigma$, where $f_{G_K}(0)=K$.

### 10.4 $t_3$ quality and $t_3$ noise: the plateau $w$

Both tails are regularly varying with index 3. The mean of $R$ iid errors $\sigma_\varepsilon T_3/\sqrt3$ has
$P(E>x)\sim R\,P(\sigma_\varepsilon T_3/\sqrt3>Rx)=c_Ex^{-3}$, $c_E=2\sigma_\varepsilon^3/(3\pi R^2)$ (one big jump). The top of the
score list is the union of two independent Poisson processes: quality extremes with $O(1)$ noise, and
noise extremes with typical quality. Each top point is of quality type with probability
$w=c_Q/(c_Q+c_E)$, independently. The quality-type points among the top $K$ scores are the top qualities
in order, so all of them are in the true top $K$. Hence, for every $K$,

$$\lim_{N\to\infty}\mathrm{prec}_{N,K}=\chi=w=\Big[1+\frac{(\sigma_\varepsilon/\sigma_q)^3}{R^2}\Big]^{-1}=\Big[1+\frac{(\tau/\rho)^3}{\sqrt R}\Big]^{-1}.$$

The last form shows that the plateau depends on $R$ at fixed $\rho$: more reviewers at the same
reliability thin the noise tail.

### 10.5 Bounded quality, and heavier noise

Beta$(a,a)$ quality: $P(Q>q_{\max}-t)\approx C_Bt^a$. With Gaussian noise the top scores are noise extremes,
$s-q_{\max}\approx\sigma_E\sqrt{2\log N}$. Given such an $s$, $q_{\max}-Q$ is approximately Gamma($a$, rate
$(s-q_{\max})/\sigma_E^2$). The true top-$K$ band is $t\lesssim(K/(NC_B))^{1/a}$, so
$\mathrm{prec}\approx\frac{((s-q_{\max})/\sigma_E^2)^a}{\Gamma(a+1)}\frac K{NC_B}\asymp\frac{K(2\log N)^{a/2}}{N\sigma_E^aC_B}\to0$. For $\sigma_q=1.2$, $a=6.53$, the factor
$(\log N)^{3.27}$ is large, and the decline in the range is much slower than $1/N$. No sharp constant
was derived beyond this form. Any quality with a lighter tail than $t_3$ noise (Gaussian, exponential,
Beta) collapses: a true top paper is selected with probability about
$(K/N)(s_N/(s_N-q))^3\to K/N$, since $s_N\propto N^{1/3}$ outgrows $q\propto\sqrt{\log N}$.

### 10.6 Fixed-percentile precision for non-Gaussian shapes

For any continuous shapes the argument of §2.1 holds unchanged: the empirical quantiles converge to
$q_p$ and $s_p$, so

$$\lim_{N\to\infty}\mathrm{prec}_{pN}=\frac{P(Q>q_p,S>s_p)}p=\frac1p\int_{q_p}^\infty f_Q(q)\,\bar F_E(s_p-q)\,dq,\qquad\bar F_S(s_p)=p.$$

It does not depend on $N$ for any shape; finite-$N$ corrections are $O(1/(pN))$. Its value depends on
the shape at fixed $\rho$.

### 10.7 Checks

*Limits* (my evaluation of the formulas above, in both notes' settings):

| setting | exp/Gaussian plateau, $K$ = 1, 5, 10, 30, 100 | $\chi=2\bar\Phi(\sigma/2)$ | $t_3$/$t_3$ plateau $w$ |
|---|---|---|---|
| notes A: $\rho^2=0.5$, $\sigma_E=\sigma_q$ ($\sigma=1$) | 0.5387, 0.5925, 0.6042, 0.6126, 0.6157 | 0.6171 | 0.6340 |
| notes B: $\rho^2=0.5563$, $R=3$ ($\sigma=0.8931$) | 0.5787, 0.6301, 0.6420, 0.6506, 0.6538 | 0.6552 | 0.7086 |

The $K=1$ value from the 1-D form equals the Mecke form to 4 digits, and at $\sigma=10^{-3}$ the plateau is
0.9994359 against $1-\sigma/\sqrt\pi=0.9994358$. The $t_3$/Gaussian first-order law reproduces both notes'
values (notes B setting: $1-\mathrm{prec}$ = 0.1401, 0.0650 at $N=10^4,10^5$ for $K=1$; 0.2590, 0.1202 for $K=10$;
0.5472, 0.2540 for $K=100$). The $N$-free fixed-percentile limits with Gaussian noise (1-D quadrature, notes B
setting): exponential 0.6552, 0.6553, 0.6712; $t_3$ 0.6197, 0.5008, 0.5695; Beta 0.2463, 0.4081, 0.6385 for
$p$ = 1 %, 5 %, 25 %. Notes B computed the same values independently.

*Repository simulator* (fresh runs; notes B setting $\sigma_q=1.2$, $\sigma_\varepsilon=1.856$, $R=3$; 4000 conferences at
$N=10^4$, 800 at $10^5$; mean ± SE):

| quality / noise | $K$ | $N=10^4$ | $N=10^5$ | theory |
|---|---|---|---|---|
| exp / Gaussian | 1 | 0.5665 ± 0.0078 | 0.5750 ± 0.0175 | plateau 0.5787 |
| exp / Gaussian | 10 | 0.6424 ± 0.0020 | 0.6418 ± 0.0045 | plateau 0.6420 |
| exp / Gaussian | 100 | 0.6532 ± 0.0006 | 0.6555 ± 0.0014 | plateau 0.6538 ($\chi$ = 0.6552) |
| $t_3$ / Gaussian | 1 | 0.8790 ± 0.0052 | 0.9287 ± 0.0091 | rises to 1; first-order deficit 0.140, 0.065 |
| $t_3$ / Gaussian | 10 | 0.8050 ± 0.0016 | 0.9049 ± 0.0026 | first-order deficit 0.259, 0.120 (an upper bound in range) |
| $t_3$ / Gaussian | 100 | 0.6193 ± 0.0007 | 0.8180 ± 0.0011 | first-order deficit 0.547, 0.254 |
| Beta / Gaussian | 1 | 0.0297 ± 0.0027 | 0.0088 ± 0.0033 | decays to 0 |
| Beta / Gaussian | 10 | 0.1015 ± 0.0015 | 0.0328 ± 0.0019 | decays to 0 |
| Beta / Gaussian | 100 | 0.2453 ± 0.0006 | 0.1033 ± 0.0010 | decays to 0 |
| $t_3$ / $t_3$ | 1 | 0.6415 ± 0.0076 | 0.6562 ± 0.0168 | plateau 0.7086, approached slowly |
| $t_3$ / $t_3$ | 10 | 0.6380 ± 0.0022 | 0.6936 ± 0.0050 | plateau 0.7086 |
| $t_3$ / $t_3$ | 100 | 0.5481 ± 0.0007 | 0.6512 ± 0.0017 | plateau 0.7086 |
| Gaussian / $t_3$ | 10 | 0.0288 ± 0.0008 | 0.0009 ± 0.0003 | collapse to $\approx K/N$ |
| Gaussian / $t_3$ | 100 | 0.2522 ± 0.0006 | 0.0254 ± 0.0006 | collapse |

Fixed percentile in the same runs ($p$ = 1 %, 5 %, $\alpha$ = 25 %; $N=10^5$): exponential/Gaussian 0.6545,
0.6551, 0.6714 (limits 0.6552, 0.6553, 0.6712); $t_3$/Gaussian 0.6209, 0.5014, 0.5696 (0.6197, 0.5008,
0.5695); Beta/Gaussian 0.2470, 0.4079, 0.6384 (0.2463, 0.4081, 0.6385); $t_3$/$t_3$ 0.5498, 0.5146, 0.6141;
Gaussian/$t_3$ 0.2530, 0.4575, 0.6798 (notes B's Gil–Pelaez limits: 0.5495, 0.5145, 0.6142 and 0.2538,
0.4575, 0.6798). The values at $N=10^4$ agree as well, except where $p=1$ % means $K=100$ (the finite-$K$
deficit of §2). These runs agree with notes B's Table 10a and notes A's §10.3 within their errors. The
four regimes are confirmed: decay (Gaussian/Gaussian, Beta/Gaussian, every heavier-noise pair), a plateau
(exponential/Gaussian, $t_3$/$t_3$), and a rise to 1 ($t_3$/Gaussian). Lognormal quality (notes B only) has
$\chi=1$, but its spacing/noise ratio is 0.70 at $N=10^6$ and 1.5 only at $10^{30}$, so in the range it
behaves like a slowly drifting plateau (notes B, Table 10a).

---

## 11. Acceptance rate (item 11)

Let $z=z_\alpha$ and $w(\alpha)=P(Y>z,X<z)$, the wrong accepts per submitted paper, so $\mathrm{swap}(\alpha)=w(\alpha)/\alpha$
and $w=\alpha-P_2(z,z;\rho)$.

1. **Symmetry.** $(X,Y)\to(-X,-Y)$ and exchangeability give $w(\alpha)=w(1-\alpha)$. The count of wrong accepts
   per submission peaks at $\alpha=\tfrac12$, where it is $\tfrac14-\arcsin(\rho)/(2\pi)$.
2. **Monotonicity.** $\frac{d}{dz}P_2(z,z;\rho)=-2\phi(z)\bar\Phi(\sqrt\beta z)$ (because $P(X>z\mid Y=z)=\bar\Phi((1-\rho)z/\tau)$), and
   $dz/d\alpha=-1/\phi(z)$. So
   $$w'(\alpha)=2\Phi(\sqrt\beta\,z_\alpha)-1,$$
   which is positive for $\alpha<\tfrac12$ and decreasing in $\alpha$. So $w$ is concave with $w(0)=0$, and
   $\mathrm{swap}=w/\alpha$ (the slope of a chord from the origin) strictly decreases on $(0,1)$.
3. **Limits.** $\alpha\to0$: $\mathrm{swap}\to1$, with $1-\mathrm{swap}\approx(1+\rho)^2\phi(\sqrt\beta z)/(\tau z)$. $\alpha\to1$: $\mathrm{swap}\to0$.
4. **Why, at high reliability.** With $Y=\rho X+\tau Z$ and $\tau\to0$, the crossing mass is
   $w\approx\phi(z_\alpha)\tau E[Z^+]=\tau\phi(z_\alpha)/\sqrt{2\pi}$, so
   $$\mathrm{swap}(\alpha)\approx\frac{\tau}{\sqrt{2\pi}}\,\frac{\phi(z_\alpha)}{\alpha}=\frac{\tau}{\sqrt{2\pi}}\,h(z_\alpha).$$
   The mistakes come from papers within about $\tau$ of the bar. Per accepted paper their number is the
   hazard $h(z_\alpha)=\phi(z_\alpha)/\alpha$, which rises as $\alpha$ falls ($h(z)\approx z$ for large $z$): a thinner
   accepted set has a larger share of its members near the bar. So a more selective venue swaps a larger
   share of its accepts, although it makes fewer wrong accepts in total.
5. **Low reliability.** The tetrachoric series $P_2=p^2+\phi(z)^2\sum_{n\ge1}\rho^nHe_{n-1}(z)^2/n!$ gives
   $\mathrm{swap}\approx1-\alpha-\rho\phi(z_\alpha)^2/\alpha$.
6. **Disagreement.** $d(\alpha)$ is the swap fraction at correlation $\rho^2$: the same monotonicity; small-noise
   form $h(z_\alpha)\sqrt{1-\rho^4}/\sqrt{2\pi}$. The inconsistent share $2\alpha d=2w(\alpha;\rho^2)$ is symmetric about and
   largest at $\alpha=\tfrac12$, where it equals $\tfrac12-\arcsin(\rho^2)/\pi$. Random decisions give $d=1-\alpha$.

**Checks** (`swap_fraction`, `disagreement`, `inconsistent_share`). On a 2000-point grid of $\alpha\in(0.001,0.999)$
the swap fraction strictly decreases; $\max\lvert w(\alpha)-w(1-\alpha)\rvert=4\times10^{-16}$; $\arg\max w=0.500$.
$w'(0.2)$ by finite differences is 0.2518726 against the formula's 0.2518726 ($\rho=0.7459$). The
high-reliability form: ratio exact/approximation 1.0011 ($\alpha=0.05$) and 1.0030 ($\alpha=0.25$) at $\rho=0.99$;
1.00001 and 1.00003 at $\rho=0.9999$. Values at $\rho=0.7459$ ($\rho^2=0.5563$):

| $\alpha$ | swap | wrong accepts / submission | high-reliability approx. | disagreement $d$ | inconsistent share | random $d$ |
|---|---|---|---|---|---|---|
| 0.01 | 0.687 | 0.0069 | 0.708 | 0.840 | 0.0168 | 0.99 |
| 0.05 | 0.564 | 0.0282 | 0.548 | 0.720 | 0.0720 | 0.95 |
| 0.10 | 0.492 | 0.0491 | 0.466 | 0.640 | 0.1280 | 0.90 |
| 0.20 | 0.401 | 0.0801 | 0.372 | 0.531 | 0.2124 | 0.80 |
| 0.25 | 0.366 | 0.0914 | 0.338 | 0.488 | 0.2438 | 0.75 |
| 0.30 | 0.335 | 0.1005 | 0.308 | 0.448 | 0.2688 | 0.70 |
| 0.40 | 0.281 | 0.1122 | 0.257 | 0.377 | 0.3015 | 0.60 |
| 0.50 | 0.232 | 0.1160 | 0.212 | 0.312 | 0.3122 | 0.50 |
| 0.80 | 0.100 | 0.0801 | 0.093 | 0.133 | 0.2124 | 0.20 |

At the repository's central $\rho^2=0.5038$: swap 0.524, 0.392, 0.249 and $d$ = 0.674, 0.517, 0.332 at
$\alpha$ = 0.10, 0.25, 0.50, from the formulas of both notes (R11); the notes tabulate other values of $\rho$. The simulator's `prec_acc`,
`dis_acc` and `incons_acc` match them up to the finite-$N$ deficit of §2 (§13).

---

## 12. Discretisation (item 12)

**Why there is no closed form.**
1. A snapped review is a step function of a Gaussian:
   $P(r_{ij}=m_k\mid q)=\Phi((c_k-q)/\sigma_\varepsilon)-\Phi((c_{k-1}-q)/\sigma_\varepsilon)$ with cut points $c_k$ halfway between
   scale points. The mean of $R$ snapped reviews lives on a lattice; its law given $q$ is an $R$-fold
   convolution of these categorical laws (a sum over compositions).
2. So $(Q,S)$ is no longer bivariate normal. $E[S\mid q]$ is a smoothed staircase and $\mathrm{Var}(S\mid q)$
   depends on $q$. $P_2$ and every result of §2 to §9 lose their basis.
3. The metrics depend on $\mu_q$, $\sigma_q$, $\sigma_\varepsilon$, $R$ and the placement of the scale points separately,
   not through $\rho$ alone (§1).
4. Ties have positive probability. With random tie-breaking, $\mathrm{Top}_K(S)$ is partly a uniform draw from a
   tie class of binomial size, so the metrics are mixtures over the tie configuration. Order-statistic
   and concomitant theory for continuous variables does not apply.
5. The score is bounded above. The top of its law is a point mass (all $R$ reviews at the top point),
   not a Gaussian tail.

**What can still be said.**
1. *Fixed percentile, $N\to\infty$: an exact 1-D integral.* Let $v^\ast$ be the lattice class with
   $P(S>v^\ast)<\alpha\le P(S\ge v^\ast)$ and $f^\ast=(\alpha-P(S>v^\ast))/P(S=v^\ast)$ the accepted share of that class. A
   paper of quality $q$ is accepted with probability $a(q)=P(S>v^\ast\mid q)+f^\ast P(S=v^\ast\mid q)$, so
   $\mathrm{prec}=E[a(Q)1\{Q>q_\alpha\}]/\alpha$ and $P(\mathrm{rej}_2\mid\mathrm{acc}_1)=1-E[a(Q)^2]/\alpha$. These are free of $N$, like §2.
   Both notes checked them against the simulator (notes A: $p=1$ %, integer scale 0.2872 against 0.2861 at
   $N=10^6$; notes B: four scales at $N=5000$, within $1.9\sigma$).
2. *Fine grids act like extra noise.* For spacing $h\ll\sigma_\varepsilon$, snapping adds roughly uniform noise of
   variance $h^2/12$ per review (Sheppard's correction): $\rho^2\approx\sigma_q^2/(\sigma_q^2+\sigma_u^2+(\sigma_\varepsilon^2+h^2/12)/R)$.
   So a coarser scale needs a smaller $\sigma_\varepsilon$ to reach the same disagreement (notes B: latent $\rho^2$ 0.556
   continuous, 0.591 five-point). After per-scale recalibration, precision at the calibration rate
   matches the continuous model to $10^{-4}$; at small $p$ the scales lose 0.01–0.03, because the bar's tie
   class is a large share of the selected set.
3. *Fixed $K$, large $N$: a lottery in the top tie class.* Let $\pi_{\rm top}=E_q[P(\text{review at the top point}\mid q)^R]$.
   Once $N\pi_{\rm top}\gg K$, $\mathrm{Top}_K(S)$ is a uniform draw of $K$ papers from the $\approx N\pi_{\rm top}$ papers that every
   reviewer gave the top mark. A true top paper is in that class with probability $p_{\rm top}(Q_{(j)})^R\to1$, so
   $$\mathrm{prec}_{N,K}\approx\frac{\sum_{j\le K}E[p_{\rm top}(Q_{(j)})^R]}{N\pi_{\rm top}}\ \xrightarrow{N\to\infty}\ \frac K{N\pi_{\rm top}}\propto\frac1N,$$
   faster than the continuous $N^{-\beta}$. The crossover is at $N^\ast\approx K/\pi_{\rm top}$. More reviewers shrink
   $\pi_{\rm top}$ geometrically (all $R$ must agree), so they postpone the lottery.

**Checks.** I recomputed $\pi_{\rm top}$ ($R=4$, $\sigma_q=1.2$, $\mu_q=5$) by 1-D quadrature. Notes A's single
$\sigma_\varepsilon=2.171$: $1.18\times10^{-4}$ (int10), $3.47\times10^{-4}$ (ICLR six-point), $4.49\times10^{-4}$ (five-point), as A
reports. Notes B's per-scale calibrated $\sigma_\varepsilon$ (2.1113, 2.0827, 2.0688, 1.9974): $1.07\times10^{-4}$,
$2.52\times10^{-4}$, $3.07\times10^{-4}$, $3.71\times10^{-4}$ (int10, six, ICLR six, five), as B reports. So the two notes'
values differ only through $\sigma_\varepsilon$ (R12). The tie-class law matches the simulator where
$N\pi_{\rm top}/K\ge3$: notes B, 13 cells, largest $|z|=1.45$; notes A, five-point $N=10^6$, $K=100$: 0.0422
against $0.0431\pm0.0022$. Numbers for the study come from simulation with per-scale recalibration
(handoff §7.3).

---

## 13. Verification (item 13)

### 13.1 The layers of checking

Each result rests on a chain: tail-accurate orthant cells, then the exact finite-$N$ integrals, then the
asymptotic formulas, then the repository simulator. Each link has an independent reference.

| link | reference | result |
|---|---|---|
| `log_P2` | adaptive quadrature at thresholds up to 12 (including unequal thresholds and negative $\rho$); Owen's $T$ in the bulk; dense quadrature at 3405 random points ($h$ from 0.3 to 40, $|\rho|$ up to $1-10^{-7}$) | $10^{-9}$ in $\log P_2$; $10^{-9}$ relative in the bulk; largest error $4\times10^{-10}$ in $\log P_2$ |
| exact fixed-$K$ integral | $N=2$ and $N=3$ closed forms and 4-D orthants; $\rho=0$ ($KM/N$, up to $N=10^{50}$); own Monte Carlo at $N\le50$ (59 cells); grid refinement; both notes' tables | $10^{-13}$; $10^{-9}$; $10^{-9}$; RMS $z=0.97$; $4\times10^{-11}$; to their rounding |
| leading law, prefactor, $\beta_K$, $\beta_{K,M}$, $\omega_K$ | exact integral at $N$ up to $10^{300}$ | ratios $\to1$; $\beta_K$ and A's coefficient to 3–4 digits; $\beta_{K,M}$ leaves an $O(b_N^{-4})$ remainder |
| finite-$N$ fixed percentile | exact integral, $K=10$ to 200, $p$ from $10^{-7}$ to 0.25 | shift captured to 2–11 % ($K=10$), 0.5 % ($K=200$) |
| best paper, winner rank | $N=2$, $N=3$ orthants; Poisson route; identity with precision at $K=1$; own Monte Carlo at $N=40$; both notes' tables | $10^{-10}$; $2\times10^{-7}$; $O(K/N)$; $2\times10^{-16}$; within 4 SE; exact match |
| containment | population-bar integral against the exact integral; asymptotic miss rate | $2\times10^{-3}$ at $N=10^3$, $\le10^{-4}$ from $10^4$; 1–3 % once the miss is small |
| tails | marked-Poisson limits; 1-D fixed-percentile limits; simulator | §10.7 |
| repository simulator, Gaussian model | the exact formulas | §13.2 |

### 13.2 The repository simulator, Gaussian model

All runs use `ReviewModel(R=1, sigma_q=1, sigma_u=0, sigma_eps=sqrt(1/rho^2 - 1))`, so the standardised pair
is bivariate normal with correlation $\rho$, and `simulate(..., two_committees=True)` with fresh salts.
$z=(\text{simulator}-\text{exact})/\text{SE}$. The exact values are `precision_fixed_K`, `overlap_fixed_K`,
`containment_fixed_K` (with $M=2K$, $10K$, $\mathrm{round}(0.01N)$, $\mathrm{round}(0.05N)$, $\mathrm{round}(0.25N)$),
`rejected_given_top`, `mean_true_percentile`, `best_paper_prob`, `winner_rank_cdf`, and
`precision_pct_finite` for fixed $\alpha$ and for $K>100$.

**(a) $N=10^6$, the overlap question (notes B's open item).** 24,000 conferences at each of $\rho=0.7459$ and
$\rho=0.5$ (4 runs of 6000 each):

| $\rho$ | metric | $K=1$ | $K=5$ | $K=10$ | $K=30$ | $K=100$ |
|---|---|---|---|---|---|---|
| 0.7459 | ovl exact | 0.006805 | 0.013347 | 0.016957 | 0.024288 | 0.035682 |
| 0.7459 | ovl simulator | 0.006083 ± 0.000502 | 0.013008 ± 0.000326 | 0.016608 ± 0.000258 | 0.024064 ± 0.000178 | 0.035813 ± 0.000117 |
| 0.7459 | $z$ | −1.44 | −1.04 | −1.35 | −1.26 | +1.12 |
| 0.5 | ovl exact | 0.000124 | 0.000373 | 0.000581 | 0.001157 | 0.002446 |
| 0.5 | ovl simulator | 0.000083 ± 0.000059 | 0.000367 ± 0.000055 | 0.000588 ± 0.000049 | 0.001194 ± 0.000041 | 0.002423 ± 0.000032 |
| 0.5 | $z$ | −0.69 | −0.12 | +0.13 | +0.93 | −0.73 |

The values at different $K$ in one run are strongly correlated. At $\rho=0.7459$, $K=10$, the relative
error is $-2.1\pm1.5$ %; notes B's pooled deficit of $-7.7$ % is excluded at $3.7\sigma$, and B's $\rho=0.5$
deficit ($K=30$, $z=-2.5$) is not reproduced ($z=+0.93$). The same draws give precision, containment in
the top $2K$, second-committee rejection and the best-paper probability: 46 distinct cells, mean
$z=-0.23$, RMS $z=0.95$, largest $|z|=2.73$ (`prec_K100`, $\rho=0.5$; 3 cells beyond 2). So the simulator's
overlap at $N=10^6$ agrees with the exact law. A deficit of about 2 % at $\rho=0.7459$ is still within the
error (open issue 6).

**(b) $N=10^3$, $10^4$, $10^5$, every metric at $\rho=0.7459$.** 40,000, 10,000 and 2,000 conferences. After
removing exact duplicates (for example `c2x_K5` = `c1pct_K5` at $N=1000$): 239 cells, mean $z=-0.25$,
RMS $z=1.17$, $|z|>2$ in 9.7 % and $|z|>3$ in 0.8 % (one quantity: `dis_acc0.10` at $N=10^5$, $z=+3.24$, and its
copy `incons_acc0.10`). The cells of one run are correlated (precision-like metrics move together), so
the table holds far fewer independent tests than cells. I reran every cell beyond $|z|=2$ that had an
independent quantity with fresh salts (100,000, 40,000 and 10,000 conferences at $N=10^3$, $10^4$, $10^5$):
30 cells, mean $z=+0.23$, RMS $z=1.06$, largest 2.09. The flagged cells moved to: `prec_acc0.10` at $10^5$:
$-2.97\to-0.76$; `dis_acc0.10` at $10^5$: $+3.24\to+0.87$; `prec_K10` at $10^4$: $-2.39\to+1.21$; `prec_K5` at
$10^4$: $-2.10\to+2.00$; `best_in_K30` at $10^4$: $-2.13\to+1.05$; `prec_K100` at $10^3$: $-2.05\to-0.62$. So the
first excursions were chance. Error sizes (handoff §6.13): for the 137 fixed-$K$ cells the median relative
error is 0.15 %, and 2.0 % at most among cells whose relative SE is below 1 %; larger relative errors (up to
26 %) occur only in rare-hit cells whose relative SE is of the same size. For the fixed-$\alpha$ quantities
(63 cells) the median absolute error is $4\times10^{-5}$ and the largest $4\times10^{-4}$; for the fixed-$p$
quantities (24 cells) $1.8\times10^{-4}$ and $9\times10^{-4}$.
`corr_qs` and `corr_s12` agree with $\rho$ and $\rho^2$ (after the small-sample bias $-\rho(1-\rho^2)/(2N)$) to
$|z|\le1.6$. Winner rank: the exact cdf at the simulator's per-run quartiles is 0.24–0.28, 0.49–0.54 and
0.70–0.77 (targets 0.25, 0.50, 0.75; 12 runs).

**(c) The finite-$N$ deficit at fixed $\alpha$.** With 100,000 conferences at $N=10^3$, the simulator gives
`prec_acc0.10` $=0.507715\pm0.000130$ against the exact finite-$N$ value 0.507791 ($z=-0.59$) and the $N$-free
value 0.508587 ($z=-6.7$). So the $O(1/K)$ deficit of §2 is real, it has the predicted size, and the
simulator reproduces it. Notes B's fresh runs show the same (RMS $z=1.05$ against exact, 4.5 against the
$N$-free values), and so do notes A's.

**(d) In the test suite.** `tests/test_analytic.py::test_simulator_matches_exact_fixed_K` runs the
simulator at $N=2000$ (2000 conferences) and checks nine metrics against the exact formulas within 4.5 SE.

**Previous comparisons.** Notes A: 629 simulator-vs-formula comparisons, mean $z=-0.005$, SD 0.996. Notes
B: 2119 cells, RMS $z=1.09$ (1.045 without the fixed-$\alpha$ cells compared with $N$-free limits). Both
agree with the results above.

### 13.3 The repository code

* `model.py`, `simulate.py`, `calibrate.py`: read, not edited. **No bug found.** Every simulator metric
  matches its exact value, including finite-$N$ effects of size $10^{-3}$ and the overlap at $N=10^6$.
  Notes B's replay of `simulate_chunk` (seeds 0–59) reproduced the overlap to the last digit.
* `calibrate.py`, two remarks (not bugs). (i) `NEURIPS2014_RAW` and `NEURIPS2021` use the mean of the
  two committees' acceptance counts (43.5/166; 200.5/764), while the formula assumes equal counts; solving
  with the actual counts moves $r_{12}$ by $+0.0001$ and $+0.0007$. (ii) `CENTRAL_TARGET` is the
  decided-papers target ($\rho^2=0.5038$), while both derivation notes used $\rho^2=0.5563$ (all 882 papers).
* `analytic.P2` (Owen's $T$, Part 1, unchanged) has an absolute error of about $10^{-16}\bar\Phi(\min(a,b))$. Its
  relative accuracy is lost when $P_2\ll10^{-7}\bar\Phi(\min(a,b))$: `P2(11, 3, 0.7)` returns $-1.4\times10^{-18}$ (true
  $1.9\times10^{-28}$); `P2(9, -2, 0.6)` returns 0 (true $1.1\times10^{-19}$); notes A report 8 % error at $(12,11;0.5)$. In the
  study range (thresholds up to 4.8) the error is below $10^{-11}$. Part 2 uses `log_P2` / `P2_tail`.
* scipy's `bdtr` fails for $n\gtrsim10^9$; Part 2 uses log-space sums and `betaincc` instead.
* Fixes after review of `analytic.py`. (i) `P2_diag` and `precision_pct` in the far tail (§2.1). (ii) `log_P2` with
  $\rho<0$ and both thresholds below 3 used Owen's $T$ alone, so tiny values became $-\infty$ (`log_P2(2.9, 2.9, -0.9)`
  was $-\infty$, true $-91.86$; `log_P2(2.0, -1.0, -0.99)` was 1.3 % off), and the function jumped at $h=3$. It now uses
  the tail integral there; the five cases quoted in review agree with dense quadrature to $10^{-13}$ in $\log P_2$.
  (iii) The ridge grid for $|\rho|>0.95$ (§4.1). (iv) Edge cases: $K=0$ raises ValueError (an empty selection has no
  precision); $M=0$ gives 0 and $A=0$ gives rejection 1; $|\rho|=1$ gives the closed values; `Phi2` and `P2` with
  infinite thresholds reduce to the margins; `precision_pct_finite` gives 1 at $K=N$, NaN at $K=0$, and 1 at $\rho=1$;
  `invert_disagreement` brackets $[-1,1]$, so $d=0$ gives $r_{12}=1$; `expected_kth_best` with $K>N$ raises; the power
  form of `winner_rank_median_asymptotic` raises for $\rho\le0$ (the semi form gives $N/2$ at $\rho=0$). (v) The
  docstring of `precision_fixed_K_asymptotic` now uses the $C_K$ of §4.3 (R4a). None of these changes a value in the
  study range: `scripts/verify_analytic.py`, rerun on the same simulations with every analytic value recomputed,
  gives 3885 analytic values that differ from the previous ones by at most $2.2\times10^{-16}$, and every $z$ by at
  most $4\times10^{-11}$.
* The simulator's SE is the sample SE over conferences. For rare-hit metrics (overlap at $\rho=0.5$,
  $N=10^6$) it can be zero or too small, so a $z$ from it overstates the deviation. A $z$ with the exact
  variance $\sqrt{p(1-p)/(Kn)}$ is the robust check; in (a) the two agree to 0.1.
* The `analytic.py` module docstring refers to `docs/derivations.md`; this file now exists.

---

## 14. Open issues

1. **The asymptotic series is poor in range.** The first-order law $1+\beta_K/b_N^2+\omega_K\varepsilon_N$ is right
   asymptotically but worse than the leading law at $N\le10^6$ for $\rho\ge0.75$ (it turns negative at $N=10^3$,
   $\rho=0.9$). Use the exact integral, or the hybrid $R_KP_2(z,z)/(K/N)$, in the range.
2. **The finite-$N$ fixed-percentile closed form** has a relative error $O(K^{-2})$: 2–11 % of the shift at
   $K=10$, and $-1$ % of the value at $K=3$ (§2.3). For $K<10$ use the exact integral; for $K<30$ do not use the
   $N$-free limit.
3. **Calibration target.** The derivations used $\rho^2=0.5563$; `calibrate.CENTRAL_TARGET` gives 0.5038.
   Resolved: the study uses 0.5038 as the central level (REPORT.md section 8.2; `results/calibration_levels.csv`). The checks here keep the notes' 0.5563 as a reference setting; this document reports both where it matters.
4. **Tails.** No sharp constant for Beta/Gaussian beyond $(K/N)(\log N)^{a/2}$. The $t_3$/Gaussian first-order
   deficit law is an upper bound in the range and sharp only from about $N=10^6$ at $K=10$. $t_3$/$t_3$
   approaches its plateau slowly (0.65–0.69 at $N=10^5$ against $w=0.709$). The lognormal limit 1 is out of
   reach in any realistic range.
5. **Discretisation.** The crossover between the continuous regime and the tie-class lottery
   ($N\pi_{\rm top}/K$ between about 0.7 and 3) has no formula; use simulation there.
6. **Overlap at $N=10^6$.** Consistent with exact at $1.35\sigma$, but 24,000 conferences cannot exclude a
   2 % deficit at $\rho=0.7459$. Each further 24,000 conferences cuts the SE by a factor $\sqrt2$.
7. **`analytic.P2`** keeps its far-tail limit (§13.3). It is harmless in the study range; new code should use
   `log_P2`.
8. **$\rho<-0.95$.** The ridge grid integrates $w$ over $[-12,12]$. Its absolute error is below about $10^{-30}$,
   but a value far below that comes back as 0 (for example `precision_fixed_K(1e6, 1, -0.96)`, whose true value is
   about $5\times10^{-197}$ by the product grid). Negative $\rho$ does not occur in the study.
9. **First-order laws in range.** The first-order laws for precision and for $P_{\rm best}$ are worse than the leading
   law at $N\le10^6$ for $\rho\ge0.75$ and can be negative there (§4.4, §7).

---

## Appendix: where each result lives in `analytic.py`

| item | functions |
|---|---|
| 1 | `rho2`, `committee_corr`, `rho2_limit`, `sigma_eps_for_rho2`, `spearman_brown` (Part 1) |
| 2 | `precision_pct`, `swap_fraction` (Part 1); `precision_pct_finite`; `precision_fixed_K` with $M=K=\mathrm{round}(pN)$ |
| 3 | `disagreement`, `inconsistent_share`, `invert_disagreement`, `invert_inconsistent` (Part 1); `rejected_given_top`, `precision_fixed_K(N, A, r12)` for finite $N$ |
| 4 | `precision_fixed_K`, `precision_fixed_K_asymptotic(order=0/1, form="bN"/"logN")`, `b_N`, `log_eps_N`, `beta_K`, `omega_K`, `finite_K_factor`, `precision_fixed_K_hybrid`, `local_loglog_slope(method="exact"/"leading")` |
| 5 | `expected_kth_best`, `conditional_quality_mean`, `conditional_quality_sd`, `true_topK_threshold`, `mechanism_gap` |
| 6 | `containment_fixed_K`, `containment_limit`, `containment_miss`, `containment_miss_asymptotic`, `containment_fixed_K_asymptotic`, `beta_KM`, `omega_KM`, `mean_true_percentile` |
| 7 | `best_paper_prob(method="exact"/"poisson")`, `best_paper_prob_asymptotic(order=0/1)` (with `beta_KM(K, 1, rho)`, `omega_KM(K, 1, rho)`) |
| 8 | `winner_rank_cdf`, `winner_rank_quantile`, `winner_rank_median_asymptotic(form="semi"/"power")` |
| 9 | `overlap_fixed_K`, `rejected_given_top`; `containment_fixed_K(N, 3, M, rho2)` for the tier sets |
| tail-accurate helpers | `log_P2`, `P2_tail` |

Every finite-$N$ function accepts a scalar or an array of $N$, and works for $N$ up to $10^{300}$ and $K/N$
down to $10^{-7}$ and below.
