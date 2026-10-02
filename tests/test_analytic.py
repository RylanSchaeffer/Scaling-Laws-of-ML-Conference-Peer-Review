"""Fast checks of the fixed-number formulas in analytic.py (handoff §6.2 to §6.9).

Each new function is checked against an exact small-N value (closed forms, 4-D orthant
probabilities, identities) or against a modest Monte Carlo run.
"""

import numpy as np
import pytest
from scipy import integrate, special, stats

from peerreview import analytic as an
from peerreview.model import ReviewModel
from peerreview.simulate import Selections, simulate

RHOS = (0.3, 0.7459, 0.9)


def _orthant4(rho, best):
    """N = 3: P(X1 > X2, X1 > X3, Y1 > Y2, Y1 > Y3); with best=True the Y inequalities are reversed."""
    C = np.array([[2, 1, 2 * rho, rho], [1, 2, rho, 2 * rho], [2 * rho, rho, 2, 1], [rho, 2 * rho, 1, 2]], float)
    if best:
        S = np.diag([1.0, 1.0, -1.0, -1.0])
        C = S @ C @ S
    return stats.multivariate_normal.cdf(np.zeros(4), np.zeros(4), C, abseps=1e-8, releps=1e-8, maxpts=2_000_000, rng=np.random.default_rng(0))


def _mc(N, rho, reps, seed=0):
    """Brute-force conferences: quality q, committee scores s and s2 (corr(s, s2) = rho^2)."""
    rng = np.random.default_rng(seed)
    tau = np.sqrt(1 - rho**2)
    q = rng.standard_normal((reps, N))
    s = rho * q + tau * rng.standard_normal((reps, N))
    s2 = rho * q + tau * rng.standard_normal((reps, N))
    rank = lambda x: (-x).argsort(1).argsort(1)  # 0 = best
    return q, s, rank(q), rank(s), rank(s2)


def _close(mc_values, exact, k=4.0):
    v = np.asarray(mc_values, float)
    se = v.std(ddof=1) / np.sqrt(v.size)
    assert abs(v.mean() - exact) < k * se + 1e-12, (v.mean(), exact, se)


# --- tail-accurate orthant ----------------------------------------------------


@pytest.mark.parametrize("a,b,r", [(11.0, 3.0, 0.7), (12.0, 11.0, 0.5), (9.0, -2.0, 0.6), (8.0, 8.0, 0.95), (10.0, 10.0, -0.5)])
def test_log_P2_far_tail(a, b, r):
    # P2 = int_a^inf phi(t) Phibar((b - r t)/tau) dt, integrated in w = t - a with the scale e^{-a w} removed.
    tau = np.sqrt(1 - r * r)
    f = lambda w: np.exp(-0.5 * w * w - a * w + special.log_ndtr(-(b - r * (a + w)) / tau))
    ref = np.log(integrate.quad(f, 0, 50, epsabs=0, epsrel=1e-13, limit=200)[0]) - 0.5 * a * a - 0.5 * np.log(2 * np.pi)
    assert abs(an.log_P2(a, b, r) - ref) < 1e-9


def test_log_P2_matches_owen_in_the_bulk():
    rng = np.random.default_rng(1)
    a, b = rng.uniform(-2, 4.5, 200), rng.uniform(-2, 4.5, 200)
    r = rng.uniform(-0.9, 0.95, 200)
    assert np.allclose(an.P2_tail(a, b, r), an.P2(a, b, r), rtol=1e-9, atol=1e-15)


# --- §6.4 exact fixed-K precision and containment -----------------------------


@pytest.mark.parametrize("rho", RHOS)
def test_precision_small_N_closed_forms(rho):
    assert abs(an.precision_fixed_K(2, 1, rho) - (0.5 + np.arcsin(rho) / np.pi)) < 1e-10
    p1, p2 = an.precision_fixed_K(3, 1, rho), an.precision_fixed_K(3, 2, rho)
    assert abs(p1 - 3 * _orthant4(rho, best=False)) < 2e-7
    assert abs(p2 - (1 + p1) / 2) < 1e-10  # |Top2 ∩ Top2| = 1 + 1{same bottom paper}


