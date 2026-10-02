"""Closed forms for the Gaussian model (handoff §6).

Standardised units: Q* = (q - mu_q)/sigma_q and S* the standardised score, so
(Q*, S*) is standard bivariate normal with correlation rho = sqrt(rho2).
Two committees' standardised scores of the same paper have correlation rho2
when the shared noise u is redrawn for the second committee.

The first part holds the basic results (§6.1 to §6.3). The second part holds
fixed-number selection (§6.4 to §6.9): exact finite-N integrals, large-N laws
and the mechanism helpers. The derivations and their numerical checks live in
docs/derivations.md.
"""

from __future__ import annotations

import functools

import numpy as np
from scipy import optimize, special

# ---------------------------------------------------------------------------
# §6.1 Reliability
# ---------------------------------------------------------------------------


def rho2(sigma_eps, R, sigma_q=1.2, sigma_u=0.0):
    """Reliability corr(score, quality)^2 = sq^2 / (sq^2 + su^2 + se^2/R)."""
    sigma_eps, R = np.asarray(sigma_eps, float), np.asarray(R, float)
    return sigma_q**2 / (sigma_q**2 + sigma_u**2 + sigma_eps**2 / R)


def committee_corr(sigma_eps, R, sigma_q=1.2, sigma_u=0.0, share_u=False):
    """corr(s1, s2) for two committees scoring the same paper.

    With u redrawn (the default, as in the field experiments) this equals rho2.
    With u shared it is (sq^2 + su^2) / (sq^2 + su^2 + se^2/R).
    """
    num = sigma_q**2 + (sigma_u**2 if share_u else 0.0)
    return num / (sigma_q**2 + sigma_u**2 + np.asarray(sigma_eps, float) ** 2 / np.asarray(R, float))


def rho2_limit(sigma_q=1.2, sigma_u=0.0):
    """Upper bound on rho2 as R -> infinity: sq^2 / (sq^2 + su^2)."""
    return sigma_q**2 / (sigma_q**2 + sigma_u**2)


def sigma_eps_for_rho2(target_rho2, R, sigma_q=1.2, sigma_u=0.0):
    """Invert rho2(): the reviewer SD that gives reliability target_rho2 (NaN if unreachable)."""
    t = np.asarray(target_rho2, float)
    var = np.asarray(R, float) * (sigma_q**2 / t - sigma_q**2 - sigma_u**2)
    return np.where(var >= 0, np.sqrt(np.maximum(var, 0.0)), np.nan)


def spearman_brown(r, R):
    """Reliability of the mean of R parallel measurements whose pairwise correlation is r."""
    r, R = np.asarray(r, float), np.asarray(R, float)
    return R * r / (1.0 + (R - 1.0) * r)


# ---------------------------------------------------------------------------
# Bivariate normal orthant probability
# ---------------------------------------------------------------------------


def Phi2(h, k, r):
    """P(X < h, Y < k) for a standard bivariate normal with correlation r (vectorised).

    Owen (1956): Phi2 = (Phi(h) + Phi(k))/2 - T(h, a_h) - T(k, a_k) - beta, with
    a_h = (k - r h) / (h sqrt(1 - r^2)), a_k = (h - r k) / (k sqrt(1 - r^2)),
    beta = 1/2 when h k < 0 (or h k = 0 and h + k < 0), else 0.
    """
    h, k, r = np.broadcast_arrays(*(np.asarray(x, float) for x in (h, k, r)))
    tiny = 1e-300
    hh = np.where(h == 0, tiny, h)
    kk = np.where(k == 0, tiny, k)
    sq = np.sqrt(np.maximum(1.0 - r * r, 0.0))
    with np.errstate(divide="ignore", invalid="ignore"):
        ah = (kk - r * hh) / (hh * sq)
        ak = (hh - r * kk) / (kk * sq)
    beta = np.where((h * k < 0) | ((h * k == 0) & (h + k < 0)), 0.5, 0.0)
    with np.errstate(invalid="ignore"):
        out = 0.5 * (special.ndtr(h) + special.ndtr(k)) - special.owens_t(hh, ah) - special.owens_t(kk, ak) - beta
    # Degenerate correlations.
    out = np.where(r >= 1.0, special.ndtr(np.minimum(h, k)), out)
    out = np.where(r <= -1.0, np.maximum(special.ndtr(h) + special.ndtr(k) - 1.0, 0.0), out)
    # Infinite thresholds reduce to a margin.
    out = np.where(h == np.inf, special.ndtr(k), out)
    out = np.where(k == np.inf, special.ndtr(h), out)
    out = np.where((h == -np.inf) | (k == -np.inf), 0.0, out)
    return out


def P2(a, b, r):
    """Upper orthant P(X > a, Y > b) for a standard bivariate normal with correlation r.

    Owen's T: the absolute error is about 1e-16, so the relative accuracy is lost when
    P2 is far below the margins (far tail, or strongly negative r). Use P2_tail there.
    """
    return Phi2(-np.asarray(a, float), -np.asarray(b, float), r)


def _log_P2_diag(a, r):
    """log P(X > a, Y > a): Owen's diagonal form, or log_P2 where that form loses relative accuracy."""
    a, r = np.broadcast_arrays(np.asarray(a, float), np.asarray(r, float))
    with np.errstate(divide="ignore", invalid="ignore"):
        v = special.ndtr(-a) - 2.0 * special.owens_t(a, np.sqrt((1.0 - r) / (1.0 + r)))
        out = np.log(np.maximum(v, 0.0))
    # Phibar(a) - 2T cancels (relative error about 3e-14 Phibar(a)/P2): use log_P2 once P2 < 1e-3 Phibar(a).
    bad = np.isfinite(a) & (a > 0.25) & (np.abs(r) < 1.0) & (v < 1e-3 * special.ndtr(-a))
    if bad.any():
        out = np.array(out, copy=True)
        out[bad] = log_P2(a[bad], a[bad], r[bad])
    return out


def P2_diag(a, r):
    """P(X > a, Y > a) = Phibar(a) - 2 T(a, sqrt((1-r)/(1+r))).

    Where this difference cancels (P2 < 1e-3 Phibar(a): tiny tail probabilities, small or
    negative r) the value comes from log_P2 instead, so it keeps about 1e-9 relative accuracy
    or better for every a > 0.25. Below 1e-308 it underflows to 0; precision_pct works in log space.
    """
    return np.exp(_log_P2_diag(a, r))


def z_upper(p):
    """z_p = Phi^{-1}(1 - p)."""
    return -special.ndtri(np.asarray(p, float))


# ---------------------------------------------------------------------------
# §6.2 Fixed-percentile precision and swap fraction (N-free in the large-N limit)
# ---------------------------------------------------------------------------


