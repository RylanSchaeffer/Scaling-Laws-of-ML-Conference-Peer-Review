# Derivations for handoff §6 (Gaussian model) — notes A

Independent derivation of every item of handoff §6. Each result comes with its derivation and
with the numerical checks that were run. Most effort is on items 4 to 10.

Reusable code (not part of the package):
`/private/tmp/claude-501/-Users-rylanschaeffer-Documents-Scaling-Laws-of-ML-Conference-Peer-Review/7d0174d6-f884-4f59-93ea-00d3f8717415/scratchpad/deriver_a/`

| file | content |
|---|---|
| `core.py` | exact finite-N integrals (precision, containment, best paper, winner rank), asymptotic laws, robust bivariate tail `P2` |
| `tails.py` | non-Gaussian shapes: noise survival function of the mean of R t3 errors, fixed-percentile limits, plateau formulas, a general independent-Poisson approximation |
| `discrete.py` | snapped scores: exact large-N fixed-percentile limit, top-cell lottery |
| `t_*.py` | the checks quoted below; their outputs are the `t_*.out` files |
| `sim_gauss.py`, `sim_tails.py`, `sim_discrete.py` | repository-simulator runs (`*.jsonl`) |
| `compare_sim.py` | simulator against exact formulas (`compare_sim2.md`) |

Run any script as `uv run --project <repo> python <script>` from that folder.

---

## 0. Summary of results

Notation (used throughout): $X = Q^\ast$ (quality), $Y = S^\ast$ (score), standard bivariate normal
with correlation $\rho$; $\tau=\sqrt{1-\rho^2}$; $\kappa=\rho/(1+\rho)$; $\beta=(1-\rho)/(1+\rho)=1-2\kappa$;
$\bar\Phi = 1-\Phi$; Mills ratio $R(x)=\bar\Phi(x)/\phi(x)$; $B_N=\bar\Phi^{-1}(1/N)$ (so
$B_N^2 = 2\log N-\log(4\pi\log N)+o(1)$); $Q_K(\lambda)=P(\mathrm{Pois}(\lambda)\le K-1)$;
$P_2(a,b;r)=P(X>a,Y>b)$ for correlation $r$.

| item | result |
|---|---|
| 1 | $\rho^2=\sigma_q^2/(\sigma_q^2+\sigma_u^2+\sigma_\varepsilon^2/R)$; two committees with $u$ redrawn: $r_{12}=\rho^2$; $\rho^2\to\sigma_q^2/(\sigma_q^2+\sigma_u^2)$ as $R\to\infty$. Spearman–Brown on inter-review correlation gives $(\sigma_q^2+\sigma_u^2)/(\sigma_q^2+\sigma_u^2+\sigma_\varepsilon^2/R)\ge\rho^2$. |
| 2 | $N\to\infty$: $\mathrm{prec}(p)=P_2(z_p,z_p;\rho)/p$, no $N$. Finite $N$, $K=\mathrm{round}(pN)$, $p_K=K/N$: $\mathrm{prec}=P_2(z_{p_K},z_{p_K})/p_K-(1-p_K)\,g\,(\rho-\varphi_I)/N+O(N^{-2})$, $g=\phi(\sqrt\beta z)/(\tau\phi(z))$, $\varphi_I=(P_2-p^2)/(p(1-p))$. Relative size $-\rho/((1+\rho)^2K)$ for small $p$. |
| 3 | $d(\alpha)=1-P_2(z_\alpha,z_\alpha;r_{12})/\alpha$; inconsistent share $=2\alpha d$; $\partial d/\partial r_{12}=-\phi_2(z_\alpha,z_\alpha;r_{12})/\alpha<0$, so the inverse is unique; at $\alpha=1/2$: $d=\tfrac12-\arcsin(r_{12})/\pi$. |
| 4 | Exact: $\mathrm{prec}_{N,K}=\frac NK\,E\,P_2(T_X,T_Y;\rho)$, $T_X,T_Y$ = K-th largest quality and score among the other $N-1$ papers (a 2D integral with a multinomial weight). Limit 0 for every $\rho<1$. Leading law: $\mathrm{prec}_{N,K}\sim C_K(\rho)\,e^{\kappa B_N^2}/N\sim C_K(\rho)\,N^{-\beta}(4\pi\log N)^{-\kappa}$, $C_K=(1+\rho)^2\Gamma(K+1-\kappa)^2/(K\tau\Gamma(K)^2)$. Next corrections: relative $-\rho\sigma_K^2/(\tau^2B_\ast^2)=O(1/\log N)$ and $+\Delta$ of relative order $N^{-\beta}(\log N)^{-\kappa}$. Practical formula, error $\le0.6\%$ for $K\ge10$ and $\le2.5\%$ for $K=1$, $\rho\le0.75$, over $N=10^3$–$10^{12}$: $\mathrm{prec}_{N,K}\approx F_K\,P_2(z,z;\rho)/(K/N)$, $z=\bar\Phi^{-1}(K/N)$, $F_K=[\Gamma(K+1-\kappa)/(\Gamma(K)K^{1-\kappa})]^2$. Local slope over $10^3$–$10^6$ is $1.1\times$ ($\rho=0.5$) to $1.7\times$ ($\rho=0.9$) the asymptotic slope $-\beta$. |
| 5 | $X$ given $Y=y$ is $N(\rho y,\tau^2)$. The top scores sit at $\approx B_N$, so their qualities sit at $\rho B_N\pm\tau$; the true top K sit at $\approx B_N$. The gap $(1-\rho)B_N$ grows like $\sqrt{2\log N}$ while the spread $\tau$ stays fixed; in SD units the gap is $\sqrt\beta\,B_N$, which gives $N^{-\beta}$. Fixed percentile: both thresholds stay at $z_p$; nothing grows. |
| 6 | Share of $\mathrm{Top}_K(S)$ in the true top $p$ (fixed $p$) $\to1$. Deficit $\approx\frac1K\sum_i\bar\Phi((\rho E Y_{(i)}-z_p)/\tau)$, of order $N^{-\rho^2/(1-\rho^2)}e^{(\rho z_p/\tau^2)\sqrt{2\log N}}$ times powers of $\log N$. Share in the true top $M=cK$ $\to0$ like $N^{-\beta}$. |
| 7 | $P_{\rm best}=N\!\int\!\!\int\phi_2\,\Phi(x)^{N-1}P(\mathrm{Bin}(N-1,\pi)\le K-1)$, $\pi=(\bar\Phi(y)-P_2(x,y))/\Phi(x)$. The handoff's Poisson($\lambda$) version differs by at most $6\times10^{-4}$ (relative) at $N=10^3$ and $6\times10^{-7}$ at $10^6$. Leading law $P_{\rm best}\sim\Gamma(1-\kappa)(1+\rho)\Gamma(K+1-\kappa)/(\tau\Gamma(K))\cdot e^{\kappa B_N^2}/N$, same rate $N^{-\beta}$; $K$-dependence $\propto\Gamma(K+1-\kappa)/\Gamma(K)\sim K^{1/(1+\rho)}$. |
| 8 | Median true rank of the top-scored paper $\approx N\bar\Phi(\rho(B_N+\gamma_E/B_N))\approx(e^{-\gamma_E\rho^2}/\rho)\,(N/(\sqrt{2\pi}B_N))^{1-\rho^2}$: grows like $N^{1-\rho^2}$. Log-rank is close to normal with SD $\approx\rho\tau B_N$. Mean rank grows faster, like $N^{2(1-\rho^2)/(2-\rho^2)}$. |
| 9 | Overlap$(N,K,\rho)$ = Precision$(N,K,\rho^2)$ exactly, at every N and K: rate $N^{-(1-\rho^2)/(1+\rho^2)}$, faster than precision. |
| 10 | Governed by the tail dependence of (quality, score). Gaussian/Gaussian: $\to0$ like $N^{-\beta}$. Exponential/Gaussian: plateau (0.539, 0.604, 0.616 for K=1, 10, 100 at $\rho^2=0.5$; $\to\chi=2\bar\Phi(\sigma_n/2\sigma_q)$ as K grows). t3/Gaussian: $\to1$, deficit $\propto N^{-1/3}$. t3/t3: plateau $w=1/(1+(\sigma_\varepsilon/\sigma_q)^3/R^2)$ (0.634) for every K. Beta/Gaussian: $\to0$ like $(K/N)\,\mathrm{polylog}(N)$. Any quality with t3 noise except t3 quality: collapse to $\approx K/N$. Fixed-percentile precision is N-free for every shape. |
| 11 | Wrong accepts per paper $w(\alpha)=\alpha s(\alpha)$ satisfy $w(\alpha)=w(1-\alpha)$ and $w'(\alpha)=2\Phi(\sqrt\beta z_\alpha)-1$, so $w$ is concave and $s=w/\alpha$ strictly decreases in $\alpha$. High reliability: $s\approx\tau\phi(z_\alpha)/(\sqrt{2\pi}\alpha)$. The same holds for the disagreement with $\rho\to\rho^2$; the inconsistent share is largest at $\alpha=1/2$. |
| 12 | No closed form in $\rho$: the score is a lattice variable with a q-dependent multinomial law, bounded above, with ties. Exact large-N fixed-percentile limit is a 1D integral (checked). Fine grids act like extra noise $h^2/12$ per review. Fixed K at large N becomes a lottery among the papers tied at the top score: $\mathrm{prec}\approx\bar p_{\rm top}K/(N\pi_{\rm top})\propto1/N$. |
| 13 | 629 simulator-vs-formula comparisons: mean z −0.005, SD 0.996, 4.8% beyond 2 SE; every case beyond 3 SE was rerun or recomputed and agrees (§13). No bug found in `model.py`, `simulate.py`, `calibrate.py`. |

---

## 1. Reliability (item 1)

**Derivation.** $\bar s_i=q_i+u_i+\bar\varepsilon_i$ with $\mathrm{Var}(\bar\varepsilon_i)=\sigma_\varepsilon^2/R$. So
$\mathrm{Var}(\bar s)=\sigma_q^2+\sigma_u^2+\sigma_\varepsilon^2/R$ and $\mathrm{Cov}(\bar s,q)=\sigma_q^2$. Hence

$$\rho^2=\frac{\sigma_q^2}{\sigma_q^2+\sigma_u^2+\sigma_\varepsilon^2/R}.$$

Two committees: $\bar s^{(k)}=q+u^{(k)}+\bar\varepsilon^{(k)}$. With $u$ redrawn, $\mathrm{Cov}=\sigma_q^2$, so
$r_{12}=\rho^2$. With $u$ shared, $r_{12}=(\sigma_q^2+\sigma_u^2)/(\sigma_q^2+\sigma_u^2+\sigma_\varepsilon^2/R)>\rho^2$.
As $R\to\infty$, $\rho^2\to\sigma_q^2/(\sigma_q^2+\sigma_u^2)$; with $\sigma_u=0.5$, $\sigma_q=1.2$ this bound is $0.852$.