def test_independent_scores_give_KM_over_N():
    for N, K, M in [(10, 3, 3), (1000, 10, 50), (1e6, 5, 7), (1e50, 3, 3)]:
        assert abs(an.containment_fixed_K(N, K, M, 0.0) / (M / N) - 1) < 1e-9


def test_precision_vectorised_over_N_and_trivial_cases():
    v = an.precision_fixed_K([2, 10, 1000], 1, 0.5)
    assert v.shape == (3,) and np.all(np.diff(v) < 0)
    assert an.precision_fixed_K(5, 5, 0.5) == 1.0
    assert an.containment_fixed_K(10, 3, 10, 0.5) == 1.0


def test_precision_containment_overlap_rejection_against_monte_carlo():
    N, rho, K, M, reps = 20, 0.8, 4, 8, 100_000
    q, s, rq, rs, rs2 = _mc(N, rho, reps, seed=3)
    top = rs < K
    _close(((top & (rq < K)).sum(1)) / K, an.precision_fixed_K(N, K, rho))
    _close(((top & (rq < M)).sum(1)) / K, an.containment_fixed_K(N, K, M, rho))
    _close(((top & (rs2 < K)).sum(1)) / K, an.overlap_fixed_K(N, K, rho))
    A = int(round(0.25 * N))
    _close(((top & (rs2 >= A)).sum(1)) / K, an.rejected_given_top(N, K, 0.25, rho))
    _close((special.ndtr(q) * top).sum(1) / K, an.mean_true_percentile(N, K, rho))


def test_large_M_branch_matches_small_M_branch(monkeypatch):
    a = an.rejected_given_top(4000, 5, 0.25, 0.7459)
    monkeypatch.setattr(an, "_MSMALL", 10)  # force betaincc for the quality window
    an._axis.cache_clear()
    b = an.rejected_given_top(4000, 5, 0.25, 0.7459)
    assert abs(a - b) < 1e-9


# --- §6.4 large-N laws and local slope -----------------------------------------


@pytest.mark.parametrize("rho,K", [(0.5, 1), (0.7459, 10)])
def test_asymptotic_law_at_huge_N(rho, K):
    N = 1e200
    ex = an.precision_fixed_K(N, K, rho)
    lead = an.precision_fixed_K_asymptotic(N, K, rho, order=0)
    corr = an.precision_fixed_K_asymptotic(N, K, rho, order=1)
    pure = an.precision_fixed_K_asymptotic(N, K, rho, order=0, form="logN")
    assert abs(ex / lead - 1) < 0.01 and abs(ex / pure - 1) < 0.01
    assert abs(ex / corr - 1) < 2e-4 < abs(ex / lead - 1)
    # The 1/b_N^2 coefficient: b^2 (exact / (lead (1 + omega eps)) - 1) = beta_K + gamma/b^2 + ..., gamma < 150 here.
    b2 = an.b_N(N) ** 2
    y = b2 * (ex / (lead * (1 + an.omega_K(K, rho) * np.exp(an.log_eps_N(N, rho)))) - 1)
    assert abs(y - an.beta_K(K, rho)) < 150.0 / b2


def test_general_KM_correction():
    assert abs(an.beta_KM(7, 7, 0.6) - an.beta_K(7, 0.6)) < 1e-12
    assert abs(an.omega_KM(7, 7, 0.6) - an.omega_K(7, 0.6)) < 1e-12
    # Top_K(S) in Top_M(Q) at N = 1e100: the corrected law removes the 1/b_N^2 error of the leading law.
    ex = an.containment_fixed_K(1e100, 10, 20, 0.75)
    lead = an.containment_fixed_K_asymptotic(1e100, 10, 20, 0.75)
    corr = an.containment_fixed_K_asymptotic(1e100, 10, 20, 0.75, order=1)
    assert abs(ex / corr - 1) < 1e-3 < abs(ex / lead - 1)