def precision_pct(p, rho):
    """Large-N (N -> infinity) precision of the top-p set: P2(z_p, z_p; rho) / p.

    This is a limit. At finite N the expected precision of the top K = round(pN) papers is
    lower by a relative kappa(p, rho)/K + O(K^-2), with kappa -> -rho/(1+rho)^2 as p -> 0
    (between -0.25/K and -0.08/K for p <= 25 %; docs/derivations.md §2.3). For K < 30 use
    precision_fixed_K(N, round(pN), rho), or precision_pct_finite from K = 10.
    The value is computed in log space, so it stays accurate for p down to 1e-300.
    p = 0 gives the limit 0 (1 at rho = 1).
    """
    p, rho = np.broadcast_arrays(np.asarray(p, float), np.asarray(rho, float))
    with np.errstate(divide="ignore", invalid="ignore"):
        out = np.exp(_log_P2_diag(z_upper(p), rho) - np.log(p))
    return np.where(p == 0, np.where(rho >= 1.0, 1.0, 0.0), out)[()]


def swap_fraction(alpha, rho):
    """Share of accepted papers not in the true top alpha N (= share of deserving rejected).

    The N -> infinity limit; at finite N it is higher by the O(1/K) deficit of precision_pct.
    """
    return 1.0 - precision_pct(alpha, rho)


# ---------------------------------------------------------------------------
# §6.3 Two-committee disagreement
# ---------------------------------------------------------------------------


def disagreement(alpha, r12):
    """P(rejected by committee 2 | accepted by committee 1) at acceptance rate alpha.

    r12 is the correlation between the committees' scores (= rho2 when u is redrawn).
    The N -> infinity limit; at finite N it is higher by the O(1/K) deficit of precision_pct
    (K = round(alpha N)); use 1 - precision_fixed_K(N, K, r12) for small K.
    """
    return 1.0 - precision_pct(alpha, r12)


def inconsistent_share(alpha, r12):
    """Share of all papers accepted by exactly one committee = 2 alpha * disagreement."""
    return 2.0 * np.asarray(alpha, float) * disagreement(alpha, r12)


def invert_disagreement(alpha, dis):
    """r12 such that disagreement(alpha, r12) = dis (scalar); NaN if dis is out of reach.

    The bracket is the closed interval [-1, 1]: dis = 0 gives r12 = 1.
    """
    f = lambda r: float(disagreement(alpha, r)) - dis
    lo, hi = -1.0, 1.0
    flo, fhi = f(lo), f(hi)
    if flo * fhi > 0:
        return np.nan
    if fhi == 0.0:
        return hi
    if flo == 0.0:
        return lo
    return optimize.brentq(f, lo, hi, xtol=1e-12)


def invert_inconsistent(alpha, incons):
    """r12 such that inconsistent_share(alpha, r12) = incons (scalar)."""
    return invert_disagreement(alpha, incons / (2.0 * alpha))


# ===========================================================================
# Part 2: fixed-number selection (§6.4 to §6.9)
#
# Notation (docs/derivations.md): (Q*, S*) standard bivariate normal with
# correlation rho; tau = sqrt(1 - rho^2); c = 1/(1 + rho); kappa = rho/(1 + rho);
# beta = (1 - rho)/(1 + rho) = c - kappa; b_N = Phibar^{-1}(1/N);
# eps_N = exp(kappa b_N^2) / (N tau); I_n = Gamma(n + c) / (c Gamma(n)).
# The finite-N functions are exact integrals, evaluated by composite
# Gauss-Legendre quadrature in tail coordinates (relative error about 1e-9);
# for |rho| > 0.95 the inner variable is the rotated coordinate (x - rho y)/tau.
# They take a scalar or an array of N; N may be as large as 1e300.
# ===========================================================================

_LOG_2PI = np.log(2.0 * np.pi)
_MSMALL = 3000  # binomial cdfs up to this count are summed term by term in log space


def _log_phi(x):
    """log phi(x) = -x^2/2 - log(2 pi)/2."""
    return -0.5 * np.asarray(x, float) ** 2 - 0.5 * _LOG_2PI


@functools.lru_cache(maxsize=None)
def _gl(n: int):
    """Gauss-Legendre nodes and weights on [-1, 1]."""
    return np.polynomial.legendre.leggauss(n)


def _panels(breaks, n: int):
    """Composite Gauss-Legendre nodes and weights on consecutive panels (either direction)."""
    b = np.asarray(breaks, float)
    x0, w0 = _gl(n)
    half = 0.5 * np.diff(b)[:, None]
    mid = 0.5 * (b[1:] + b[:-1])[:, None]
    return (mid + half * x0).ravel(), (np.abs(half) * w0).ravel()


def _over_N(N, fn):
    """Apply a scalar-N function elementwise over N (a float for scalar N)."""
    arr = np.asarray(N, float)
    out = np.array([fn(float(v)) for v in arr.ravel()]).reshape(arr.shape)
    return float(out) if out.ndim == 0 else out


def _consts(rho):
    """(tau, c, kappa, beta) for correlation rho."""
    rho = float(rho)
    return np.sqrt(1.0 - rho * rho), 1.0 / (1.0 + rho), rho / (1.0 + rho), (1.0 - rho) / (1.0 + rho)


# ---------------------------------------------------------------------------
# Tail-accurate bivariate normal orthant and binomial helpers
# ---------------------------------------------------------------------------

_W_BREAKS = np.array([0, 0.25, 0.5, 1, 2, 4, 8, 16, 32, 64, 128.0])
_W_X, _W_W = _panels(_W_BREAKS, 10)
_W_LOGW = np.log(_W_W)
# Extra breakpoints for hard cases, in units of the transition width (around its centre)
# and of the decay length 1/(1 + lambda) (from w = 0).
_W_STEP = np.array([-8, -4, -2, -1, -0.5, 0, 0.5, 1, 2, 4, 8.0])
_W_DECAY = np.array([0.25, 0.5, 1, 2, 4, 8, 16, 32.0])