Two reviews of one paper correlate at $r_1=(\sigma_q^2+\sigma_u^2)/(\sigma_q^2+\sigma_u^2+\sigma_\varepsilon^2)$. Spearman–Brown gives
$Rr_1/(1+(R-1)r_1)=(\sigma_q^2+\sigma_u^2)/(\sigma_q^2+\sigma_u^2+\sigma_\varepsilon^2/R)$. This is the
shared-$u$ committee correlation, not $\rho^2$: it treats $u$ as signal. So a Spearman–Brown value is an
upper bound on $\rho^2$ when $\sigma_u>0$.

**Which metrics depend only on $\rho$.** In the continuous Gaussian model,
$(X,Y_1,Y_2)$ with $Y_k=\rho X+\tau Z_k$, $Z_1\perp Z_2$ (u redrawn), is a function of $\rho$ alone.
Every metric of §4 is a function of the ranks of $(X,Y_1,Y_2)$, so it depends on
$(\sigma_q,\sigma_\varepsilon,R,\sigma_u)$ only through $\rho$. Exceptions: (a) shared $u$ for the second committee
(two parameters $\rho$, $r_{12}$); (b) $t_3$ noise (the mean of $R$ $t_3$ errors has an R-dependent shape; §10
shows a plateau that depends on $R$ at fixed $\rho$); (c) snapped scores (depend on $\sigma_\varepsilon$, $R$, grid
and $\mu_q$ separately). Non-Gaussian quality with Gaussian noise depends on (shape, $\rho$) only.

**Checks** (`t_items123.out`, 400,000 papers per line):

| $\sigma_\varepsilon$, R, $\sigma_u$ | $\rho^2$ formula | sim corr$(q,\bar s)^2$ | $r_{12}$ formula | sim | shared-u $r_{12}$ formula | sim |
|---|---|---|---|---|---|---|
| 1.5, 3, 0 | 0.6575 | 0.6574 | 0.6575 | 0.6578 | 0.6575 | 0.6568 |
| 2.0, 4, 0.5 | 0.5353 | 0.5342 | 0.5353 | 0.5371 | 0.6283 | 0.6295 |
| 2.5, 50, 0.5 | 0.7934 | 0.7921 | 0.7934 | 0.7923 | 0.9311 | 0.9311 |

Spearman–Brown at $(\sigma_\varepsilon,R,\sigma_u)=(2,4,0.5)$: 0.6283, equal to the shared-$u$ correlation, while $\rho^2=0.5353$.
`analytic.rho2`, `committee_corr`, `rho2_limit`, `sigma_eps_for_rho2`, `spearman_brown` are correct.

---

## 2. Fixed-percentile precision (item 2)

### 2.1 Large-N limit

Let $z_p=\bar\Phi^{-1}(p)$. By the law of large numbers the empirical $\mathrm{round}(pN)$-th largest score and
quality converge to $z_p$. The selected set tends to $\{Y>z_p\}$ and the true top set to $\{X>z_p\}$. So

$$\mathrm{prec}_\infty(p)=\frac{P_2(z_p,z_p;\rho)}{p},\qquad \mathrm{swap}(\alpha)=1-\frac{P_2(z_\alpha,z_\alpha;\rho)}{\alpha}.$$