def test_far_tail_p_down_to_1e_minus_7():
    # p = K/N = 1e-7: closed forms against the exact integral; exact rho = 0 value K/N.
    for rho in (0.3, 0.9):
        ex = an.precision_fixed_K(1e8, 10, rho)
        assert abs(an.precision_pct_finite(1e8, 1e-7, rho) / ex - 1) < 2e-3
        assert abs(an.precision_fixed_K_hybrid(1e8, 10, rho) / ex - 1) < 5e-3
    assert abs(an.precision_fixed_K(1e7, 1, 0.0) / 1e-7 - 1) < 1e-9
    # A tiny containment miss rate is computed without cancellation.
    miss = an.containment_miss(1e20, 10, 0.01, 0.9)
    assert 0 < miss < 1e-39 and abs(an.containment_miss_asymptotic(1e20, 10, 0.01, 0.9) / miss - 1) < 0.01
    assert abs(an.containment_miss(1e4, 10, 0.01, 0.7459) + an.containment_limit(10, 0.01, 0.7459, N=1e4) - 1) < 1e-12


def test_hybrid_formula_and_finite_K_factor():
    assert abs(an.finite_K_factor(1, 0.5) - (special.gamma(1 + 2 / 3) ** 2)) < 1e-12
    for N, K in [(1e4, 10), (1e6, 30)]:
        assert abs(an.precision_fixed_K_hybrid(N, K, 0.7459) / an.precision_fixed_K(N, K, 0.7459) - 1) < 0.003


def test_local_slope():
    assert abs(an.local_loglog_slope(1e4, 5, 0.0) + 1.0) < 1e-6  # random selection: K/N
    lo, hi = an.precision_fixed_K([1e4 * np.exp(-0.02), 1e4 * np.exp(0.02)], 10, 0.7459)
    assert abs(an.local_loglog_slope(1e4, 10, 0.7459) - np.log(hi / lo) / 0.04) < 1e-9
    s = an.local_loglog_slope([1e3, 1e6], 10, 0.7459)
    beta = (1 - 0.7459) / (1 + 0.7459)
    assert s[0] < s[1] < -beta  # steeper than the asymptote, approaching it
    assert abs(an.local_loglog_slope(1e300, 1, 0.5, method="leading") + 1 / 3) < 0.003


# --- §6.2 finite-N fixed percentile ----------------------------------------------


def test_precision_pct_finite_N_correction():
    for N, K, rho in [(1000, 10, 0.75), (400, 20, 0.9), (300, 15, 0.5)]:
        ex = an.precision_fixed_K(N, K, rho)
        lim = float(an.precision_pct(K / N, rho))
        cf = an.precision_pct_finite(N, K / N, rho)
        assert abs(cf - ex) < 0.05 * abs(ex - lim)  # captures at least 95% of the finite-N shift


# --- §6.5 mechanism helpers -------------------------------------------------------


def test_mechanism_helpers():
    assert abs(an.expected_kth_best(2, 1) - 1 / np.sqrt(np.pi)) < 1e-10
    assert abs(an.expected_kth_best(3, 2)) < 1e-10  # median of three
    assert abs(an.expected_kth_best(3, 1) - 1.5 / np.sqrt(np.pi)) < 1e-10
    rng = np.random.default_rng(5)
    srt = -np.sort(-rng.standard_normal((100_000, 100)), axis=1)
    for K in (1, 10):
        _close(srt[:, K - 1], an.expected_kth_best(100, K))
    assert an.conditional_quality_mean(2.0, 0.6) == pytest.approx(1.2)
    assert an.conditional_quality_sd(0.6) == pytest.approx(0.8)
    assert an.true_topK_threshold(1000, 10, kind="quantile") == pytest.approx(float(an.z_upper(0.01)))
    assert an.true_topK_threshold(1000, 10) == pytest.approx(an.expected_kth_best(1000, 10))
    g = an.mechanism_gap(1e4, 10, 0.75, i=1)
    assert g == pytest.approx((an.expected_kth_best(1e4, 10) - 0.75 * an.expected_kth_best(1e4, 1)) / np.sqrt(1 - 0.75**2))


# --- §6.6 containment limit ----------------------------------------------------------