def _log_P2_integral(h, k, r):
    """log P2 for h = max > 0 by the tail integral in w = h (t - h) (1-D arrays, |r| < 1).

    The integrand is exp(-w - w^2/(2h^2)) Phibar(z(w)), z = (k - r(h + w/h))/tau. Two features
    can be narrower than the fixed panels: the step of Phibar(z) at w_c = h(k - r h)/r, of width
    h tau/|r| (r near +-1), and the decay rate lambda = hazard(z(0)) |r|/(h tau) at w = 0 (r < 0).
    For those elements the panels are refined around both.
    """
    tau = np.sqrt(1.0 - r * r)
    out = np.empty(h.size)
    with np.errstate(divide="ignore", invalid="ignore"):
        width = np.where(r != 0, h * tau / np.abs(r), np.inf)
        wc = np.where(r != 0, h * (k - r * h) / r, 0.0)
        z0 = (k - r * h) / tau
        hazard = np.exp(_log_phi(z0) - special.log_ndtr(-z0))
        lam = np.where(r < 0, hazard * (-r) / (h * tau), 0.0)
    # Hard: the step is narrower than a tenth of the fixed panel around it, or the decay is fast.
    hard = (width < 0.1 * np.maximum(1.0, np.clip(wc, 0.0, _W_BREAKS[-1]))) | (lam > 10.0)
    for sel, refine in ((~hard, False), (hard, True)):
        idx = np.flatnonzero(sel)
        for s in range(0, idx.size, 20_000):
            i = idx[s : s + 20_000]
            hh, kk, rr, tt = h[i, None], k[i, None], r[i, None], tau[i, None]
            if refine:
                wb = np.concatenate([np.broadcast_to(_W_BREAKS, (i.size, _W_BREAKS.size)),
                                     np.where(np.isfinite(width[i, None]), wc[i, None] + width[i, None] * _W_STEP, 0.0),
                                     _W_DECAY / (1.0 + lam[i, None])], axis=1)
                wb = np.sort(np.clip(wb, 0.0, _W_BREAKS[-1]), axis=1)
                x0, w0 = _gl(10)
                half = 0.5 * np.diff(wb, axis=1)
                mid = 0.5 * (wb[:, 1:] + wb[:, :-1])
                wx = (mid[:, :, None] + half[:, :, None] * x0).reshape(i.size, -1)
                with np.errstate(divide="ignore"):
                    lw = np.log((half[:, :, None] * w0).reshape(i.size, -1))
            else:
                wx, lw = _W_X[None, :], _W_LOGW[None, :]
            z = (kk - rr * (hh + wx / hh)) / tt
            g = lw - wx - 0.5 * (wx / hh) ** 2 + special.log_ndtr(-z)
            out[i] = special.logsumexp(g, axis=1) + _log_phi(h[i]) - np.log(h[i])
    return out


def log_P2(a, b, r):
    """log P(X > a, Y > b), accurate in relative terms far in the tail.

    Owen's T (P2) when max(a, b) < 3. Otherwise, with h = max(a, b), k = min(a, b):
    P2 = (phi(h)/h) int_0^inf exp(-w - w^2/(2h^2)) Phibar((k - r(h + w/h)) / sqrt(1 - r^2)) dw,
    with panels refined where the integrand has a narrow step or decay (|r| near 1).
    Owen's T has an absolute error of about 1e-16, so for r < 0 an Owen value below 1e-7
    (with h > 0.25) is replaced by the integral too. Relative accuracy: about 1e-12 on the
    integral branch, and 1e-9 or better on the Owen branch (P2 >= 1e-7 there, or h <= 0.25).
    Infinite thresholds give the margins (or 0, -inf).
    """
    a, b, r = np.broadcast_arrays(*(np.asarray(v, float) for v in (a, b, r)))
    shape = a.shape
    a, b, r = a.ravel(), b.ravel(), r.ravel()
    h, k = np.maximum(a, b), np.minimum(a, b)
    out = np.empty(a.size)
    owen = (h < 3.0) | (np.abs(r) >= 1.0) | ~np.isfinite(h) | (k == -np.inf)
    if owen.any():
        with np.errstate(divide="ignore"):
            out[owen] = np.log(np.maximum(P2(a[owen], b[owen], r[owen]), 0.0))
        # Owen's absolute error swamps a tiny P2 at negative r: use the integral there.
        tiny = owen & (r < 0) & (r > -1.0) & (h > 0.25) & np.isfinite(h) & (k > -np.inf) & (out < np.log(1e-7))
        if tiny.any():
            out[tiny] = _log_P2_integral(h[tiny], k[tiny], r[tiny])
    tail = ~owen
    if tail.any():
        out[tail] = _log_P2_integral(h[tail], k[tail], r[tail])
    return out.reshape(shape)


def P2_tail(a, b, r):
    """P(X > a, Y > b) = exp(log_P2(a, b, r)); use it instead of P2 when max(a, b) > 6."""
    return np.exp(log_P2(a, b, r))


def _log_binom_coef(n: float, m: int) -> np.ndarray:
    """log C(n, i) for i = 0..m-1, as sum_{l<i} log(n - l) - log i! (stable for n up to 1e300)."""
    i = np.arange(m, dtype=float)
    terms = np.log(n) + np.log1p(-i / n)
    return np.concatenate([[0.0], np.cumsum(terms[:-1])]) - special.gammaln(i + 1.0)


def _log_binom_pmf(logC, n, logp, log1mp):
    """log Bin(i; n, p) for i = 0..len(logC)-1; rows are nodes (logp, log1mp are 1-D)."""
    i = np.arange(logC.size, dtype=float)
    with np.errstate(invalid="ignore"):
        a = np.where(i == 0, 0.0, i * logp[:, None])
        b = np.where(n - i == 0, 0.0, (n - i) * log1mp[:, None])
    return logC + a + b


def _binom_cdf(k: int, n: float, logp, log1mp, logC=None):
    """P(Bin(n, p) <= k) per node: a log-space sum for k < _MSMALL, else betaincc."""
    if k < 0:
        return np.zeros(np.shape(logp))
    if k < _MSMALL:
        logC = _log_binom_coef(n, k + 1) if logC is None else logC[: k + 1]
        return np.minimum(np.exp(_log_binom_pmf(logC, n, logp, log1mp)).sum(axis=1), 1.0)
    p = np.clip(np.exp(logp), 0.0, 1.0)
    return special.betaincc(k + 1.0, n - k, p)


def _log1m_from(logp, log_rest):
    """log(1 - p): log1p(-p) when p < 1/2, else the separately computed log of the complement."""
    p = np.exp(logp)
    with np.errstate(divide="ignore", invalid="ignore"):
        return np.where(p < 0.5, np.log1p(-np.minimum(p, 1.0)), log_rest)


# ---------------------------------------------------------------------------
# Quadrature axis for one tail coordinate of a tagged paper
# ---------------------------------------------------------------------------

_TRANS = np.array([-9, -6, -4, -2.5, -1, 0, 1, 2.5, 4, 6, 9, 12.0])
_TAIL = np.array([0.75, 2, 4, 7, 11, 16, 22, 30, 40, 55.0])