$P_2(a,a;r)=\bar\Phi(a)-2T(a,\sqrt{(1-r)/(1+r)})$ (Owen's T), as in `analytic.P2_diag`.

### 2.2 Exact finite N

The exact representation of §4.1 holds for any K. Write $U=\bar\Phi(X)$, $V=\bar\Phi(Y)$ (uniform),
$H(u,v)=P(U\le u,V\le v)=P_2(\bar\Phi^{-1}(u),\bar\Phi^{-1}(v);\rho)$. Then

$$\mathrm{prec}_{N,K}=\frac NK\,E\,H(\hat U,\hat V),$$

where $\hat U$, $\hat V$ are the K-th smallest $U$ and $V$ among the other $n=N-1$ papers (§4.1).
Expand around $p_K=K/N$. Exact facts: $E\hat U=K/(n+1)=p_K$ (uniform order statistic). By the Bahadur
representation $\mathrm{Var}\hat U\approx p(1-p)/N$ and $\mathrm{Cov}(\hat U,\hat V)\approx(H(p,p)-p^2)/N$.
The first-order term vanishes exactly. Second order:

$$E H(\hat U,\hat V)=H+H_{uu}\mathrm{Var}\hat U+H_{uv}\mathrm{Cov}(\hat U,\hat V)+O(N^{-2}).$$

Derivatives: $H_u(u,v)=P(V\le v\mid U=u)=\bar\Phi((y-\rho x)/\tau)$;
$H_{uu}=-(\rho/\tau)\phi((y-\rho x)/\tau)/\phi(x)$; $H_{uv}=c(u,v)$, the copula density. At $x=y=z$:
$H_{uu}=-\rho g$, $H_{uv}=g$, with $g=\phi(\sqrt\beta z)/(\tau\phi(z))$ (because $(1-\rho)z/\tau=\sqrt\beta z$). So

$$\boxed{\mathrm{prec}_{N,K}=\frac{H(p_K,p_K)}{p_K}-\frac{(1-p_K)\,g\,(\rho-\varphi_I)}{N}+O(N^{-2}),\quad \varphi_I=\frac{H-p_K^2}{p_K(1-p_K)}.}$$

$\varphi_I$ is the correlation of the two selection indicators; $\varphi_I<\rho$, so the correction is negative.
For small $p$, $H/p\approx(1+\rho)^2\phi(\sqrt\beta z)/(\tau z)$ and $z/\phi(z)\approx1/p$, so the relative
correction is $-\rho/((1+\rho)^2K)=-\kappa(1-\kappa)/K$. This equals the large-K expansion of the factor
$F_K$ of §4.6, found by a different route.

**Answer.** The expected precision depends on N only through $K=\mathrm{round}(pN)$ and through an $O(1/N)$
term (relative size $\approx\kappa(1-\kappa)/K$ at small p). Rounding changes $p$ to $p_K$ by at most $1/(2N)$.
The swap fraction is $1-\mathrm{prec}$ with $p=\alpha$; at $\alpha=0.25$, $N\ge1000$ the correction is
below $10^{-3}$.

**Checks** (exact multinomial integral of §4 against the formula, `t_items123.out`):

| N | K | $\rho$ | exact | $H/p_K$ | exact $-H/p_K$ | formula | tail form |
|---|---|---|---|---|---|---|---|
| 100 | 25 | 0.75 | 0.634166 | 0.637295 | −0.003130 | −0.003219 | −0.006243 |
| 200 | 40 | 0.5 | 0.434566 | 0.435753 | −0.001186 | −0.001201 | −0.002421 |
| 400 | 20 | 0.9 | 0.631979 | 0.637355 | −0.005376 | −0.005530 | −0.007945 |
| 1000 | 10 | 0.75 | 0.310560 | 0.317065 | −0.006505 | −0.006695 | −0.007765 |
| 5000 | 50 | 0.75 | 0.315734 | 0.317065 | −0.001331 | −0.001339 | −0.001553 |

The formula captures 97 to 99 percent of the finite-N shift. In the simulator, $\alpha=0.10$, $\rho=0.9$,
$N=1000$: swap 0.31240 ± 0.00036 against the N-free value 0.31135 (+2.9 SE) and the exact finite-N value 0.31245
(−0.1 SE).
`P2_diag` agrees with adaptive quadrature to $10^{-11}$ relative for $a\le6$.

---

## 3. Two-committee disagreement (item 3)

$(Y_1,Y_2)$ is standard bivariate normal with correlation $r_{12}$ ($=\rho^2$ with $u$ redrawn). Both committees
accept $\alpha N$. By §2 with $\rho\to r_{12}$:

$$d(\alpha,r_{12})=P(\mathrm{rej}_2\mid\mathrm{acc}_1)=1-\frac{P_2(z_\alpha,z_\alpha;r_{12})}{\alpha},\qquad
I(\alpha,r_{12})=P(\mathrm{acc}_1,\mathrm{rej}_2)+P(\mathrm{rej}_1,\mathrm{acc}_2)=2(\alpha-P_2)=2\alpha d.$$

**Inverse.** Plackett's identity $\partial P_2(a,a;r)/\partial r=\phi_2(a,a;r)>0$ gives
$\partial d/\partial r_{12}=-\phi_2(z_\alpha,z_\alpha;r_{12})/\alpha<0$. So $d$ is strictly decreasing and the inverse
is unique (bracketing root search). Then $\rho^2=r_{12}$ and
$\sigma_\varepsilon=\sqrt{R(\sigma_q^2/\rho^2-\sigma_q^2-\sigma_u^2)}$. Error propagation: $\delta r_{12}=-\alpha\,\delta d/\phi_2$.
Closed form at $\alpha=1/2$: $P_2(0,0;r)=1/4+\arcsin(r)/(2\pi)$, so $d=1/2-\arcsin(r)/\pi$ and $r=\cos(\pi d)$.
Random decisions ($r=0$): $d=1-\alpha$, $I=2\alpha(1-\alpha)$ (35.1 percent at $\alpha=0.227$, as reported).

**Checks.** $\alpha=1/2$ closed form: agreement to $10^{-16}$ for $r\in\{0.2,0.5,0.8\}$; $\cos(\pi d)$
returns $r$. Inversions (N-free formula; `t_items123.out`):

| experiment | $\alpha$ | inconsistent | $d$ | $r_{12}=\rho^2$ | $\rho$ |
|---|---|---|---|---|---|
| NeurIPS 2014 raw table | 0.2620 | 0.2590 | 0.4943 | 0.5265 | 0.7256 |
| NeurIPS 2014 quoted | 0.2250 | 0.2590 | 0.5756 | 0.4362 | 0.6604 |
| NeurIPS 2021 | 0.2270 | 0.2302 | 0.5070 | 0.5563 | 0.7459 |

Finite-N bias of the inversion (exact integral of §4 at the experiment's N): at N=166, A=44 the exact
disagreement at fixed $r_{12}$ is 0.0012 above the N-free value at $\alpha=44/166$; by
$\delta r_{12}=\alpha\,\delta d/\phi_2$ this moves the inverted $r_{12}$ by about +0.002. At N=882, A=200 the shift in
$d$ is +0.0003 and the root search on the exact law moves $r_{12}$ from 0.5563 to 0.5571. Both are far below
the binomial uncertainty of the experiments (§7.1 of the handoff). `analytic.disagreement`, `inconsistent_share`,
`invert_disagreement`, `invert_inconsistent` are correct.

---

## 4. Fixed-number precision (item 4)

### 4.1 Exact finite-N representation (order statistics and concomitants)

Let $I=|\mathrm{Top}_K(Y)\cap\mathrm{Top}_K(X)|$. By exchangeability $E I=N\,P(\text{paper 1 in both sets})$.

*Concomitant form.* Order the scores, $Y_{(1)}>\dots>Y_{(N)}$, and let $X_{[i]}$ be the quality of the paper
with the i-th largest score (its concomitant). Given the scores, $X_{[i]}=\rho Y_{(i)}+\tau W_i$ with
$W_i$ iid $N(0,1)$, independent of the scores. So $EI=\sum_{i\le K}P(X_{[i]}\ge X_{(K)})$. Each term
conditions on the i-th score (density of an order statistic), on the concomitant law, and on the other
papers' qualities. Summing over $i$ collapses the order-statistic densities into one paper-centred form:

*Paper-centred form.* Condition on paper 1's $(x,y)$. Let $T_X$, $T_Y$ be the K-th largest quality and the
K-th largest score among the other $n=N-1$ papers. Paper 1 is in both sets iff $x>T_X$ and $y>T_Y$.
$(T_X,T_Y)$ is independent of paper 1, so

$$\boxed{\mathrm{prec}_{N,K}=\frac NK\;E\big[P_2(T_X,T_Y;\rho)\big]=\frac NK\int\!\!\int\phi_2(x,y;\rho)\,G(x,y)\,dx\,dy,}$$

$$G(x,y)=P(T_X<x,\;T_Y<y)=P(A\le K-1,\;B\le K-1),$$

where $A$ ($B$) counts the other papers with score above $y$ (quality above $x$). The counts come from a
multinomial over four cells with probabilities $p_{11}=P_2(x,y)$, $p_{10}=\bar\Phi(x)-p_{11}$ (only quality
above), $p_{01}=\bar\Phi(y)-p_{11}$ (only score above). With $A=n_{11}+n_{01}$, $B=n_{11}+n_{10}$:

$$G=\sum_{j=0}^{K-1}\mathrm{Bin}(j;n,p_{11})\sum_{a=0}^{K-1-j}\mathrm{Bin}\Big(a;n-j,\tfrac{p_{01}}{1-p_{11}}\Big)\,
F_{\rm Bin}\Big(K-1-j;\,n-j-a,\,\tfrac{p_{10}}{1-p_{11}-p_{01}}\Big).$$

The same formula with the quality cap $K$ replaced by $M$ gives the share of $\mathrm{Top}_K(Y)$ in the true
top M (used in §6).

*Vectorised evaluation* (`core.precision_exact`). Substitute $u=\bar\Phi(x)$, $v=\bar\Phi(y)$:
$\phi_2\,dx\,dy=c(u,v)\,du\,dv$ with the Gaussian copula density $c$. Integrate over $s=\log(nu)$, $t=\log(nv)$
on composite Gauss–Legendre nodes with breakpoints near the Poisson cut at $K\pm4\sqrt K$ (16 nodes per
segment, 11 segments, lower limit $nu=e^{-46}$). Per grid one incomplete-beta call is made for each $j$; the
inner sum uses the exact recursion $F_{M-1}(m)=F_M(m)+\pi f_{M-1}(m)$ for binomial cdfs. Binomial pmfs use
$\log\binom nk=\sum_{i<k}\log(n-i)-\log k!$, which is stable for $n$ up to $10^{300}$. For $N>10^7$ the
binomial cdf is replaced by the Poisson cdf (error $O(K^2/N)$). Quadrature converges: values with 12, 16,
24 and 32 nodes per segment agree to $10^{-10}$ (`t_conv.out`).

**Checks of the exact formula.**

* $N=2$, $K=1$: precision $=P(\text{concordant pair})=1/2+\arcsin(\rho)/\pi$. Integral: 0.5969866832 vs
  0.5969866840 ($\rho=0.3$); 0.8564337454 vs 0.8564337069 ($\rho=0.9$).
* $N=3$, $K=1$: $3P(X_1>X_2,X_1>X_3,Y_1>Y_2,Y_1>Y_3)$, a 4-dim orthant (scipy, tolerance $10^{-10}$):
  0.44735091 vs 0.44735088 ($\rho=0.3$), 0.79081824 vs 0.79081832 ($\rho=0.9$).
* Brute-force Monte Carlo, 400,000 conferences: (N,K,ρ) = (5,2,0.7): 0.67504 vs 0.67463 ± 0.00045;
  (8,3,0.5): 0.56768 vs 0.56734 ± 0.00037; (20,4,0.8): 0.62667 vs 0.62658 ± 0.00031;
  (50,5,0.6): 0.37948 vs 0.37948 ± 0.00030.
* $N=1000$, $\rho=0.9$, 3.2 million conferences (`t_rho09b_*.out`): K=5: 0.48853 ± 0.00011 vs 0.48875;
  K=10: 0.531712 ± 0.000074 vs 0.531722.
* Repository simulator at $\rho\in\{0.6,0.75,0.9\}$, $N\in\{10^3,\dots,10^6\}$, $K\in\{1,5,10,30,100\}$: §13.

### 4.2 Large-N limit at fixed K

For fixed K the relevant $(x,y)$ have $N\bar\Phi(x)$, $N\bar\Phi(y)$ of order 1. The cell counts become
independent Poisson variables. The joint cell has mean $Np_{11}\to0$ there (§4.4), so $T_X$ and $T_Y$
become independent, with $N\bar\Phi(T_X)$ and $N\bar\Phi(T_Y)$ each $\Gamma(K,1)$. Hence

$$\mathrm{prec}_{N,K}\approx\frac NK\,E\Big[H\big(\tfrac{\Gamma_K}N,\tfrac{\Gamma'_K}N\big)\Big],\qquad\Gamma_K,\Gamma'_K\text{ iid }\Gamma(K,1).$$

### 4.3 Leading law with prefactor (Laplace method)

*Copula identity.* With $x=\bar\Phi^{-1}(u)$, $y=\bar\Phi^{-1}(v)$,
$\log c=-\log\tau-(\rho^2x^2-2\rho xy+\rho^2y^2)/(2\tau^2)$. Rewrite the quadratic form:
$\kappa(x^2+y^2)/2-\rho(x-y)^2/(2\tau^2)$ has $x^2$ coefficient $\kappa/2-\rho/(2\tau^2)=-\rho^2/(2\tau^2)$ and
$xy$ coefficient $\rho/\tau^2$, which matches. With $e^{x^2/2}=R(x)/(\sqrt{2\pi}\,u)$, exactly:

$$c(u,v)=\frac1\tau\left[\frac{R(x)R(y)}{2\pi uv}\right]^{\kappa}\exp\!\Big(-\frac{\rho(x-y)^2}{2\tau^2}\Big).$$

*Laplace step.* For $u=a/N$, $v=b/N$ with $a,b=O(1)$: $x,y=B_N+O(1/B_N)$, so $R(x)R(y)=R(B_N)^2(1+O(B_N^{-2}))$
and $(x-y)^2=O(B_N^{-2})$. Since $NR(B_N)=1/\phi(B_N)$, $N^2R(B_N)^2/(2\pi)=e^{B_N^2}$, and

$$c(a/N,b/N)\approx\frac1\tau\,e^{\kappa B_N^2}(ab)^{-\kappa},\qquad
H(a/N,b/N)\approx\frac{e^{\kappa B_N^2}}{\tau N^2}\,\frac{(ab)^{1-\kappa}}{(1-\kappa)^2}.$$

Insert into §4.2 and use $E\Gamma_K^{1-\kappa}=\Gamma(K+1-\kappa)/\Gamma(K)$ and $1/(1-\kappa)=1+\rho$:

$$\boxed{\mathrm{prec}_{N,K}\sim C_K(\rho)\,\frac{e^{\kappa B_N^2}}{N},\qquad C_K(\rho)=\frac{(1+\rho)^2}{K\tau}\left[\frac{\Gamma(K+1-\kappa)}{\Gamma(K)}\right]^2.}$$

Because $e^{-B_N^2/2}=\sqrt{2\pi}/(NR(B_N))$ and $R(B)\approx1/B$: $e^{\kappa B_N^2}/N=N^{-\beta}(2\pi B_N^2)^{-\kappa}(1+O(B_N^{-2}))$, so

$$\mathrm{prec}_{N,K}\sim C_K(\rho)\,N^{-(1-\rho)/(1+\rho)}\,(4\pi\log N)^{-\rho/(1+\rho)}.$$

The precision tends to 0 for every $\rho<1$. The rate is the power $\beta=(1-\rho)/(1+\rho)$ times the
slowly varying factor $(\log N)^{-\kappa}$. In terms of the reliability $r=\rho^2$: $\beta=(1-\sqrt r)/(1+\sqrt r)$.
$\beta=1/\eta-1$ with Ledford–Tawn's coefficient $\eta=(1+\rho)/2$. Check $\rho=0$: $\kappa=0$, $c\equiv1$,
the formula gives exactly $K/N$ (random selection).

Values: $\beta$ = 0.333, 0.250, 0.176, 0.143, 0.111, 0.053 for $\rho$ = 0.5, 0.6, 0.7, 0.75, 0.8, 0.9; at the
NeurIPS 2021 calibration ($\rho^2=0.5563$) $\beta=0.1456$.

| $\rho$ | $C_1$ | $C_5$ | $C_{10}$ | $C_{30}$ | $C_{100}$ |
|---|---|---|---|---|---|
| 0.50 | 2.117 | 4.252 | 5.475 | 8.013 | 12.03 |
| 0.75 | 3.673 | 5.550 | 6.278 | 7.466 | 8.917 |
| 0.90 | 6.521 | 8.577 | 9.119 | 9.824 | 10.53 |

*K=1 form.* $C_1=\Gamma(1-\kappa)^2/\tau$ (since $(1+\rho)\Gamma(2-\kappa)=\Gamma(1-\kappa)$).

*A wrong prefactor to avoid.* The heuristic "a selected paper has quality $N(\rho z,\tau^2)$ and must
exceed $z$", with $z=\bar\Phi^{-1}(K/N)$, gives $\bar\Phi(\sqrt\beta z)\sim(K/N)^{\beta}(2\pi z^2)^{-\kappa}/\sqrt\beta$.
It has the correct exponents but the wrong constant. The true law is larger by the factor $(1+\rho)F_K(\rho)$
($F_K$ of §4.6): 1.22 at $K=1$, $\rho=0.5$ (where it equals $\Gamma(1-\kappa)\Gamma(2-\kappa)$) and 1.71 at $K=10$,
$\rho=0.75$. The numerics confirm it: heuristic/exact = 0.819 and 0.586 at $N=10^{250}$ (column "naive" in
`t_asym.out`). The heuristic puts the selected paper's score exactly at the threshold instead of above it (worth the factor
$1+\rho$) and ignores the Poisson fluctuation of both thresholds (worth $F_K$). The fixed-percentile formula at $p=K/N$ keeps the first and
misses only the second, by the factor $F_K$.

### 4.4 Size of the next corrections

**(i) Slowly varying correction, relative $O(1/\log N)$.** Choose the reference point $a_\ast=e^{\mu_K}$ with
$\mu_K=E_w\log a$, $\sigma_K^2=\mathrm{Var}_w\log a$ under the weight $w(a)\propto a^{-\kappa}Q_K(a)$. This weight is a
mixture of $\Gamma(j+1-\kappa)$ laws with weights $\propto\Gamma(j+1-\kappa)/j!$, so
$\mu_K=\sum w_j\psi(j+1-\kappa)$, $\sigma_K^2=\sum w_j[\psi(j+1-\kappa)^2+\psi'(j+1-\kappa)]-\mu_K^2$. Let
$B_\ast=\bar\Phi^{-1}(a_\ast/N)$. Expand $x(a)=B_\ast-\log(a/a_\ast)/B_\ast+\dots$ so that
$R(x)/R(B_\ast)=1+\log(a/a_\ast)/B_\ast^2$ and $(x-y)^2=\log^2(a/b)/B_\ast^2$. The linear terms vanish by the
choice of $a_\ast$. The quadratic term gives

$$\mathrm{prec}_{N,K}\approx\frac{(1+\rho)^2\Gamma(K+1-\kappa)^2}{K\tau\Gamma(K)^2}\,\frac{a_\ast^{2\kappa}e^{\kappa B_\ast^2}}{N}\Big(1-\frac{\rho\,\sigma_K^2}{\tau^2B_\ast^2}+O(B_\ast^{-4})\Big).$$

The coefficient $-\rho\sigma_K^2/\tau^2$ is large: $-2.04$ ($\rho=0.5$, K=1), $-6.76$ ($\rho=0.75$, K=1),
$-5.42$ ($\rho=0.75$, K=10), $-21.4$ ($\rho=0.9$, K=1). With $B_\ast^2\approx10$–25 in the range of interest the
first-order term is not small. This is why the leading law is off by 10 to 60 percent at $N\le10^6$.

**(ii) Joint exceedances, relative $O(N^{-\beta}(\log N)^{-\kappa})$.** In the Poisson limit with independent cell
counts, expand $G$ to first order in $\lambda_{11}=Np_{11}$:
$G\approx Q_K(a)Q_K(b)+\lambda_{11}\pi_{K-1}(a)\pi_{K-1}(b)$, $\pi_{K-1}(a)=e^{-a}a^{K-1}/(K-1)!$
(the shift of the other two cell means by $-\lambda_{11}$ and $Q_{K-1}=Q_K-\pi_{K-1}$ give this). A second Laplace
step, $P_2(x,y)\approx\phi_2(x,y)\tau^4/((x-\rho y)(y-\rho x))$, gives $\lambda_{11}\approx c\,ab(1+\rho)^2/N$. With
$\int a^{1-2\kappa}\pi_{K-1}(a)\,da=\Gamma(K+\beta)/\Gamma(K)$:

$$\Delta=\frac{(1+\rho)^2}{K\tau^2}\left[\frac{\Gamma(K+\beta)}{\Gamma(K)}\right]^2\frac{e^{2\kappa B^2}}{N^2},\qquad
\frac{\Delta}{\text{lead}}=\frac1\tau\left[\frac{\Gamma(K+\beta)}{\Gamma(K+1-\kappa)}\right]^2N^{-\beta}(2\pi B^2)^{-\kappa}.$$

$\Delta>0$: the two thresholds are positively dependent. Its relative size is comparable to the precision
itself. It is a power of N below term (i), so (i) dominates asymptotically.

**(iii) Binomial versus Poisson:** relative $O(K/N)$.

### 4.5 Numerical verification of the law, up to $N=10^{250}$

`t_asym.out`: "exact" is the multinomial integral ($N\le10^7$) or the Poisson-cell integral ($N\le10^{40}$);
"indep" is §4.2 (independent thresholds), computed to $N=10^{250}$ in log space. Ratios to the exact value:

| K | $\rho$ | N | lead ($B_N$ form) | lead ($4\pi\log N$ form) | indep | (exact−indep)/$\Delta$ |
|---|---|---|---|---|---|---|
| 1 | 0.5 | $10^3$ | 1.153 | 1.080 | 0.976 | 0.78 |
| 1 | 0.5 | $10^6$ | 1.096 | 1.052 | 0.998 | 0.88 |
| 1 | 0.5 | $10^{12}$ | 1.051 | 1.026 | 1.000 | 0.94 |
| 1 | 0.5 | $10^{30}$ | 1.021 | 1.009 | 1.000 | 0.97 |
| 1 | 0.5 | $10^{100}$ | 1.006 | 1.002 | | |
| 1 | 0.5 | $10^{250}$ | 1.0025 | 1.0005 | | |
| 10 | 0.75 | $10^3$ | 1.211 | 1.113 | 0.986 | 0.61 |
| 10 | 0.75 | $10^6$ | 1.132 | 1.075 | 0.996 | 0.80 |
| 10 | 0.75 | $10^{12}$ | 1.076 | 1.043 | 1.000 | 0.89 |
| 10 | 0.75 | $10^{30}$ | 1.033 | 1.018 | 1.000 | 0.95 |
| 10 | 0.75 | $10^{100}$ | 1.011 | 1.005 | | |
| 10 | 0.75 | $10^{250}$ | 1.0043 | 1.0017 | | |
| 100 | 0.75 | $10^3$ | 1.044 | 0.959 | 0.998 | 0.30 |
| 100 | 0.75 | $10^{12}$ | 1.037 | 1.006 | 1.000 | 0.89 |
| 100 | 0.75 | $10^{250}$ | 1.0024 | 0.9998 | | |
| 1 | 0.9 | $10^3$ | 1.604 | 1.461 | 0.817 | 0.49 |
| 1 | 0.9 | $10^6$ | 1.405 | 1.327 | 0.900 | 0.60 |
| 1 | 0.9 | $10^{30}$ | 1.141 | 1.123 | 0.997 | 0.83 |
| 1 | 0.9 | $10^{250}$ | 1.020 | 1.017 | | |
| 10 | 0.9 | $10^{6}$ | 1.364 | 1.288 | 0.987 | 0.65 |
| 10 | 0.9 | $10^{250}$ | 1.0145 | 1.0117 | | |

The leading law, prefactor included, is confirmed: every ratio tends to 1, with the slow $1/B_N^2$ approach
that (i) predicts. Test of the coefficient in (i): $(\text{indep}/\text{lead}_\ast-1)B_\ast^2$ tends to
$-\rho\sigma_K^2/\tau^2$: −2.023 vs −2.043 ($\rho=0.5$, K=1, $N=10^{250}$); −5.31 vs −5.42 ($\rho=0.75$, K=10);
−5.16 vs −5.27 ($\rho=0.75$, K=100); −20.4 vs −21.4 ($\rho=0.9$, K=1); the remaining gap is $O(B^{-2})$.
Test of (ii): (exact−indep)/$\Delta$ rises toward 1 (0.97 at $10^{30}$ for $\rho=0.5$, K=1; 0.95 for
$\rho=0.75$, K=10). The first-order formula (i) is useless at $N\le10^6$ for $\rho\ge0.75$ (it can turn
negative); use the 2D integral or §4.6 there.

### 4.6 Practical formula: fixed-percentile formula times a Poisson factor

Write the fixed-K result as the percentile formula at $p=K/N$ times a correction. In the §4.3 calculation
the percentile formula uses fixed thresholds ($\Gamma_K\equiv K$), which gives $K^{2(1-\kappa)}$ in place of
$[\Gamma(K+1-\kappa)/\Gamma(K)]^2$. Hence

$$\boxed{\mathrm{prec}_{N,K}\approx F_K(\rho)\,\frac{P_2(z,z;\rho)}{K/N},\quad z=\bar\Phi^{-1}(K/N),\quad
F_K=\left[\frac{\Gamma(K+1-\kappa)}{\Gamma(K)\,K^{1-\kappa}}\right]^2=1-\frac{\kappa(1-\kappa)}K+O(K^{-2}).}$$

$F_K$ = 0.81, 0.95, 0.976, 0.992, 0.998 for K = 1, 5, 10, 30, 100 (nearly independent of $\rho$). Because
$P_2$ is computed exactly, this formula keeps the exact Gaussian tail and avoids error (i). Ratio to the
exact value (`t_tables.out`), $N=10^3\dots10^{12}$:

| $\rho$ | K=1 | K=10 | K=100 |
|---|---|---|---|
| 0.5 | 0.998–1.011 | 0.998–1.002 | 0.999–1.0002 |
| 0.75 | 0.975–1.020 | 0.996–1.003 | 0.999–1.0003 |
| 0.9 | 0.926–1.015 | 0.994–1.003 | 0.999–1.0002 |

At the NeurIPS 2021 calibration ($\rho=0.7459$), exact precision vs this formula (`t_calib_table.out`):

| K | $N=10^3$ | $10^4$ | $10^5$ | $10^6$ |
|---|---|---|---|---|
| 1 | 0.1635 / 0.1595 | 0.1054 / 0.1050 | 0.0696 / 0.0702 | 0.0467 / 0.0473 |
| 10 | 0.3062 / 0.3050 | 0.1963 / 0.1962 | 0.1290 / 0.1292 | 0.0861 / 0.0863 |
| 30 | 0.3886 / 0.3879 | 0.2454 / 0.2452 | 0.1599 / 0.1599 | 0.1061 / 0.1062 |
| 100 | 0.5078 / 0.5073 | 0.3119 / 0.3118 | 0.2006 / 0.2006 | 0.1320 / 0.1320 |

### 4.7 Local log-log slope versus the asymptotic slope

From the leading form with reference $B_\ast$: $\log\mathrm{prec}=\text{const}+\kappa B_\ast^2-\log N$ and
$dB_\ast/d\log N=R(B_\ast)$, so

$$\frac{d\log\mathrm{prec}}{d\log N}\approx-1+2\kappa B_\ast R(B_\ast)=-\beta-2\kappa\,(1-B_\ast R(B_\ast))\approx-\beta-\frac{2\kappa}{B_\ast^2}.$$

The local slope is steeper than $-\beta$ and approaches it only like $1/\log N$. Exact local slopes
(finite differences of the exact integral; `t_slope.out`):

| $\rho$ | K | slope at $10^3$ | $10^4$ | $10^5$ | $10^6$ | chord $10^3\to10^6$ | $-\beta$ | chord/$(-\beta)$ |
|---|---|---|---|---|---|---|---|---|
| 0.5 | 1 | −0.379 | −0.366 | −0.359 | −0.354 | −0.363 | −0.333 | 1.09 |
| 0.5 | 10 | −0.387 | −0.372 | −0.364 | −0.358 | −0.369 | −0.333 | 1.11 |
| 0.5 | 100 | −0.419 | −0.386 | −0.371 | −0.363 | −0.381 | −0.333 | 1.14 |
| 0.6 | 10 | −0.307 | −0.291 | −0.282 | −0.277 | −0.288 | −0.250 | 1.15 |
| 0.7 | 10 | −0.233 | −0.218 | −0.210 | −0.204 | −0.215 | −0.176 | 1.22 |
| 0.75 | 1 | −0.195 | −0.182 | −0.174 | −0.169 | −0.179 | −0.143 | 1.25 |
| 0.75 | 10 | −0.198 | −0.184 | −0.176 | −0.170 | −0.181 | −0.143 | 1.27 |
| 0.75 | 100 | −0.227 | −0.197 | −0.183 | −0.175 | −0.192 | −0.143 | 1.35 |
| 0.8 | 10 | −0.164 | −0.151 | −0.143 | −0.138 | −0.148 | −0.111 | 1.33 |
| 0.9 | 1 | −0.099 | −0.089 | −0.083 | −0.078 | −0.086 | −0.053 | 1.64 |
| 0.9 | 10 | −0.097 | −0.086 | −0.080 | −0.076 | −0.084 | −0.053 | 1.60 |
| 0.9 | 100 | −0.117 | −0.095 | −0.086 | −0.080 | −0.092 | −0.053 | 1.75 |

The approximation $-\beta-2\kappa(1-B_\ast R(B_\ast))$ at $N=10^6$: −0.357, −0.211, −0.178, −0.148, −0.091
for ($\rho$, K) = (0.5,1), (0.7,10), (0.75,10), (0.8,10), (0.9,10); exact −0.354, −0.204, −0.170, −0.138,
−0.076. A power law fitted over $10^3$–$10^6$ overstates the asymptotic decay rate by 10 percent at
$\rho=0.5$ and by 60 to 75 percent at $\rho=0.9$.

---

## 5. The mechanism (item 5)

1. *Conditional law.* $X\mid Y=y\sim N(\rho y,\tau^2)$, so the concomitant of the i-th score is
   $X_{[i]}=\rho Y_{(i)}+\tau W_i$ exactly.
2. *Fixed number.* The top scores sit at $Y_{(i)}\approx B_N\approx\sqrt{2\log N}$. Their expected quality is
   $\rho E Y_{(i)}$. Entry to the true top K needs quality above $X_{(K)}\approx B_N$. The ratio of expected to
   needed quality stays at $\rho$, but the absolute gap $(1-\rho)B_N$ grows without bound. The conditional
   spread that could close the gap stays at $\tau$ (plus a vanishing $\rho^2\mathrm{Var}Y_{(1)}=O(1/\log N)$).
   The gap in SD units is $(1-\rho)B_N/\tau=\sqrt\beta\,B_N$, and $\bar\Phi(\sqrt\beta B_N)\approx N^{-\beta}$ up to logs.
3. *Laplace view of the exponent.* A paper is in both top sets only if $x\gtrsim B$ and $y\gtrsim B$. The
   cheapest such point is $x=y=B$, where $\phi_2\propto\exp(-B^2/(1+\rho))=N^{-2/(1+\rho)}\times$ logs. N papers
   times this, divided by K, gives $N^{1-2/(1+\rho)}=N^{-\beta}$.
4. *What is selected instead.* The selected papers have quality about $\rho B_N\pm\tau$: very good (true
   percentile $1-O(N^{-\rho^2})$), not the best (true rank about $N^{1-\rho^2}$; §8).
5. *Fixed percentile.* Thresholds stay at $z_p$. $E[X\mid Y=z_p]=\rho z_p$, $E[X\mid Y>z_p]=\rho\phi(z_p)/p$,
   $E[X\mid X>z_p]=\phi(z_p)/p$. The gap $(1-\rho)z_p/\tau$ is fixed, so precision is fixed.

Numbers (`t_mech.out`; exact order-statistic integrals):

| $\rho$ | N | $E Y_{(1)}$ | $\rho E Y_{(1)}$ (top-scored quality) | needed: $E X_{(10)}$ | gap to $X_{(10)}$ in $\tau$ units | exact prec K=10 |
|---|---|---|---|---|---|---|
| 0.75 | $10^3$ | 3.241 | 2.431 | 2.343 | −0.13 | 0.311 |
| 0.75 | $10^4$ | 3.852 | 2.889 | 3.104 | 0.33 | 0.200 |
| 0.75 | $10^5$ | 4.384 | 3.288 | 3.731 | 0.67 | 0.133 |
| 0.75 | $10^6$ | 4.863 | 3.647 | 4.276 | 0.95 | 0.089 |
| 0.6 | $10^6$ | 4.863 | 2.918 | 4.276 | 1.70 | 0.025 |
| 0.9 | $10^6$ | 4.863 | 4.377 | 4.276 | −0.23 | 0.297 |

Fixed percentile, $\rho=0.75$: $p=1\%$: $z_p=2.326$, $\rho z_p=1.745$, gap $0.88\tau$; $p=5\%$: gap $0.62\tau$;
$p=25\%$: gap $0.26\tau$, all independent of N. Simulator check ($\rho=0.75$, $N=10^4$, 2000 conferences): mean
quality of the top-scored paper 2.884 ± 0.016 (formula 2.889); SD 0.714 (formula
$\sqrt{\tau^2+\rho^2\mathrm{Var}Y_{(1)}}\approx0.70$).

---

## 6. Containment in a fixed top percentile (item 6)

For a fixed population threshold $z_p$ the share is a one-dimensional functional of the top-K scores. Because
$E\sum_{i\in\mathrm{Top}_K(Y)}g(Y_i)=N\int\phi(y)P(\mathrm{Bin}(N-1,\bar\Phi(y))\le K-1)g(y)\,dy$ exactly,

$$C_{N,K}(p)=\frac NK\int_0^1F_{\rm Bin}(K-1;N-1,v)\;\Phi\!\Big(\frac{\rho\bar\Phi^{-1}(v)-z_p}{\tau}\Big)dv.$$

The empirical threshold (true top $\mathrm{round}(pN)$) differs by $O(1/N)$; its exact value is the
multinomial formula of §4.1 with quality cap $M=\mathrm{round}(pN)$.

**Limit.** The selected scores grow like $B_N$, so their qualities $\rho B_N+\tau W$ pass any fixed $z_p$:
$C_{N,K}(p)\to1$ for every $\rho>0$, $p$ and K. The deficit is $\frac1K\sum_{i\le K}E\,\Phi((z_p-\rho Y_{(i)})/\tau)$.
With $\bar\Phi(t)\approx\phi(t)/t$, $(\rho y-z)^2=\rho^2y^2-2\rho yz+z^2$ and $e^{-y^2/2}=\sqrt{2\pi}\,a/(NR(y))$:

$$1-C_{N,K}(p)\asymp N^{-\rho^2/(1-\rho^2)}\exp\!\Big(\frac{\rho z_p}{\tau^2}B_N\Big)\times(\text{powers of }\log N),$$

so the decay is slower than any fixed power $N^{-\rho^2/(1-\rho^2)}$ suggests at moderate N. Practical form:
$1-C\approx\frac1K\sum_{i\le K}\bar\Phi((\rho E Y_{(i)}-z_p)/\tau)$.

Numbers (`t_contain.out`; exact integral, deficit, practical form):

| $\rho$ | p | K | N=$10^3$ | $10^4$ | $10^5$ | $10^6$ | $10^8$ | $10^{12}$ |
|---|---|---|---|---|---|---|---|---|
| 0.5 | 1% | 10 | 0.128 | 0.229 | 0.343 | 0.458 | 0.660 | 0.896 |
| 0.75 | 1% | 1 | 0.556 | 0.789 | 0.918 | 0.973 | 0.998 | 1.000 |
| 0.75 | 1% | 10 | 0.311 | 0.605 | 0.822 | 0.934 | 0.994 | 1.000 |
| 0.75 | 5% | 10 | 0.683 | 0.896 | 0.973 | 0.994 | 0.9998 | 1.000 |
| 0.9 | 1% | 10 | 0.529 | 0.921 | 0.995 | 0.9999 | 1.000 | 1.000 |

Practical form vs exact deficit at $\rho=0.75$, $p=1\%$, K=10: 0.690/0.689, 0.392/0.395, 0.175/0.178,
0.064/0.066 for $N=10^3\dots10^6$. Simulator checks of $c1pct$, $c5pct$: §13.

Contrast: the share of $\mathrm{Top}_K(Y)$ in the true top $M=cK$ (fixed multiple) tends to 0 at the same rate
as the precision. The leading law is
$\frac{(1+\rho)^2}{K\tau}\frac{\Gamma(K+1-\kappa)\Gamma(M+1-\kappa)}{\Gamma(K)\Gamma(M)}\frac{e^{\kappa B_N^2}}N$
(same derivation as §4.3 with one Gamma moment taken at $M$). Check against the independent-threshold
integral at $\rho=0.75$ (`t_containM.out`): ratio law/integral for (K, M) = (10, 20): 1.140, 1.034, 1.011, 1.004
at $N=10^6,10^{30},10^{100},10^{250}$; (10, 100): 1.297, 1.060, 1.018, 1.007. The crossover between "$\to0$" and
"$\to1$" is at $M$ of the order of the typical true rank of a selected paper, about $N^{1-\rho^2}$ (§8).

---

## 7. Best-paper probability (item 7)

**Exact.** Condition on the best paper's quality $m$ (density $N\phi(m)\Phi(m)^{N-1}$) and its score
$y=\rho m+\tau z$. The other $N-1$ papers are iid given $X<m$. Each out-scores it with probability
$\pi(m,y)=(\bar\Phi(y)-P_2(m,y))/\Phi(m)$. The best paper is in $\mathrm{Top}_K(Y)$ iff at most $K-1$ do:

$$P_{\rm best}(N,K)=\int N\phi(m)\Phi(m)^{N-1}\!\int\phi(z)\,F_{\rm Bin}\big(K-1;N-1,\pi(m,\rho m+\tau z)\big)\,dz\,dm.$$

The handoff's semi-analytic version replaces the binomial by Poisson($\lambda=(N-1)\pi$). In copula
variables (`core.best_exact`) the integrand is $c(u,v)(1-u)^nF_{\rm Bin}(K-1;n,(v-p_{11})/(1-u))$.

**Leading law.** $a=N\bar\Phi(m)$ tends to Exp(1) and $b=N\bar\Phi(y)$ has the conditional density of the copula.
The integral is $\frac1N\int\!\!\int e^{-a}c(a/N,b/N)Q_K(b)\,da\,db$. The Laplace step of §4.3 gives

$$\boxed{P_{\rm best}(N,K)\sim\frac{\Gamma(1-\kappa)(1+\rho)\Gamma(K+1-\kappa)}{\tau\,\Gamma(K)}\,\frac{e^{\kappa B_N^2}}N
\sim\frac{\Gamma(1-\kappa)(1+\rho)\Gamma(K+1-\kappa)}{\tau\,\Gamma(K)}\,N^{-\beta}(4\pi\log N)^{-\kappa}.}$$

Same rate as the precision. At K=1 it equals $C_1$ (as it must: $P_{\rm best}(N,1)=\mathrm{prec}_{N,1}$).
K-dependence: $P_{\rm best}(K)/P_{\rm best}(1)\to\Gamma(K+1-\kappa)/(\Gamma(K)\Gamma(2-\kappa))\sim K^{1/(1+\rho)}$.
ρ-dependence: through $\beta$ and the constant.

**Checks** (`t_best.out`):

* Exact small N: $N=3$, K=2, $1-3P(X_1>X_2,X_1>X_3,Y_1<Y_2,Y_1<Y_3)$ (4-dim orthant): 0.77002017 /
  0.77002017 ($\rho=0.3$); 0.96669635 / 0.96669634 ($\rho=0.9$). $N=2$: $1/2+\arcsin(\rho)/\pi$ to $10^{-9}$.
* Poisson($\lambda$) route of the handoff (exact density of $m$, Poisson count with $\lambda=(N-1)\pi$) vs the
  exact binomial: relative difference at most $5.5\times10^{-4}$ at $N=10^3$, $5.5\times10^{-5}$ at $10^4$,
  $6\times10^{-7}$ at $10^6$ ($\rho\in\{0.5,0.75,0.9\}$, $K\in\{1,10,30\}$; `t_best_poisson.out`).
* Repository `simulate_best_paper`, $\rho=0.75$:

| N | reps | K=1 sim / exact | K=5 | K=10 | K=30 |
|---|---|---|---|---|---|
| $10^3$ | 40,000 | 0.1683 ± 0.0019 / 0.1670 | 0.4189 / 0.4176 | 0.5584 / 0.5585 | 0.7786 / 0.7816 |
| $10^4$ | 20,000 | 0.1069 ± 0.0022 / 0.1084 | 0.2808 / 0.2792 | 0.3859 / 0.3844 | 0.5824 / 0.5788 |
| $10^5$ | 6,000 | 0.0737 ± 0.0034 / 0.0720 | 0.1932 / 0.1887 | 0.2638 / 0.2645 | 0.4127 / 0.4164 |
| $10^6$ | 2,000 | 0.0480 ± 0.0048 / 0.0486 | 0.1290 / 0.1287 | 0.1860 / 0.1825 | 0.3100 / 0.2960 |

  All within 1.5 SE.
* Leading law (exact/leading): $\rho=0.5$, K=1: 0.867 ($10^3$), 0.913 ($10^6$), 0.952 ($10^{12}$), 0.994 ($10^{100}$);
  $\rho=0.75$, K=10: 0.614, 0.749, 0.848, 0.977; $\rho=0.9$, K=1: 0.623, 0.712, 0.787, 0.955. The law holds but
  converges slowly; use the exact integral (cheap) for numbers.

At the NeurIPS 2021 calibration: $P_{\rm best}$ (K=1, 5, 10, 30) = 0.164, 0.411, 0.551, 0.775 at $N=10^3$ and
0.047, 0.124, 0.176, 0.287 at $N=10^6$.

---

## 8. True rank of the top-scored paper (item 8)

**Exact distribution.** The winner has score $y$ (density $N\phi(y)\Phi(y)^{N-1}$) and quality
$x=\rho y+\tau w$. The others are iid given $Y<y$; each has higher quality with probability
$\theta=(\bar\Phi(x)-P_2(x,y))/\Phi(y)$. So

$$P(\mathrm{rank}\le r)=\int N\phi(y)\Phi(y)^{N-1}\!\int\phi(w)\,F_{\rm Bin}\big(r-1;N-1,\theta(\rho y+\tau w,y)\big)\,dw\,dy$$

(`core.winner_cdf`; the quality grid has breakpoints at $r\pm k\sqrt r$, where the binomial cdf steps).
$P(\mathrm{rank}=1)=\mathrm{prec}_{N,1}$.

**Median.** Rank $\approx N\bar\Phi(V)$ with $V=\rho Y_{(1)}+\tau W$, a decreasing function of $V$. So the median
rank is $N\bar\Phi(\mathrm{med}\,V)$. With $Y_{(1)}=B-\log A/B$, $A\sim$Exp(1), and $E[-\log A]=\gamma_E$, a
small-perturbation argument gives $\mathrm{med}\,V=\rho(B+\gamma_E/B)+O(B^{-2})$. Hence

$$\mathrm{median\ rank}\approx N\bar\Phi\big(\rho(B_N+\gamma_E/B_N)\big)\approx\frac{e^{-\gamma_E\rho^2}}{\rho}\left(\frac{N}{\sqrt{2\pi}\,B_N}\right)^{1-\rho^2}.$$

The factor $e^{-\gamma_E\rho^2}$ (0.87, 0.72, 0.63 for $\rho$ = 0.5, 0.75, 0.9) is easy to lose. Plugging the
typical maximum $B_N$ into $\bar\Phi$ omits it and overstates the median by 15 to 60 percent. The median grows like
$N^{1-\rho^2}(\log N)^{-(1-\rho^2)/2}$.

**Spread.** $\log\mathrm{rank}\approx\log N+\log\bar\Phi(V)$ and $d\log\bar\Phi/dv\approx-\rho B$, so log-rank is close
to normal with SD $\approx\sqrt{\rho^2\tau^2B_N^2+\pi^2\rho^4/6}$ (W part, Gumbel part). It widens like
$\sqrt{\log N}$.

**Mean.** $E[\mathrm{rank}]-1=(N-1)E\bar\Phi(V)$-like and $E\bar\Phi(\rho y+\tau W)=\bar\Phi(\rho y/\sqrt{2-\rho^2})$. So
the mean grows like $N^{1-\omega}$, $\omega=\rho^2/(2-\rho^2)$, faster than the median: unlucky draws ($W\ll0$)
dominate it. The mean true percentile of $\mathrm{Top}_K$ (simulator `pctl_K`) is exactly
$\frac NK\int F_{\rm Bin}(K-1;n,v)\,\Phi(\rho\bar\Phi^{-1}(v)/\sqrt{2-\rho^2})\,dv$ (§13 checks it).

**Checks** (`t_winner.out`, `compare_sim2.md`):

| $\rho$ | N | exact median | semi $N\bar\Phi(\rho(B+\gamma/B))+2/3$ | closed form | simulator median | q10 – q90 (exact) |
|---|---|---|---|---|---|---|
| 0.5 | $10^3$ | 53 | 51.3 | 66.3 | | 4 – 313 |
| 0.5 | $10^6$ | 7,528 | 7,397 | 8,538 | | 191 – 95,004 |
| 0.5 | $10^{12}$ | 1.88e8 | 1.87e8 | 2.01e8 | | 1.5e6 – 7.3e9 |
| 0.75 | $10^3$ | 8 | 7.7 | 8.1 | 8 (40,000 conf.) | 1 – 64 |
| 0.75 | $10^4$ | 20 | 19.0 | 20.4 | 20 | 1 – 230 |
| 0.75 | $10^5$ | 51 | 49.0 | 52.6 | 50 | 2 – 812 |
| 0.75 | $10^6$ | 134 | 128.7 | 137.4 | 139.5 (2,000 conf.) | 4 – 2,818 |
| 0.75 | $10^{12}$ | 48,166 | 47,144 | 48,830 | | 285 – 3.9e6 |
| 0.9 | $10^6$ | 7 | 6.4 | 6.0 | 7 | 1 – 87 |

Exact cdf at the simulator's pooled quartiles ($\rho=0.75$): 0.255/0.506/0.746 at $N=10^6$ (target
0.25/0.5/0.75); similar at the other N and $\rho$. Small-N check: $N=2$: $P(\mathrm{rank}=1)=0.70483275$ vs
$1/2+\arcsin(0.6)/\pi=0.70483276$.

---

## 9. Two-committee top-K overlap (item 9)

$(Y_1,Y_2)$ is a standard bivariate normal pair with correlation $r_{12}$ ($=\rho^2$ when $u$ is redrawn), and
$|\mathrm{Top}_K(Y_1)\cap\mathrm{Top}_K(Y_2)|$ has the same law as $|\mathrm{Top}_K(Y)\cap\mathrm{Top}_K(X)|$ with
correlation $r_{12}$. So, exactly, at every N and K,

$$\mathrm{ovl}(N,K,\rho)=\mathrm{prec}(N,K,r_{12}),$$

and every result of §4 carries over with $\rho\to r_{12}$: limit 0, rate $N^{-(1-r_{12})/(1+r_{12})}(\log N)^{-r_{12}/(1+r_{12})}$,
prefactor $C_K(r_{12})$, practical formula $F_K(r_{12})P_2(z,z;r_{12})/(K/N)$; fixed percentile
$P_2(z_p,z_p;r_{12})/p$. Since $r_{12}=\rho^2<\rho$, the overlap is below the precision and decays faster
(exponent 0.285 vs 0.146 at the NeurIPS 2021 calibration). Overlap is observable; inverting it gives $r_{12}$,
then $\rho=\sqrt{r_{12}}$, then the precision. If $u$ were shared by both committees, $r_{12}>\rho^2$ and the
overlap would overstate the reliability that matters.

At the NeurIPS 2021 calibration, overlap K=10: 0.157, 0.073, 0.035, 0.017 for $N=10^3\dots10^6$ (precision
0.306, 0.196, 0.129, 0.086). Simulator checks of `ovl_K` and `ovl_p`: §13.

---

## 10. Tails (item 10)

### 10.1 Principle

$\mathrm{prec}_{N,K}=(N/K)P(\text{paper in }\mathrm{Top}_K(Q)\cap\mathrm{Top}_K(S))$ is decided by the joint upper tail of
(Q, S) at levels exceeded by O(1) papers, that is, by the copula of (Q, S) near (1, 1). Let
$\chi=\lim_{u\to1}P(F_S(S)>u\mid F_Q(Q)>u)$.

* $\chi>0$ (asymptotic dependence): the point process of the top (quality, score) pairs has a
  non-degenerate limit, so $\mathrm{prec}_{N,K}$ tends to a positive constant that depends on K; as K grows
  (with $K/N\to0$) it tends to $\chi$.
* $\chi=0$ (asymptotic independence): $\mathrm{prec}_{N,K}\to0$ like $N^{1-1/\eta}$ times a slowly varying factor,
  with Ledford–Tawn $\eta\in[1/2,1)$. $\eta=1/2$ gives about $K/N$, which is random selection.

Operational rule. Compare the spacing of the top quality order statistics, $a_Q(N)$, with the noise. The
spacing is $\sigma_q/B_N\to0$ (Gaussian), $\sigma_q$ (exponential), $\propto N^{1/\alpha}$ (regularly varying with
index $\alpha$), $\propto N^{-1/a}$ (bounded with edge exponent $a$). If the noise tail is not heavier than the
quality tail, the top scores belong to top-quality papers, and the ratio $a_Q/\sigma_n$ decides:
$\to\infty$ gives $\mathrm{prec}\to1$; a constant gives a plateau; $\to0$ gives decay. If the noise tail is heavier,
the top scores belong to noise outliers and precision collapses to about $K/N$. Equal regular-variation
indices give a plateau.

### 10.2 The cases

Setting for all numbers: $\mu_q=5$, $\sigma_q=1.2$, $R=3$, $\sigma_u=0$, $\sigma_\varepsilon=\sqrt{4.32}=2.078$ (latent
$\rho^2=0.5$, $\sigma_n/\sigma_q=1$).

1. **Gaussian / Gaussian.** $\chi=0$, $\eta=(1+\rho)/2$: decay $N^{-\beta}$ (§4).
2. **Exponential / Gaussian: plateau.** Top qualities form a Poisson process with intensity $e^{-q}$ (in
   $\sigma_q$ units, shifted by $\log N$). Each point carries an independent mark $\sigma Z$, $\sigma=\sigma_n/\sigma_q$.
   For a tagged point at quality $q$ and score $q+\sigma z$ (Mecke formula), the three region counts are
   independent Poisson with means, with $a=e^{-q}$ and $e_z=e^{\sigma^2/2-\sigma z}$:
   $m_{11}=a[\bar\Phi(z)+e_z\Phi(z-\sigma)]$, $m_{10}=a-m_{11}$, $m_{01}=ae_z-m_{11}$. (Derivative check:
   $\partial_qm_{11}=-e^{-q}\bar\Phi(z)$, as required.) Then
   $$P_\infty(K,\sigma)=\frac1K\int_0^\infty\!da\int\phi(z)\sum_{j<K}\mathrm{Pois}(j;m_{11})\,Q_{K-j}(m_{10})\,Q_{K-j}(m_{01})\,dz,$$
   and for K=1, $P_\infty(1,\sigma)=\int\phi(z)/(\Phi(z)+e^{\sigma^2/2-\sigma z}\bar\Phi(z-\sigma))\,dz$.
   Tail dependence: $P(E'+\sigma Z>\sigma^2/2)$ with $E'\sim$Exp(1) gives $\chi=2\bar\Phi(\sigma/2)$.
   $\sigma=1$: $P_\infty$ = 0.5387 (K=1, 1D and 2D forms agree to $10^{-14}$), 0.5925 (5), 0.6042 (10),
   0.6126 (30), 0.6157 (100); $\chi=0.6171$; $\sigma\to0$: 0.973 at $\sigma=0.05$.
3. **t3 / Gaussian: rises to 1.** Top qualities are $a_N\Gamma_i^{-1/3}$ with $a_N=\sigma_q(2N/(3\pi))^{1/3}$
   (since $P(Q-\mu>x)\sim2\sigma_q^3/(3\pi x^3)$). To first order only the pair (K, K+1) can swap. It swaps when
   $\sigma_n\sqrt2Z$ exceeds the gap $D$; $f_D(0)=3\Gamma(K+4/3)/(\Gamma(K)a_N)$. So
   $$1-\mathrm{prec}_{N,K}\approx\frac{\sigma_n}{\sigma_q}\,\frac{3\,\Gamma(K+4/3)}{K\sqrt\pi\,\Gamma(K)}\left(\frac{3\pi}{2N}\right)^{1/3}\propto N^{-1/3}.$$
4. **t3 / t3: plateau $w$.** Both tails are regularly varying with index 3:
   $P(Q-\mu>x)\sim c_Qx^{-3}$, $P(\bar\varepsilon>e)\sim c_Ee^{-3}$ with $c_E/c_Q=(\sigma_\varepsilon/\sigma_q)^3/R^2$. The top of
   the score list is the union of two independent Poisson processes (quality-driven, noise-driven). Each
   top point is quality-driven with probability $w=c_Q/(c_Q+c_E)$. The j quality-driven points among the top
   K are the top j qualities, all in the true top K. So $\mathrm{prec}\to E[j]/K=w$ for every K:
   $$w=\Big(1+\frac{(\sigma_\varepsilon/\sigma_q)^3}{R^2}\Big)^{-1}=\Big(1+\frac{(\tau/\rho)^3}{\sqrt R}\Big)^{-1}\quad(=0.634\text{ here}),$$
   which depends on R at fixed $\rho$.
5. **Beta / Gaussian: decay, nearly a lottery.** Quality is bounded (edge exponent $a=6.53$); the top
   spacings shrink like $N^{-1/a}$ while the noise stays $\sigma_n$; $\eta=1/2$. Papers within about
   $\sigma_n^2/(s_N-q_{\max})$ of the edge compete on noise. Leading behaviour:
   $\mathrm{prec}\approx K\zeta_N^a/(Nc\,\Gamma(a)\sigma_n^a)$, $\zeta_N\approx\sqrt{2\log N}$, that is $(K/N)(\log N)^{a/2}$.
6. **Heavier noise than quality (Gaussian/t3, exponential/t3, Beta/t3): collapse.** The score tail is the
   noise tail, so the top scores are noise outliers. A true top paper is selected with probability
   $\approx P(\bar\varepsilon>s_N-q)\approx(K/N)(s_N/(s_N-q))^3\to K/N$, because $s_N\propto N^{1/3}\gg q\propto\sqrt{\log N}$.

For the asymptotically independent cases a general approximation holds. With exact marginals and
independent thresholds (`tails.prec_indep_general`):
$\mathrm{prec}\approx\frac NK\int_0^1Q_K(Nu)\,E_E[Q_K(N\bar F_S(q(u)+E))]\,du$.

### 10.3 Simulator results (repository `simulate`, `t_tails_compare.out`, `t_tails_indep.out`)

Fixed-number precision (mean ± SE; reps 10,000 / 4,000 / 800 / 200 / 40 for $N=10^3\dots10^7$):

| quality / noise | K | $10^3$ | $10^4$ | $10^5$ | $10^6$ | $10^7$ | theory |
|---|---|---|---|---|---|---|---|
| Gaussian / Gaussian | 10 | 0.265 | 0.164 | 0.096 | 0.059 | | exact 0.268, 0.162, 0.100, 0.063 |
| exp / Gaussian | 1 | 0.539 | 0.544 | 0.516 ± 0.018 | 0.545 ± 0.035 | 0.55 ± 0.08 | plateau 0.539 |
| exp / Gaussian | 10 | 0.604 | 0.604 | 0.608 | 0.603 | 0.615 | plateau 0.604 |
| exp / Gaussian | 100 | 0.619 | 0.616 | 0.618 | 0.619 | 0.621 | plateau 0.616 ($\chi$ = 0.617) |
| t3 / Gaussian | 1 | 0.698 | 0.854 | 0.935 | 0.960 | 1.000 | $1-cN^{-1/3}$: 0.66, 0.84, 0.93, 0.966, 0.984 |
| t3 / Gaussian | 10 | 0.559 | 0.782 | 0.899 | 0.936 | 0.958 | 0.38, 0.71, 0.865, 0.938, 0.971 |
| t3 / t3 | 10 | 0.484 | 0.572 | 0.620 | 0.633 | 0.605 ± 0.022 | plateau 0.634 |
| t3 / t3 | 100 | 0.499 | 0.493 | 0.580 | 0.623 | 0.623 | plateau 0.634 |
| Beta / Gaussian | 10 | 0.214 | 0.084 | 0.027 | 0.009 | 0.000 | indep. approx 0.209, 0.083, 0.028, 0.008, 0.002 |
| Beta / Gaussian | 100 | 0.462 | 0.214 | 0.085 | 0.028 | 0.009 | 0.461, 0.214, 0.085, 0.029, 0.008 |
| Gaussian / t3 | 10 | 0.206 | 0.018 | 0.0008 | 0.0000 | | 0.202, 0.018, 0.0004, 1.9e-5 |
| Gaussian / t3 | 100 | 0.512 | 0.208 | 0.016 | 0.0003 | | 0.510, 0.208, 0.017, 0.0004 |
| exp / t3 | 100 | 0.650 | 0.578 | 0.422 | 0.071 | | 0.647, 0.576, 0.422, 0.069 |
| Beta / t3 | 100 | 0.501 | 0.152 | 0.0078 | 0.0004 | | 0.500, 0.153, 0.0083, 0.0003 |

So: decay to 0 for Gaussian/Gaussian (slow power), Beta/Gaussian (fast), and every pair whose noise tail is
heavier than the quality tail (collapse to about $K/N$). A positive plateau for exponential/Gaussian and
t3/t3. A rise toward 1 for t3/Gaussian. The independent-threshold approximation reproduces all
asymptotically independent cases. It fails, as it must, for the dependent ones (exponential/Gaussian: 0.398
vs 0.539 at K=1).

### 10.4 Fixed-percentile precision for non-Gaussian shapes

As $N\to\infty$ the empirical quantiles converge, so for every shape
$\mathrm{prec}_\infty(p)=P(Q>q_p,S>s_p)/p$ with population quantiles $q_p$, $s_p$. This depends on the shape and on
$p$ but not on N; finite-N corrections are $O(1/(pN))$ as in §2. Computed limits (1D integrals; the $t_3$
noise survival function by Gil–Pelaez inversion of the characteristic function
$[(1+\sigma_\varepsilon|t|/R)e^{-\sigma_\varepsilon|t|/R}]^R$, checked against 4 million draws) against the simulator:

| quality / noise | limit p=1% | sim $10^4$ / $10^5$ / $10^6$ / $10^7$ | limit p=5% | sim $10^4$ / $10^6$ |
|---|---|---|---|---|
| Gaussian / Gaussian | 0.2735 | 0.2733 / 0.2726 / 0.2736 / – | 0.3985 | 0.3989 / 0.3985 |
| Gaussian / t3 | 0.2088 | 0.2083 / 0.2088 / 0.2089 / – | 0.4166 | 0.4163 / 0.4162 |
| exp / Gaussian | 0.6171 | 0.6156 / 0.6167 / 0.6175 / 0.6171 | 0.6175 | 0.6167 / 0.6177 |
| exp / t3 | 0.5795 | 0.5780 / 0.5796 / 0.5793 / – | 0.6308 | 0.6306 / 0.6308 |
| t3 / Gaussian | 0.5736 | 0.5722 / 0.5727 / 0.5735 / 0.5738 | 0.4610 | 0.4608 / 0.4613 |
| t3 / t3 | 0.4952 | 0.4931 / 0.4948 / 0.4955 / 0.4952 | 0.4739 | 0.4740 / 0.4741 |
| Beta / Gaussian | 0.2149 | 0.2140 / 0.2147 / 0.2146 / 0.2149 | 0.3727 | 0.3735 / 0.3726 |
| Beta / t3 | 0.1528 | 0.1523 / 0.1525 / 0.1531 / – | 0.3889 | 0.3886 / 0.3889 |

Fixed-percentile precision does not depend on N for any shape, once $pN$ is not small. At $N=10^3$, $p=1\%$
(K=10) every shape sits 0.5 to 3 percent below its limit; that is the finite-K effect of §2.

---

## 11. Acceptance rate (item 11)

Let $z=z_\alpha$ and let $w(\alpha)=P(Y>z,X<z)$ be the wrong accepts per submitted paper, so
$\mathrm{swap}(\alpha)=w(\alpha)/\alpha$.

1. *Symmetry.* $(X,Y)\to(-X,-Y)$ and exchangeability give $w(\alpha)=w(1-\alpha)$. So the count of wrong
   accepts per submission is largest at $\alpha=1/2$.
2. *Monotonicity.* $\frac{d}{dz}P(X>z,Y<z)=-\phi(z)\Phi(\sqrt\beta z)+\phi(z)\bar\Phi(\sqrt\beta z)$ (exchangeability
   gives $P(X>z\mid Y=z)=\bar\Phi((1-\rho)z/\tau)$). With $dz/d\alpha=-1/\phi(z)$:
   $$w'(\alpha)=2\Phi(\sqrt\beta\,z_\alpha)-1,$$
   positive for $\alpha<1/2$ and decreasing in $\alpha$. So $w$ is concave with $w(0)=0$, and
   $\mathrm{swap}=w/\alpha$ strictly decreases on (0, 1).
3. *Limits.* $\alpha\to0$: $\mathrm{swap}\to1$ with $1-\mathrm{swap}\approx(1+\rho)^2\phi(\sqrt\beta z)/(\tau z)$. $\alpha\to1$: $\mathrm{swap}\to0$.
4. *High reliability* ($\tau\to0$, $t=\tau s$):
   $w=\tau\int_0^\infty\phi(z+\tau s)\Phi(\tau z/(1+\rho)-\rho s)\,ds=\tau\phi(z)/\sqrt{2\pi}+O(\tau^2)$, so
   $$\mathrm{swap}(\alpha)\approx\frac{\tau}{\sqrt{2\pi}}\,\frac{\phi(z_\alpha)}{\alpha}.$$
   The mistakes come from papers within about $\tau$ of the threshold. Per accepted paper their number is
   proportional to the inverse Mills ratio $\phi(z_\alpha)/\alpha$, which grows as $\alpha$ falls ($\approx z_\alpha$ for small
   $\alpha$). That is the reason a more selective venue swaps a larger share.
5. *Low reliability* (tetrachoric series $P_2=p^2+\phi(z)^2\sum_{n\ge1}\rho^nHe_{n-1}(z)^2/n!$):
   $\mathrm{swap}\approx1-\alpha-\rho\phi(z_\alpha)^2/\alpha$.
6. *Disagreement.* $d(\alpha)=\mathrm{swap}(\alpha)$ evaluated at correlation $\rho^2$: same monotonicity. The
   inconsistent share $2\alpha d=2w(\alpha;\rho^2)$ is symmetric about and largest at $\alpha=1/2$. Random decisions
   give $d=1-\alpha$.

Checks (`t_items123.out`): symmetry holds to $3\times10^{-16}$; swap is decreasing on a 49-point grid for
$\rho\in\{0.5,0.75,0.9\}$; argmax of $w$ at 0.50. Values at $\rho=0.75$:

| $\alpha$ | swap | high-rel. approx | disagreement | inconsistent share | random $d$ |
|---|---|---|---|---|---|
| 0.10 | 0.488 | 0.463 | 0.636 | 0.127 | 0.90 |
| 0.20 | 0.397 | 0.369 | 0.527 | 0.211 | 0.80 |
| 0.25 | 0.363 | 0.335 | 0.484 | 0.242 | 0.75 |
| 0.30 | 0.332 | 0.306 | 0.445 | 0.267 | 0.70 |
| 0.40 | 0.278 | 0.255 | 0.374 | 0.299 | 0.60 |

At $\rho=0.9$ the high-reliability form is within 2 to 3 percent (0.3052 vs 0.3114 at $\alpha=0.1$).

---

## 12. Discretisation (item 12)

**Why there is no closed form.** (a) A snapped review is a categorical variable with probabilities
$\pi_k(q)=\Phi((m_k-q)/\sigma_\varepsilon)-\Phi((m_{k-1}-q)/\sigma_\varepsilon)$ ($m_k$ = midpoints). The mean of R is a lattice
variable whose law is an R-fold convolution (a sum over compositions). (Q, S) is not bivariate normal, so
$P_2$ and the dependence on $\rho$ alone are lost: results depend on $\sigma_\varepsilon$, R, the grid and $\mu_q$
separately. (b) Ties: the top-K set depends on tie-breaking inside a score cell, so continuous
order-statistic and concomitant theory does not apply. (c) The score is bounded above; the top of its
distribution is a point mass (all R reviews at the top point), not a Gaussian tail.

**What can be said.**

1. *Fixed percentile, $N\to\infty$: exact semi-analytic limit* (`discrete.pct_limit`). Let $s_c$ be the cell
   that contains the cutoff, $P_{>}$ the mass above it and $\theta=(p-P_>)/P(S=s_c)$ the selected fraction of
   that cell. Then $\mathrm{prec}_\infty=\int_{q>q_p}f(q)[P(S>s_c\mid q)+\theta P(S=s_c\mid q)]dq/p$. It does not
   depend on N. Check ($R=4$, $\sigma_\varepsilon=2.171$, latent $\rho^2=0.55$, `t_disc_compare.out`):

   | scale | limit p=1% / 5% / $\alpha$=25% | simulator $N=10^6$ |
   |---|---|---|
   | continuous | 0.3080 / 0.4317 / 0.6311 | 0.3086 / 0.4318 / 0.6311 |
   | integer 1–10 | 0.2872 / 0.4224 / 0.6279 | 0.2861 / 0.4221 / 0.6280 |
   | five-point | 0.2793 / 0.4054 / 0.6147 | 0.2796 / 0.4054 / 0.6145 |
   | ICLR six-point | 0.2738 / 0.4144 / 0.6236 | 0.2740 / 0.4144 / 0.6237 |

   (A first version with the indicator $q>q_p$ inside a Riemann sum was off by 0.001; Gauss–Legendre nodes
   on $[q_p,\infty)$ fixed it.)
2. *Fine grids act like extra noise.* For spacing $h\ll\sigma_\varepsilon$, snapping adds about uniform noise of
   variance $h^2/12$ per review (Sheppard): $\rho^2\approx\sigma_q^2/(\sigma_q^2+\sigma_u^2+(\sigma_\varepsilon^2+h^2/12)/R)$. Check
   ($h=0.5$, $R=2$, $\sigma_\varepsilon=1.5$): p=1%: 0.3131 (snapped) vs 0.3146 (Sheppard) vs 0.3163 (unsnapped).
3. *Fixed K, large N: the top cell becomes a lottery.* Let $\pi_{\rm top}=P(\text{all R reviews at the top point})>0$.
   When $N\pi_{\rm top}\gg K$, $\mathrm{Top}_K$ is a uniform random K-subset of the $\approx N\pi_{\rm top}$ tied papers, so
   $$\mathrm{prec}_{N,K}\approx\bar p_{\rm top}\,\frac K{N\pi_{\rm top}}\propto\frac1N,$$
   with $\bar p_{\rm top}$ the probability that a true top paper lands in the top cell ($\to1$). This is faster than
   the continuous $N^{-\beta}$. Check (same setting): five-point $N=10^6$ ($N\pi_{\rm top}=449$): K=10 0.0072 vs
   0.0070 ± 0.0026, K=100 0.0422 vs 0.0431 ± 0.0022; ICLR six-point $10^6$, K=100: 0.0480 vs 0.0481 ± 0.0019;
   integer scale $10^6$ ($N\pi_{\rm top}=118$), K=10: 0.0158 vs 0.0220 ± 0.0048. $\pi_{\rm top}$ = 1.2e-4 (integer),
   3.5e-4 (ICLR), 4.5e-4 (five-point): the coarser the scale, the earlier the lottery starts. Simulated fixed-K
   precision at $N=10^6$, K=100: 0.130 continuous, 0.073 integer, 0.048 ICLR, 0.043 five-point.
4. Numbers for the study come from simulation with per-scale recalibration (§7.3); these checks used one
   $\sigma_\varepsilon$ for all scales.

---

## 13. Verification summary (item 13) and code review

**Simulator vs exact formulas.** `compare_sim2.md` compares the repository simulator (Gaussian model, R=1,
$\sigma_q=1$, $\sigma_\varepsilon=\sqrt{1/\rho^2-1}$; $\rho\in\{0.6,0.75,0.9\}$; $N\in\{10^3,10^4,10^5,10^6\}$ with
10,000 / 10,000 / 1,500 / 300 conferences; plus `simulate_best_paper` at $\rho=0.75$) with the exact formulas:
prec_K, ovl_K, pctl_K, c1pct_K, c5pct_K, c2x_K, c10x_K, prec_p, ovl_p, swap, dis, incons, best_in_K, winner
quantiles.

Result over 629 comparisons: mean z = −0.005, SD 0.996, share $|z|>2$ = 4.8 percent (normal: 4.6),
share $|z|>3$ = 0.8 percent (5 cases). The 5 cases:

* `c1pct_K100` at $N=1000$ ($\rho$ = 0.75, 0.9): here $K=100>M=10$ and the script used the
  fixed-population-threshold formula. The exact empirical-threshold value (§4.1 with caps 100 and 10) is
  0.084169 and 0.098655 against simulated 0.08406 ± 0.00012 and 0.09864 ± 0.00004 (−0.9 and −0.4 SE).
* `c2x_K5` (identical to `c1pct_K5`) and `prec_K5` at $\rho=0.9$, $N=1000$: one batch of 10,000 conferences,
  so these metrics are correlated. Reruns with 40,000 + 40,000 + 40,000 conferences give 0.48845, 0.48714,
  0.48633 (each ± 0.00096) for prec_K5, and 3.2 million conferences give 0.48853 ± 0.00011, against 0.48875.
* `c1pct_K100` at $\rho=0.9$, $N=10^4$ (+3.3 SE; fixed-threshold formula) and `prec_K100` there (+2.65 SE): a
  rerun with 20,000 conferences gives 0.54068 ± 0.00029 against 0.54091 (−0.8 SE).

A first pass (`compare_sim.md`) used the N-free acceptance formulas. There the acceptance metrics at
$\rho=0.9$, $N=1000$ sat 2.5 to 3 SE away, which is the $O(1/N)$ shift that §2 predicts; with the finite-N
formula they sit within 1 SE. Winner-rank quantiles: the exact cdf at the simulator's pooled quartiles is 0.24–0.37 / 0.49–0.54 /
0.71–0.79 (targets 0.25 / 0.5 / 0.75); the values far from 0.25 occur where the lower quartile is rank 1 or 2,
where the cdf jumps.

**Code review of the package** (read, not edited):

* `model.py`, `simulate.py`, `calibrate.py`: no bug found. The simulator reproduces every exact Gaussian result
  above, including finite-N effects of size $10^{-3}$.
* `analytic.Phi2`/`P2`/`P2_diag` (Owen's T) lose relative accuracy deep in the tail, where
  $P_2\ll10^{-7}\bar\Phi(\min(a,b))$: relative error $1.1\times10^{-6}$ at $(15,15;0.75)$, 8 percent at
  $(12,11;0.5)$, total loss at $(25,24;0.9)$. Inside the study's range ($z\le4.8$) the error is below
  $10^{-11}$. Asymptotic checks need a non-cancelling form; `core.P2` switches to Gauss–Laguerre there.
* `analytic.py` docstring points to `docs/derivations.md`, which does not exist (derivations are under
  `docs/derivations/`).
* `calibrate.NEURIPS2014_RAW` uses $\alpha=43.5/166$ while the committees accepted 44 and 43; the formula
  assumes equal counts. The effect is far below the sampling error.

**Open points.** (1) The first-order $1/\log N$ correction (§4.4 (i)) is asymptotically right but useless at
$N\le10^6$ for $\rho\ge0.75$; the practical formula of §4.6 is the recommended closed form there. (2) No
closed-form constant was derived for the Beta/Gaussian decay beyond the leading $(K/N)(\log N)^{a/2}$ form; the
independent-threshold integral gives the numbers. (3) For t3 quality with Gaussian noise the $N^{-1/3}$
deficit law is accurate only for $N\gtrsim10^6$ at K=10.