def test_containment_limit():
    assert an.containment_limit(10, 0.01, 0.75) == 1.0
    assert an.containment_limit(10, 0.01, 0.0) == 0.01
    N = 1e4
    pop = an.containment_limit(10, 0.01, 0.7459, N=N)
    ex = an.containment_fixed_K(N, 10, int(round(0.01 * N)), 0.7459)
    assert abs(pop - ex) < 1e-3
    vals = an.containment_limit(10, 0.01, 0.7459, N=[1e3, 1e6, 1e12])
    assert np.all(np.diff(vals) > 0) and vals[-1] > 0.9999
    miss = 1 - an.containment_limit(1, 0.01, 0.5, N=1e20)
    assert abs(an.containment_miss_asymptotic(1e20, 1, 0.01, 0.5) / miss - 1) < 0.05


# --- §6.7 best paper; §6.8 winner rank -----------------------------------------------


@pytest.mark.parametrize("rho", RHOS)
def test_best_paper_small_N(rho):
    assert abs(an.best_paper_prob(2, 1, rho) - (0.5 + np.arcsin(rho) / np.pi)) < 1e-10
    assert abs(an.best_paper_prob(3, 2, rho) - (1 - 3 * _orthant4(rho, best=True))) < 2e-7
    assert abs(an.best_paper_prob(50, 1, rho) - an.precision_fixed_K(50, 1, rho)) < 1e-9


def test_best_paper_poisson_route_and_law():
    ex = an.best_paper_prob(1e4, 10, 0.7459)
    po = an.best_paper_prob(1e4, 10, 0.7459, method="poisson")
    assert 0 < abs(po / ex - 1) < 1e-4
    N = 1e100
    assert abs(an.best_paper_prob(N, 1, 0.5) / an.best_paper_prob_asymptotic(N, 1, 0.5) - 1) < 0.01
    assert an.best_paper_prob_asymptotic(N, 1, 0.5) == pytest.approx(an.precision_fixed_K_asymptotic(N, 1, 0.5))


def test_best_paper_and_winner_rank_against_monte_carlo():
    N, rho, reps = 40, 0.6, 60_000
    q, s, rq, rs, _ = _mc(N, rho, reps, seed=11)
    rows = np.arange(reps)
    best_rank = rs[rows, q.argmax(1)]
    for K in (1, 5):
        _close(best_rank < K, an.best_paper_prob(N, K, rho))
    w = rq[rows, s.argmax(1)] + 1
    cdf = an.winner_rank_cdf(N, rho, [1, 3, 8])
    for r, c in zip((1, 3, 8), cdf):
        _close(w <= r, c)
    med = an.winner_rank_quantile(N, rho, 0.5)
    assert cdf[1] < 0.5 <= cdf[2] and 3 < med <= 8
    assert np.median(w) in (med - 1, med, med + 1)


def test_winner_median_asymptotics():
    exact = an.winner_rank_quantile(1e5, 0.7459, 0.5)  # 55
    assert abs(an.winner_rank_median_asymptotic(1e5, 0.7459) / exact - 1) < 0.08
    assert abs(an.winner_rank_median_asymptotic(1e5, 0.7459, form="power") / exact - 1) < 0.15


# --- the repository simulator against the exact values -------------------------------


def test_simulator_matches_exact_fixed_K():
    rho = 0.7459
    m = ReviewModel(R=1, sigma_q=1.0, sigma_eps=float(np.sqrt(1 / rho**2 - 1)))
    sel = Selections(fixed_K=(5, 10), pct=(0.01,), alphas=(), best_K=(1, 5), alpha_ref=0.25)
    N = 2000
    row = simulate(m, N, reps=2000, sel=sel, seed=20261002)
    checks = {
        "prec_K10": an.precision_fixed_K(N, 10, rho),
        "c2x_K10": an.containment_fixed_K(N, 10, 20, rho),
        "c1pct_K5": an.containment_fixed_K(N, 5, 20, rho),
        "ovl_K10": an.overlap_fixed_K(N, 10, rho),
        "rej2_K10": an.rejected_given_top(N, 10, 0.25, rho),
        "pctl_K5": an.mean_true_percentile(N, 5, rho),
        "prec_p1pct": an.precision_fixed_K(N, 20, rho),
        "best_in_K1": an.best_paper_prob(N, 1, rho),
        "best_in_K5": an.best_paper_prob(N, 5, rho),
    }
    for name, exact in checks.items():
        assert abs(row[name] - exact) < 4.5 * row[f"{name}_se"] + 1e-4, (name, row[name], exact)