@functools.lru_cache(maxsize=256)
def _axis_breaks(n: float, cap: float):
    """Panel breakpoints for u = Phibar(x) when the event is 'fewer than cap of n other papers exceed x'.

    Breakpoints sit at the counts cap + k sqrt(cap) and reach 55 e-folds below them.
    Returns (tb, xb): tb, ascending breakpoints in t = log u for u <= 1/2 (panels uniform in t);
    xb, descending breakpoints in x from 0 for u > 1/2 (panels uniform in x), or None.
    """
    C = float(cap)
    cnt = C + np.sqrt(C) * _TRANS
    cnt = np.append(cnt[cnt > 0], C + 12.0 * np.sqrt(C) + 40.0)
    lt = np.log(cnt)
    gaps = np.maximum(1, np.ceil(np.diff(lt) / 0.6)).astype(int)  # transition panels at most 0.6 wide
    lt = np.concatenate([np.linspace(a, b, g, endpoint=False) for a, b, g in zip(lt[:-1], lt[1:], gaps)] + [lt[-1:]])
    lu = np.concatenate([lt[0] - _TAIL[::-1], lt]) - np.log(n)
    half = np.log(0.5)
    tb = lu[lu < half]
    xb = None
    if lu[-1] > half:
        tb = np.append(tb, half)
        x_end = -9.5 if lu[-1] >= 0.0 else float(-special.ndtri_exp(lu[-1]))
        mids = lu[(lu > half) & (lu < min(lu[-1], 0.0))]
        xb = np.unique(np.concatenate([[0.0, x_end], -special.ndtri_exp(mids), np.arange(-1.0, x_end, -1.0)]))[::-1]
    return tb, xb


@functools.lru_cache(maxsize=256)
def _axis(n: float, cap: float, nodes: int = 8):
    """Nodes for u = Phibar(x) on the panels of _axis_breaks. Returns (x, log u, log of the du-weight)."""
    tb, xb = _axis_breaks(n, cap)
    t, w = _panels(tb, nodes)
    xs, lus, lws = [-special.ndtri_exp(t)], [t], [np.log(w) + t]
    if xb is not None:
        x, w = _panels(xb, nodes)
        xs.append(x)
        lus.append(special.log_ndtr(-x))
        lws.append(np.log(w) + _log_phi(x))
    return tuple(np.concatenate(v) for v in (xs, lus, lws))


def _log_copula(x, y, r):
    """log of the Gaussian copula density: -log tau + kappa (x^2 + y^2)/2 - r (x - y)^2 / (2 tau^2)."""
    tau2 = 1.0 - r * r
    return -0.5 * np.log(tau2) + 0.5 * r / (1.0 + r) * (x * x + y * y) - 0.5 * r * (x - y) ** 2 / tau2


# Above this |rho| the copula ridge (width tau along x = rho y) is narrower than the panels of
# the product grid; the ridge grid integrates x = rho y + tau w over w instead.
_RIDGE_RHO = 0.95
_W_RIDGE = np.arange(-12.0, 12.5, 1.0)  # unit panels in w on [-12, 12]; phi(12) = 2e-32