# --- rho near +-1, tails and edge cases ---------------------------------------------------


@pytest.mark.parametrize("rho", (0.96, 0.99, 0.999, 0.99999))
def test_ridge_grid_near_rho_one(rho):
    # N = 2 closed form; N = 3 identity; values stay in [0, 1] and increase to 1 with rho.
    exact2 = 0.5 + np.arcsin(rho) / np.pi
    assert abs(an.precision_fixed_K(2, 1, rho) - exact2) < 1e-10
    assert abs(an.best_paper_prob(2, 1, rho) - exact2) < 1e-10
    p1, p2 = an.precision_fixed_K(3, 1, rho), an.precision_fixed_K(3, 2, rho)
    assert abs(p2 - (1 + p1) / 2) < 1e-10
    for N, K in [(1000, 10), (1e6, 10)]:
        lo, hi = an.precision_fixed_K(N, K, 0.95), an.precision_fixed_K(N, K, rho)
        assert 0 < lo < hi < 1
        b = an.best_paper_prob(N, K, rho)
        assert hi < b <= 1 + 1e-12
    c95, c = an.containment_fixed_K(1e4, 10, 100, 0.95), an.containment_fixed_K(1e4, 10, 100, rho)
    assert c95 < c <= 1 + 1e-12


def test_ridge_grid_matches_product_grid(monkeypatch):
    # Where the product grid is converged (|rho| <= 0.95), the ridge grid must give the same value.
    for N, K, M, rho in [(1000, 10, 10, 0.9), (1e6, 5, 30, 0.95), (50, 3, 7, 0.93), (1e30, 1, 1, 0.9)]:
        grid = an._count_topK_topM(N, K, M, rho)
        monkeypatch.setattr(an, "_RIDGE_RHO", -1.0)
        ridge = an._count_topK_topM(N, K, M, rho)
        monkeypatch.setattr(an, "_RIDGE_RHO", 0.95)
        assert abs(ridge / grid - 1) < 1e-9, (N, K, M, rho, grid, ridge)


def test_near_one_against_monte_carlo():
    N, rho, K, reps = 30, 0.999, 3, 100_000
    q, s, rq, rs, _ = _mc(N, rho, reps, seed=21)
    top = rs < K
    _close(((top & (rq < K)).sum(1)) / K, an.precision_fixed_K(N, K, rho))
    best_rank = rs[np.arange(reps), q.argmax(1)]
    _close(best_rank < K, an.best_paper_prob(N, K, rho))


def test_closed_values_at_rho_plus_minus_one():
    assert an.precision_fixed_K(1000, 10, 1.0) == 1.0
    assert an.best_paper_prob(1000, 10, 1.0) == 1.0
    assert an.containment_fixed_K(1000, 10, 4, 1.0) == pytest.approx(0.4)
    assert an.precision_fixed_K(1000, 10, -1.0) == 0.0
    assert an.precision_fixed_K(12, 10, -1.0) == pytest.approx(0.8)  # 2K - N = 8 shared papers
    assert an.best_paper_prob(1000, 10, -1.0) == 0.0
    assert an.overlap_fixed_K(1000, 10, -1.0) == 1.0  # rho^2 = 1


def test_edge_cases():
    with pytest.raises(ValueError):
        an.precision_fixed_K(1000, 0, 0.5)
    with pytest.raises(ValueError):
        an.precision_fixed_K(1000, 2.5, 0.5)
    with pytest.raises(ValueError):
        an.precision_fixed_K(1000, 10, 1.5)
    with pytest.raises(ValueError):
        an.expected_kth_best(10, 20)
    with pytest.raises(ValueError):
        an.winner_rank_median_asymptotic(1e4, 0.0, form="power")
    assert an.winner_rank_median_asymptotic(1e4, 0.0) == pytest.approx(5000.0)
    assert an.rejected_given_top(1000, 10, 0.0001, 0.7) == 1.0  # A = 0
    assert an.containment_fixed_K(1000, 10, 0, 0.5) == 0.0
    assert an.best_paper_prob(1000, 0, 0.5) == 0.0
    assert float(an.Phi2(np.inf, 1.0, 0.5)) == pytest.approx(special.ndtr(1.0))
    assert float(an.Phi2(-np.inf, 1.0, 0.5)) == 0.0
    assert float(an.P2(np.inf, np.inf, 0.5)) == 0.0 and float(an.P2(-np.inf, -np.inf, 0.5)) == 1.0
    assert float(an.log_P2(-np.inf, 1.0, 0.5)) == pytest.approx(special.log_ndtr(-1.0))
    assert an.precision_pct_finite(1000, 1.0, 0.7) == 1.0
    assert np.isnan(an.precision_pct_finite(1000, 1e-4, 0.7))
    assert an.precision_pct_finite(1000, 0.01, 1.0) == 1.0
    assert float(an.precision_pct(0.0, 0.5)) == 0.0 and float(an.swap_fraction(0.0, 0.5)) == 1.0
    assert an.invert_disagreement(0.25, 0.0) == 1.0
    assert abs(an.invert_disagreement(0.25, float(an.disagreement(0.25, 0.4))) - 0.4) < 1e-9


def test_tail_orthant_relative_accuracy():
    # Tiny fixed-percentile precision: Owen's diagonal form cancels; the value must track log_P2.
    for p, r in [(1e-30, 0.3), (1e-100, 0.3), (1e-300, 0.7), (1e-20, -0.5)]:
        z = float(an.z_upper(p))
        assert abs(float(an.precision_pct(p, r)) / np.exp(float(an.log_P2(z, z, r)) - np.log(p)) - 1) < 1e-9
    # Strongly negative r with thresholds below 3: Owen's T alone returns -inf here.
    for a, b, r in [(2.9, 2.9, -0.9), (2.5, 2.5, -0.99), (2.0, -1.0, -0.99), (5.0, 5.0, -0.99), (3.0, 3.0, 0.99999)]:
        tau = np.sqrt(1 - r * r)
        f = lambda w: np.exp(-0.5 * w * w - a * w + special.log_ndtr(-(b - r * (a + w)) / tau) - lmax)
        grid = np.linspace(0, 50, 200_001)
        lmax = np.max(-0.5 * grid**2 - a * grid + special.log_ndtr(-(b - r * (a + grid)) / tau))
        pts = grid[np.argmax(-0.5 * grid**2 - a * grid + special.log_ndtr(-(b - r * (a + grid)) / tau))]
        val = integrate.quad(f, 0, 50, points=[pts], epsabs=0, epsrel=1e-12, limit=500)[0]
        ref = np.log(val) + lmax - 0.5 * a * a - 0.5 * np.log(2 * np.pi)
        assert abs(float(an.log_P2(a, b, r)) - ref) < 1e-8, (a, b, r)


def test_best_paper_first_order_law():
    # P_best(N, K) = E|Top_K(S) ∩ Top_1(Q)|, so its first correction is beta_KM(K, 1), omega_KM(K, 1).
    assert abs(an.best_paper_prob(1e4, 10, 0.7459) / (10 * an.containment_fixed_K(1e4, 10, 1, 0.7459)) - 1) < 1e-9
    for N in (1e100, 1e300):
        ex = an.best_paper_prob(N, 5, 0.5)
        lead = an.best_paper_prob_asymptotic(N, 5, 0.5)
        corr = an.best_paper_prob_asymptotic(N, 5, 0.5, order=1)
        assert abs(ex / corr - 1) < 3e-4 < abs(ex / lead - 1)
    assert an.best_paper_prob_asymptotic(1e100, 7, 0.6, order=1) == pytest.approx(
        7 * an.containment_fixed_K_asymptotic(1e100, 7, 1, 0.6, order=1))


def test_precision_pct_finite_small_K_error():
    # The closed form's relative error is O(1/K^2): about -1 % at K = 3, below 1e-4 from K = 30.
    rho = np.sqrt(0.85)
    e3 = an.precision_pct_finite(1000, 0.003, rho) / an.precision_fixed_K(1000, 3, rho) - 1
    e30 = an.precision_pct_finite(1000, 0.03, rho) / an.precision_fixed_K(1000, 30, rho) - 1
    assert -0.012 < e3 < -0.008 and abs(e30) < 1.5e-4