def _grid_blocks(n: float, cap_q: float, cap_s: float, r: float, per_node: int, nodes: int = 8):
    """Yield flattened (x, y, log u, log v, log weight) blocks for N phi2(x, y; r) dx dy / N.

    The weight includes the density. For |r| <= _RIDGE_RHO: the product of the quality axis
    (cap_q) and the score axis (cap_s), with the copula density. Otherwise: for each score node y,
    w = (x - r y)/tau on unit panels over [-12, 12] plus the quality-axis breakpoints mapped
    into w, so that both the ridge and the quality-count switch are resolved; the weight is then
    dv phi(w) dw.
    """
    xs, lus, lws = _axis(n, cap_s, nodes)
    if abs(r) <= _RIDGE_RHO:
        xq, luq, lwq = _axis(n, cap_q, nodes)
        rows = max(1, int(2_000_000 // (xs.size * (per_node + 1))))
        for r0 in range(0, xq.size, rows):
            sl = slice(r0, r0 + rows)
            shape = (xq[sl].size, xs.size)
            x = np.broadcast_to(xq[sl, None], shape).ravel()
            y = np.broadcast_to(xs[None, :], shape).ravel()
            lw = (lwq[sl, None] + lws[None, :]).ravel() + _log_copula(x, y, r)
            yield x, y, np.broadcast_to(luq[sl, None], shape).ravel(), np.broadcast_to(lus[None, :], shape).ravel(), lw
        return
    tau = np.sqrt(1.0 - r * r)
    tb, xb = _axis_breaks(n, cap_q)
    xqb = -special.ndtri_exp(tb)
    if xb is not None:
        xqb = np.concatenate([xqb, xb[1:]])
    x_hi, x_lo = float(xqb[0]), float(xqb[-1])
    x0, w0 = _gl(nodes)
    nb = _W_RIDGE.size + xqb.size
    rows = max(1, int(2_000_000 // ((nb - 1) * nodes * (per_node + 1))))
    for r0 in range(0, xs.size, rows):
        y, lv, lwy = xs[r0 : r0 + rows], lus[r0 : r0 + rows], lws[r0 : r0 + rows]
        mu = r * y[:, None]
        lo = np.maximum(_W_RIDGE[0], (x_lo - mu) / tau)  # below x_lo too many papers have higher quality
        hi = np.minimum(_W_RIDGE[-1], (x_hi - mu) / tau)
        wb = np.concatenate([np.broadcast_to(_W_RIDGE, (y.size, _W_RIDGE.size)), (xqb[None, :] - mu) / tau], axis=1)
        wb = np.sort(np.minimum(np.maximum(wb, lo), hi), axis=1)  # lo > hi collapses every panel
        half = 0.5 * np.diff(wb, axis=1)[:, :, None]
        w = (0.5 * (wb[:, 1:] + wb[:, :-1])[:, :, None] + half * x0).reshape(y.size, -1)
        with np.errstate(divide="ignore"):
            lw = lwy[:, None] + _log_phi(w) + np.log((half * w0).reshape(y.size, -1))
        x = mu + tau * w
        shape = x.shape
        yield (x.ravel(), np.broadcast_to(y[:, None], shape).ravel(), special.log_ndtr(-x).ravel(),
               np.broadcast_to(lv[:, None], shape).ravel(), lw.ravel())


# ---------------------------------------------------------------------------
# §6.4 Exact E|Top_K(S) ∩ Top_M(Q)| at finite N
# ---------------------------------------------------------------------------


def _count_arg(v, name: str, low: int) -> int:
    """v as an int >= low (a float with an integral value is accepted); ValueError otherwise."""
    if not (np.isfinite(v) and float(v) == int(v) and int(v) >= low):
        raise ValueError(f"{name} must be an integer >= {low}, got {v!r}")
    return int(v)


def _check_rho(r: float) -> float:
    r = float(r)
    if not -1.0 <= r <= 1.0:
        raise ValueError(f"rho must lie in [-1, 1], got {r!r}")
    return r


def _count_topK_topM(N: float, K: int, M: int, r: float, nodes: int = 8) -> float:
    """E|Top_K(S) ∩ Top_M(Q)| for N iid standard normal pairs with correlation r.

    N int int phi2(x, y; r) sum_{a<K} Bin(a; n, Phibar(y)) sum_{j<=min(a, M-1)} Bin(j; a, pi1)
    F_Bin(M-1-j; n-a, pi0) dx dy, with n = N - 1, pi1 = P(Q>x | S>y), pi0 = P(Q>x | S<y).
    K, M >= 0. |r| = 1 gives the closed values min(K, M) (r = 1) and max(0, K + M - N) (r = -1).
    """
    K, M = _count_arg(K, "K", 0), _count_arg(M, "M", 0)
    r = _check_rho(r)
    if K == 0 or M == 0:
        return 0.0
    if K >= N:
        return float(min(M, N))
    if M >= N:
        return float(K)
    if r == 1.0:
        return float(min(K, M))
    if r == -1.0:
        return float(max(0.0, K + M - N))
    n = N - 1.0
    W = min(K, M)
    small = M <= _MSMALL
    logC = _log_binom_coef(n, max(K, M) if small else K)
    mwin = M - 1.0 - np.arange(W, dtype=float)  # window of quality counts m_j = M-1-j
    total = 0.0
    for x, y, lu, lv, lw in _grid_blocks(n, float(M), float(K), r, K + W + (M if small else 0), nodes):
        l11 = log_P2(x, y, r)
        p11 = np.exp(l11)
        lPhi_y = special.log_ndtr(y)
        Phi_y = np.exp(lPhi_y)
        p10 = np.maximum(np.exp(lu) - p11, 0.0)  # P(Q > x, S < y)
        neg = y < 0
        if neg.any():
            p10[neg] = np.exp(log_P2(x[neg], -y[neg], -r))
        p01 = np.maximum(np.exp(lv) - p11, 0.0)  # P(Q < x, S > y)
        neg = x < 0
        if neg.any():
            p01[neg] = np.exp(log_P2(-x[neg], y[neg], -r))
        with np.errstate(divide="ignore", invalid="ignore"):
            lpi1 = np.minimum(l11 - lv, 0.0)
            l1mpi1 = _log1m_from(lpi1, np.log(p01) - lv)
            lpi0 = np.minimum(np.log(p10) - lPhi_y, 0.0)
            l1mpi0 = np.maximum(_log1m_from(lpi0, np.log(np.maximum(Phi_y - p10, 0.0)) - lPhi_y), -700.0)
        pa = np.exp(_log_binom_pmf(logC[:K], n, lv, lPhi_y))  # score count a of the other papers
        if small:
            lf_all = _log_binom_pmf(logC[:M], n, lpi0, l1mpi0)
            cols = (M - 1 - np.arange(W)).astype(int)
            Fw = np.minimum(np.cumsum(np.exp(lf_all), axis=1)[:, cols], 1.0)
            fw = np.exp(lf_all[:, cols])
        else:
            m = mwin[None, :]
            Fw = special.betaincc(m + 1.0, n - m, np.exp(lpi0)[:, None])
            fw = np.exp(-np.log1p(n) - special.betaln(n - m + 1.0, m + 1.0) + m * lpi0[:, None] + (n - m) * l1mpi0[:, None])
        pi0 = np.exp(lpi0)[:, None]
        inv1mpi0 = np.exp(-l1mpi0)[:, None]
        pi1, q1 = np.exp(lpi1)[:, None], np.exp(l1mpi1)[:, None]
        Bj = np.zeros((x.size, W))  # Bin(j; a, pi1) for j < W, built up over a
        Bj[:, 0] = 1.0
        G = np.zeros(x.size)
        for a in range(K):
            G += pa[:, a] * np.einsum("ij,ij->i", Bj, Fw)
            if a < K - 1:
                nn = n - a  # move the quality window from nn to nn - 1 trials
                fw = fw * (np.maximum(nn - mwin, 0.0) / nn)[None, :] * inv1mpi0
                Fw = np.minimum(Fw + pi0 * fw, 1.0)
                Bj[:, 1:] = Bj[:, 1:] * q1 + Bj[:, :-1] * pi1
                Bj[:, 0] *= q1[:, 0]
        total += float(np.sum(np.exp(np.log(N) + lw) * G))
    return total


def precision_fixed_K(N, K, rho):
    """Exact E|Top_K(S) ∩ Top_K(Q)| / K at finite N (2-D integral of §6.4 with M = K).

    K is an integer >= 1 (an empty selection has no precision: ValueError). Relative error
    about 1e-9 for rho in [-0.95, 1]; for |rho| > 0.95 the ridge grid of _grid_blocks is used, whose
    absolute error is below about 1e-30, so for rho < -0.95 a value far below that returns as 0.
    rho = 1 gives 1 and rho = -1 gives max(0, 2K - N)/K.
    """
    K = _count_arg(K, "K", 1)
    return _over_N(N, lambda n: _count_topK_topM(n, K, K, float(rho)) / K)


def containment_fixed_K(N, K, M, rho):
    """Exact expected share of Top_K(S) inside the true top M: E|Top_K(S) ∩ Top_M(Q)| / K (K >= 1, M >= 0)."""
    K = _count_arg(K, "K", 1)
    return _over_N(N, lambda n: _count_topK_topM(n, K, M, float(rho)) / K)


def overlap_fixed_K(N, K, rho):
    """Two-committee top-K overlap E|Top_K(S1) ∩ Top_K(S2)| / K = precision_fixed_K(N, K, rho^2)."""
    return precision_fixed_K(N, K, float(rho) ** 2)


def rejected_given_top(N, K, alpha, rho):
    """P(committee 2 rejects at rate alpha | in Top_K(S1)) = 1 - E|Top_K(S1) ∩ Top_A(S2)|/K, A = round(alpha N).

    A = 0 (committee 2 accepts nothing) gives 1.
    """
    K = _count_arg(K, "K", 1)
    return _over_N(N, lambda n: 1.0 - _count_topK_topM(n, K, int(round(alpha * n)), float(rho) ** 2) / K)


# ---------------------------------------------------------------------------
# §6.4 Large-N laws and the local slope
# ---------------------------------------------------------------------------


def b_N(N):
    """b_N = Phibar^{-1}(1/N), the level that one of N standard normals exceeds on average."""
    return -special.ndtri_exp(-np.log(np.asarray(N, float)))


def _log_I(n, c):
    """log I_n(c) = log Gamma(n + c) - log Gamma(n) - log c."""
    return special.gammaln(n + c) - special.gammaln(n) - np.log(c)


def beta_K(K, rho):
    """Coefficient of the 1/b_N^2 correction: 2 kappa psi(K+c) - rho(3-rho)/(1-rho) - rho psi'(K+c)/(1-rho^2)."""
    tau, c, kap, _ = _consts(rho)
    K = np.asarray(K, float)
    return 2 * kap * special.digamma(K + c) - rho * (3 - rho) / (1 - rho) - rho * special.polygamma(1, K + c) / tau**2


def omega_K(K, rho):
    """Coefficient of the joint-exceedance correction omega_K eps_N: [Gamma(K + beta) / Gamma(K + c)]^2."""
    _, c, _, beta = _consts(rho)
    K = np.asarray(K, float)
    return np.exp(2 * (special.gammaln(K + beta) - special.gammaln(K + c)))


def log_eps_N(N, rho):
    """log eps_N = kappa b_N^2 - log N - log tau: eps_N is the mean number of papers in both rescaled tops."""
    tau, _, kap, _ = _consts(rho)
    return kap * b_N(N) ** 2 - np.log(np.asarray(N, float)) - np.log(tau)


def precision_fixed_K_asymptotic(N, K, rho, order=0, form="bN"):
    """Leading law eps_N I_K^2 / K (order 0); order 1 multiplies by 1 + beta_K/b_N^2 + omega_K eps_N.

    form="logN" gives the same law in elementary functions,
    C_K N^(-beta) (4 pi log N)^(-kappa) with C_K = (1+rho)^2 Gamma(K+c)^2 / (tau K Gamma(K)^2)
    (the C_K of docs/derivations.md §4.3; notes B's constant (4 pi)^(-kappa) C_K multiplies (log N)^(-kappa) N^(-beta)),
    and order 1 then multiplies by 1 + kappa log(4 pi L)/(2L) + (beta_K - 2 kappa)/(2L) + omega_K eps_N, L = log N.
    """
    tau, c, kap, beta = _consts(rho)
    N = np.asarray(N, float)
    lI = _log_I(K, c)
    le = log_eps_N(N, rho)
    corr_om = omega_K(K, rho) * np.exp(le)
    if form == "bN":
        out = np.exp(le + 2 * lI - np.log(K))
        if order >= 1:
            out = out * (1 + beta_K(K, rho) / b_N(N) ** 2 + corr_om)
    elif form == "logN":
        L = np.log(N)
        out = np.exp(2 * lI - np.log(K) - np.log(tau) - kap * np.log(4 * np.pi * L) - beta * L)
        if order >= 1:
            out = out * (1 + kap * np.log(4 * np.pi * L) / (2 * L) + (beta_K(K, rho) - 2 * kap) / (2 * L) + corr_om)
    else:
        raise ValueError("form must be 'bN' or 'logN'")
    return float(out) if out.ndim == 0 else out


def beta_KM(K, M, rho):
    """1/b_N^2 coefficient for Top_K(S) in Top_M(Q): kappa (D_K + D_M) - rho/(2 tau^2) [(D_K - D_M)^2 + P_K + P_M + 2 (1+rho)^2].

    D_n = psi(n + c) - (1 + rho), P_n = psi'(n + c); beta_KM(K, K, rho) = beta_K(K, rho).
    """
    tau, c, kap, _ = _consts(rho)
    K, M = np.asarray(K, float), np.asarray(M, float)
    DK, DM = special.digamma(K + c) - (1 + rho), special.digamma(M + c) - (1 + rho)
    PK, PM = special.polygamma(1, K + c), special.polygamma(1, M + c)
    return kap * (DK + DM) - rho / (2 * tau**2) * ((DK - DM) ** 2 + PK + PM + 2 * (1 + rho) ** 2)


def omega_KM(K, M, rho):
    """Joint-exceedance coefficient (1+rho)^2 Gamma(K+beta) Gamma(M+beta) / (Gamma(K) Gamma(M) I_K I_M)."""
    _, c, _, beta = _consts(rho)
    K, M = np.asarray(K, float), np.asarray(M, float)
    lg = special.gammaln(K + beta) + special.gammaln(M + beta) - special.gammaln(K) - special.gammaln(M)
    return (1 + rho) ** 2 * np.exp(lg - _log_I(K, c) - _log_I(M, c))


def containment_fixed_K_asymptotic(N, K, M, rho, order=0):
    """Leading law eps_N I_K I_M / K for the share of Top_K(S) in the true top M; order 1 adds beta_KM/b_N^2 + omega_KM eps_N."""
    _, c, _, _ = _consts(rho)
    le = log_eps_N(N, rho)
    out = np.exp(le + _log_I(K, c) + _log_I(M, c) - np.log(K))
    if order >= 1:
        out = out * (1 + beta_KM(K, M, rho) / b_N(N) ** 2 + omega_KM(K, M, rho) * np.exp(le))
    return float(out) if np.ndim(out) == 0 else out


def finite_K_factor(K, rho):
    """R_K = [Gamma(K + c) / (Gamma(K) K^c)]^2: limit of prec_K(N) / precision_pct(K/N) as N -> inf."""
    _, c, _, _ = _consts(rho)
    K = np.asarray(K, float)
    return np.exp(2 * (special.gammaln(K + c) - special.gammaln(K) - c * np.log(K)))


def precision_fixed_K_hybrid(N, K, rho):
    """Practical closed form R_K P2(z, z; rho) / (K/N) with z = Phibar^{-1}(K/N) (tail-accurate P2)."""
    N = np.asarray(N, float)
    lp = np.log(K) - np.log(N)
    z = -special.ndtri_exp(lp)
    out = finite_K_factor(K, rho) * np.exp(log_P2(z, z, rho) - lp)
    return float(out) if out.ndim == 0 else out


def local_loglog_slope(N, K, rho, method="exact", h=0.02):
    """d log prec_K / d log N: centred difference of the exact precision, or -beta - 2 kappa (1 - b_N/a_N) ("leading").

    The exact slope uses steps of h in log N. The leading form is the derivative of
    eps_N I_K^2 / K, with a_N = N phi(b_N).
    """
    if method == "leading":
        _, _, kap, beta = _consts(rho)
        N = np.asarray(N, float)
        b = b_N(N)
        a = np.exp(np.log(N) + _log_phi(b))
        out = -beta - 2 * kap * (1 - b / a)
        return float(out) if out.ndim == 0 else out
    if method != "exact":
        raise ValueError("method must be 'exact' or 'leading'")

    def one(n):
        hi = _count_topK_topM(n * np.exp(h), K, K, float(rho))
        lo = _count_topK_topM(n * np.exp(-h), K, K, float(rho))
        return (np.log(hi) - np.log(lo)) / (2 * h)

    return _over_N(N, one)


# ---------------------------------------------------------------------------
# §6.2 Fixed-percentile precision at finite N (closed-form O(1/N) correction)
# ---------------------------------------------------------------------------


def precision_pct_finite(N, p, rho):
    """Finite-N fixed-percentile precision H(p_K)/p_K - (1 - p_K) g (rho - phi_I) / N (closed form).

    p_K = round(pN)/N, z = Phibar^{-1}(p_K), H = P2(z, z; rho), g = phi(sqrt(beta) z) / (tau phi(z)),
    phi_I = (H - p_K^2) / (p_K (1 - p_K)).
    Error: O(N^-2) at fixed p, but with a constant of order 1/p^2, so the relative error is
    O(1/K^2) with K = round(pN). It is negative and grows as K falls: -0.98 % at K = 3,
    -0.36 % at K = 5, -0.09 % at K = 10 and -0.011 % at K = 30 (N = 1000, rho^2 = 0.85; a little
    smaller at lower rho; docs/derivations.md §2.3). For K < 10 use precision_fixed_K(N, K, rho).
    K = N gives 1; K = 0 (an empty selection) gives NaN; rho = 1 gives 1.
    """
    rho = float(rho)
    N = np.asarray(N, float)
    Kn = np.round(p * N)
    pk = Kn / N
    if rho >= 1.0:
        out = np.where(Kn > 0, 1.0, np.nan)
        return float(out) if out.ndim == 0 else out
    tau, _, _, beta = _consts(rho)
    with np.errstate(divide="ignore", invalid="ignore", over="ignore"):
        z = z_upper(pk)
        H = P2_tail(z, z, rho)
        g = np.exp(_log_phi(np.sqrt(beta) * z) - _log_phi(z)) / tau
        phi_I = (H - pk**2) / (pk * (1 - pk))
        out = H / pk - (1 - pk) * g * (rho - phi_I) / N
    out = np.where(Kn >= N, 1.0, np.where(Kn <= 0, np.nan, out))
    return float(out) if out.ndim == 0 else out


# ---------------------------------------------------------------------------
# §6.5 Mechanism helpers (standardised units)
# ---------------------------------------------------------------------------


def _top_score_mean(N: float, K: int, g) -> float:
    """(1/K) E sum_{i in Top_K(S)} g(S_i) = (N/K) int_0^1 F_Bin(K-1; N-1, v) g(Phibar^{-1}(v)) dv."""
    n = N - 1.0
    y, lv, lw = _axis(n, float(K))
    F = _binom_cdf(int(K) - 1, n, lv, special.log_ndtr(y))
    return float(np.sum(np.exp(np.log(N) + lw) * F * g(y)) / K)


def expected_kth_best(N, K):
    """E[S*_(K)], the K-th largest of N standard normals: N int Bin(K-1; N-1, v) Phibar^{-1}(v) dv (1 <= K <= N)."""
    K = _count_arg(K, "K", 1)
    if np.any(np.asarray(N, float) < K):
        raise ValueError(f"K = {K} exceeds N")

    def one(n):
        y, lv, lw = _axis(n - 1.0, float(K))
        k = int(K) - 1
        if k < _MSMALL:
            lc = _log_binom_coef(n - 1.0, k + 1)[k]
        else:
            lc = -np.log(n) - special.betaln(n - k, k + 1.0)
        lpmf = lc + k * lv + (n - 1.0 - k) * special.log_ndtr(y)
        return float(np.sum(np.exp(np.log(n) + lw + lpmf) * y))

    return _over_N(N, one)


def conditional_quality_mean(s, rho):
    """E[Q* | S* = s] = rho s."""
    return float(rho) * np.asarray(s, float)


def conditional_quality_sd(rho):
    """SD(Q* | S* = s) = tau = sqrt(1 - rho^2), the same for every s."""
    return float(np.sqrt(1.0 - float(rho) ** 2))


def true_topK_threshold(N, K, kind="expected"):
    """Quality needed to be in the true top K: E[Q*_(K)] (kind="expected") or Phibar^{-1}(K/N) ("quantile")."""
    if kind == "expected":
        return expected_kth_best(N, K)
    if kind == "quantile":
        return z_upper(np.asarray(K, float) / np.asarray(N, float))
    raise ValueError("kind must be 'expected' or 'quantile'")


def mechanism_gap(N, K, rho, i=1):
    """(E[Q*_(K)] - rho E[S*_(i)]) / tau: shortfall of the i-th top-scored paper below the true top-K bar, in SDs."""
    tau = conditional_quality_sd(rho)
    return (expected_kth_best(N, K) - float(rho) * np.asarray(expected_kth_best(N, i))) / tau


# ---------------------------------------------------------------------------
# §6.6 Containment in a fixed top percentile; mean true percentile
# ---------------------------------------------------------------------------


def containment_limit(K, p, rho, N=None):
    """Share of Top_K(S) in the true top fraction p: limit 1 for rho > 0; with N, (N/K) int F_Bin Phi((rho y - z_p)/tau) dv.

    Without N: the N -> infinity limit (p at rho = 0, 0 for rho < 0). With N: the population-threshold
    value (N/K) int F_Bin(K-1; N-1, v) Phi((rho Phibar^{-1}(v) - z_p)/tau) dv, within O(1/N) of the exact
    share. Use containment_miss for 1 - share when it is tiny.
    """
    rho = float(rho)
    if N is None:
        return 1.0 if rho > 0 else (float(p) if rho == 0 else 0.0)
    tau, zp = np.sqrt(1 - rho * rho), float(z_upper(p))
    return _over_N(N, lambda n: _top_score_mean(n, K, lambda y: special.ndtr((rho * y - zp) / tau)))


def containment_miss(N, K, p, rho):
    """1 - containment_limit(K, p, rho, N) = (N/K) int F_Bin(K-1; N-1, v) Phi((z_p - rho y)/tau) dv, with no cancellation."""
    rho = float(rho)
    tau, zp = np.sqrt(1 - rho * rho), float(z_upper(p))
    return _over_N(N, lambda n: _top_score_mean(n, K, lambda y: special.ndtr((zp - rho * y) / tau)))


def containment_miss_asymptotic(N, K, p, rho):
    """1 - share ~ Phibar(w_N) Gamma(K+1+g) / ((1+g) Gamma(K+1)), w_N = (rho b_N - z_p)/tau, g = rho w_N/(a_N tau)."""
    tau, _, _, _ = _consts(rho)
    N = np.asarray(N, float)
    b = b_N(N)
    a = np.exp(np.log(N) + _log_phi(b))
    w = (rho * b - z_upper(p)) / tau
    g = rho * w / (a * tau)
    out = special.ndtr(-w) * np.exp(special.gammaln(K + 1 + g) - special.gammaln(K + 1)) / (1 + g)
    return float(out) if out.ndim == 0 else out


def mean_true_percentile(N, K, rho):
    """Mean population percentile Phi(Q*) of Top_K(S): (N/K) int F_Bin(K-1; N-1, v) Phi(rho y / sqrt(2 - rho^2)) dv."""
    s = np.sqrt(2.0 - float(rho) ** 2)
    return _over_N(N, lambda n: _top_score_mean(n, K, lambda y: special.ndtr(float(rho) * y / s)))


# ---------------------------------------------------------------------------
# §6.7 Best-paper probability; §6.8 rank of the winner
# ---------------------------------------------------------------------------


def _best_in_topK(N: float, K: float, r: float, poisson: bool = False, nodes: int = 8) -> float:
    """P(best in Top_K(S)) = N int int phi2(m, y) Phi(m)^(N-1) P(Bin(N-1, pi) <= K-1), pi = (Phibar(y) - P2(m, y))/Phi(m)."""
    K = _count_arg(K, "K", 0)
    r = _check_rho(r)
    if K == 0:
        return 0.0
    if K >= N:
        return 1.0
    if r == 1.0:
        return 1.0
    if r == -1.0:
        return 0.0  # the best paper has the lowest score, and K < N
    n = N - 1.0
    logC = _log_binom_coef(n, K) if K < _MSMALL else None
    total = 0.0
    for m, y, lu, lv, lw in _grid_blocks(n, 1.0, float(K), r, min(K, _MSMALL), nodes):
        lPhi_m = special.log_ndtr(m)
        p11 = P2_tail(m, y, r)
        p01 = np.maximum(np.exp(lv) - p11, 0.0)
        neg = m < 0
        if neg.any():
            p01[neg] = P2_tail(-m[neg], y[neg], -r)
        with np.errstate(divide="ignore", invalid="ignore"):
            lpi = np.minimum(np.log(p01) - lPhi_m, 0.0)
            l1mpi = _log1m_from(lpi, np.log(np.maximum(np.exp(lPhi_m) - p01, 0.0)) - lPhi_m)
        if poisson:
            F = special.pdtr(K - 1, n * np.exp(lpi))
        else:
            F = _binom_cdf(K - 1, n, lpi, l1mpi, logC)
        total += float(np.sum(np.exp(np.log(N) + lw + n * lPhi_m) * F))
    return total


def best_paper_prob(N, K, rho, method="exact"):
    """P(the truly best paper is in Top_K(S)): exact binomial integral, or the handoff's Poisson((N-1) pi) route.

    K = 0 gives 0 and K >= N gives 1; rho = 1 gives 1 and rho = -1 gives 0 (K < N). For |rho| > 0.95
    the integral uses the ridge grid of _grid_blocks.
    """
    if method not in ("exact", "poisson"):
        raise ValueError("method must be 'exact' or 'poisson'")
    return _over_N(N, lambda n: _best_in_topK(n, K, float(rho), poisson=(method == "poisson")))


def best_paper_prob_asymptotic(N, K, rho, order=0):
    """Leading law eps_N Gamma(c) I_K(c) = (1+rho) Gamma(c) Gamma(K+c) e^{kappa b_N^2} / (tau Gamma(K) N).

    P_best(N, K) = E|Top_K(S) ∩ Top_1(Q)| exactly, so this is K containment_fixed_K_asymptotic(N, K, 1, rho)
    (I_1 = Gamma(c)). order=1 multiplies by 1 + beta_KM(K, 1)/b_N^2 + omega_KM(K, 1) eps_N. The (D_K - D_1)^2
    ~ log^2 K term of beta_KM(K, 1) does not cancel, so the correction is large for large K: like the
    precision series it is worse than the leading law at N <= 1e6 for rho >= 0.75, and it can be negative
    there (-0.088 at N = 1e6, K = 5, rho = 0.9). Use it only far beyond the range; use best_paper_prob in it.
    """
    _, c, _, _ = _consts(rho)
    le = log_eps_N(N, rho)
    out = np.exp(le + special.gammaln(c) + _log_I(K, c))
    if order >= 1:
        out = out * (1 + beta_KM(K, 1, rho) / b_N(N) ** 2 + omega_KM(K, 1, rho) * np.exp(le))
    return float(out) if np.ndim(out) == 0 else out


def winner_rank_cdf(N, rho, ranks):
    """P(true rank of the top-scored paper <= r) = P(best paper in Top_r(S)), by exchangeability of (Q*, S*)."""
    ranks = np.asarray(ranks)
    out = np.array([_best_in_topK(float(N), int(r), float(rho)) for r in ranks.ravel()]).reshape(ranks.shape)
    return float(out) if out.ndim == 0 else out


def winner_rank_quantile(N, rho, q=0.5):
    """Smallest r with P(true rank of the top-scored paper <= r) >= q (exact cdf, integer search)."""

    def one(n):
        cdf = lambda r: _best_in_topK(n, int(r), float(rho))
        tau = np.sqrt(1 - float(rho) ** 2)
        guess = n * special.ndtr(-(float(rho) * b_N(n) + tau * special.ndtri(1 - q)))
        hi = int(min(max(1, round(guess)), n))
        while hi < n and cdf(hi) < q:
            hi = int(min(2 * hi, n))
        lo = hi // 2
        while lo >= 1 and cdf(lo) >= q:
            hi, lo = lo, lo // 2
        while hi - lo > 1:  # cdf(lo) < q <= cdf(hi), lo = 0 meaning cdf(0) = 0
            mid = (lo + hi) // 2
            if cdf(mid) >= q:
                hi = mid
            else:
                lo = mid
        return float(hi)

    return _over_N(N, one)


def winner_rank_median_asymptotic(N, rho, form="semi"):
    """Median winner rank N Phibar(rho b_N + rho gamma_E / a_N) ("semi") or (e^{-gamma_E rho^2}/rho) (N/(sqrt(2 pi) b_N))^(1-rho^2) ("power").

    The semi form holds for every rho (N/2 at rho = 0). The power form uses Phibar(t) ~ phi(t)/t at
    t = rho b_N, so it needs rho > 0: ValueError otherwise.
    """
    rho = float(rho)
    if form == "power" and rho <= 0:
        raise ValueError("the power form needs rho > 0; use form='semi'")
    N = np.asarray(N, float)
    b = b_N(N)
    if form == "semi":
        a = np.exp(np.log(N) + _log_phi(b))
        out = N * special.ndtr(-(rho * b + rho * np.euler_gamma / a))
    elif form == "power":
        out = np.exp(-np.euler_gamma * rho**2) / rho * (N / (np.sqrt(2 * np.pi) * b)) ** (1 - rho**2)
    else:
        raise ValueError("form must be 'semi' or 'power'")
    return float(out) if out.ndim == 0 else out
