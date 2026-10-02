"""Check every closed form in analytic.py against the simulator (handoff §6.13).

Model: Gaussian continuous scores, R = 1, sigma_q = 1.2, sigma_u = 0, and sigma_eps set
so that rho^2 is 0.3, 0.45, 0.56, 0.7 or 0.85. Conference sizes N = 1e3, 1e4, 1e5, 1e6.

Simulations (one distinct seed per configuration, recorded in the CSV):
  main  simulate(..., two_committees=True) with the default replicate budget
        (10,000 / 10,000 / 2,000 / 200 conferences at N = 1e3 / 1e4 / 1e5 / 1e6).
  best  simulate_best_paper with max(4000, min(100000, 2e9 / N)) conferences.
The winner ranks of both runs are kept in full (the accumulator class is swapped for a
subclass that also returns the raw values; the simulation itself is unchanged).

Each CSV row compares one simulated metric with one analytic value. The column `role`
says what kind of analytic value it is:
  exact   finite-N integral (precision_fixed_K, containment_fixed_K, overlap_fixed_K,
          rejected_given_top, mean_true_percentile, best_paper_prob, winner_rank_*).
          These must agree with the simulator within Monte Carlo error.
  closed  closed-form finite-N fixed-percentile value precision_pct_finite, for every
          fixed-percentile and acceptance size (the exact integral is added only up to
          K = EXACT_KMAX, where it is fast). Its own error is O(1/K^2) relative: about
          -0.005 (-1%) at K = 3 and rho^2 = 0.85, and negligible from K = 30.
  limit   N-free large-N value (precision_pct, swap_fraction, disagreement,
          inconsistent_share, P2 ratios, sqrt(rho2), committee_corr). It differs from the
          finite-N simulation by O(1/K) relative; that bias is expected.
  approx  asymptotic or approximate laws (hybrid, large-N series, population-threshold
          containment, Poisson best paper). Reported for information.

Columns: quantity, metric (simulator column), selection, K, M, kind (fixed-K or N-free),
role, analytic_fn, rho2, N, src, reps, seed, analytic, sim, se, se_sim, se_model,
abs_err = |sim - analytic|, rel_err = (sim - analytic)/|analytic| (signed),
z = (sim - analytic)/se (signed), vs_exact_rel = (approx - exact)/exact for approx rows (no
Monte Carlo noise), note, error (an exception raised by the analytic call, if any).

The SE used for z is the simulator's sample SE, except for rare-outcome cells (fewer than 25
expected minority outcomes over all conferences), where the SE column holds the binomial SE
at the analytic value, sqrt(a(1-a)/(K reps)), and z comes from the Poisson mid-p tail of the
observed minority count (the sample SE of such a cell is often 0, and a normal z from one
or two events overstates the deviation). For the winner rank,
`winner_cdf_q*` rows test the exact cdf F(m) at the exact q-quantile m against the share
of simulated ranks <= m; the `winner_median` row reports the SE of a sample median,
sqrt(1/(4 reps))/f(m), with f from a central difference of the exact cdf. Because ranks are
integers, its z is the exact-cdf test at m or at m - 1, whichever the simulated median lies
beyond (0 when the simulated median equals m).

Writes results/verify_analytic.csv and prints a summary.
Usage: uv run python scripts/verify_analytic.py [--workers 4] [--salt S] [--cache PATH]
       [--rho2 ...] [--N ...] [--kinds main best] [--out PATH]
A new --salt reruns the simulations with fresh seeds; --cache keeps raw results (analytic
values and simulations per salt) in a pickle so that a rerun only computes what is missing.
"""

from __future__ import annotations

import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse  # noqa: E402
import pickle  # noqa: E402
import sys  # noqa: E402
import traceback  # noqa: E402
from concurrent.futures import ProcessPoolExecutor, as_completed  # noqa: E402

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from scipy import stats  # noqa: E402

from peerreview import analytic as an  # noqa: E402
from peerreview import simulate as simmod  # noqa: E402
from peerreview.model import ReviewModel  # noqa: E402
from peerreview.simulate import DEFAULT_ALPHAS, Selections, simulate, simulate_best_paper  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "results", "verify_analytic.csv")

RHO2S = (0.3, 0.45, 0.56, 0.7, 0.85)
NS = (1_000, 10_000, 100_000, 1_000_000)
SIGMA_Q, R = 1.2, 1
FIXED_K = (1, 5, 10, 30, 100)
PCTS = (0.003, 0.005, 0.01, 0.05)
BEST_K = (1, 5, 10, 30)
ALPHA_REF = 0.25
EXACT_KMAX = 100  # exact finite-N integral for fixed-percentile sizes up to this K
MAX_WORKERS = 4
SEL = Selections(fixed_K=FIXED_K, pct=PCTS, alphas=DEFAULT_ALPHAS, best_K=BEST_K, alpha_ref=ALPHA_REF)
WINNER_Q = (0.25, 0.5, 0.75)


def model(rho2: float) -> ReviewModel:
    se = float(an.sigma_eps_for_rho2(rho2, R, SIGMA_Q))
    return ReviewModel(R=R, sigma_q=SIGMA_Q, sigma_u=0.0, sigma_eps=se)


def best_reps(N: int) -> int:
    return int(max(4000, min(100_000, 2e9 // N)))


# ---------------------------------------------------------------------------
# Simulation workers
# ---------------------------------------------------------------------------


class _RawAcc(simmod._Acc):
    """The simulator's accumulator, but summary() also returns the raw winner ranks."""

    def summary(self):
        out = super().summary()
        if "winner_rank" in self.vals:
            out["_winner_ranks"] = np.sort(np.concatenate(self.vals["winner_rank"])).astype(np.int64)
        return out


def _with_raw(fn, *a, **k):
    old = simmod._Acc
    simmod._Acc = _RawAcc
    try:
        return fn(*a, **k)
    finally:
        simmod._Acc = old


def run_sim(task):
    kind, rho2, N, salt = task
    m = model(rho2)
    tag = f"verify_analytic|{salt}|rho2={rho2}"
    if kind == "main":
        row = _with_raw(simulate, m, N, None, SEL, True, None, 4e6, tag)
    else:
        row = _with_raw(simulate_best_paper, m, N, best_reps(N), BEST_K, None, 4e6, tag)
    return task, row


# ---------------------------------------------------------------------------
# Analytic workers: every call is a hashable key (name, *args)
# ---------------------------------------------------------------------------


def _p2_share(N, K, M, r):
    """N-free share of Top_K(S) inside Top_M(Q): P2(z_{M/N}, z_{K/N}; r) / (K/N) (tail-accurate P2)."""
    pk, pm = K / N, M / N
    return float(an.P2_tail(an.z_upper(pm), an.z_upper(pk), r) / pk)


def _winner_stats(N, rho):
    """Exact winner-rank quantiles m_q, the cdf at m_q and m_q - 1, and the density at the median."""
    out = {}
    for q in WINNER_Q:
        mq = int(an.winner_rank_quantile(N, rho, q))
        out[q] = dict(m=mq, F=float(an.winner_rank_cdf(N, rho, mq)), Fm1=float(an.winner_rank_cdf(N, rho, mq - 1)) if mq > 1 else 0.0)
    m = out[0.5]["m"]
    d = max(1, int(round(0.1 * m)))
    lo = max(m - d, 0)
    Flo = float(an.winner_rank_cdf(N, rho, lo)) if lo >= 1 else 0.0
    Fhi = float(an.winner_rank_cdf(N, rho, m + d))
    out["density"] = (Fhi - Flo) / (m + d - lo)
    return out


CALLS = {
    "precision_fixed_K": an.precision_fixed_K,
    "precision_fixed_K_hybrid": an.precision_fixed_K_hybrid,
    "precision_fixed_K_asymptotic": an.precision_fixed_K_asymptotic,
    "containment_fixed_K": an.containment_fixed_K,
    "containment_fixed_K_asymptotic": an.containment_fixed_K_asymptotic,
    "containment_limit": lambda K, p, rho, N: an.containment_limit(K, p, rho, N=N),
    "containment_miss_asymptotic": an.containment_miss_asymptotic,
    "mean_true_percentile": an.mean_true_percentile,
    "overlap_fixed_K": an.overlap_fixed_K,
    "rejected_given_top": an.rejected_given_top,
    "best_paper_prob": an.best_paper_prob,
    "best_paper_prob_asymptotic": an.best_paper_prob_asymptotic,
    "winner_rank_median_asymptotic": an.winner_rank_median_asymptotic,
    "precision_pct": an.precision_pct,
    "precision_pct_finite": an.precision_pct_finite,
    "swap_fraction": an.swap_fraction,
    "disagreement": an.disagreement,
    "inconsistent_share": an.inconsistent_share,
    "p2_share": _p2_share,
    "winner_stats": _winner_stats,
    "rho2": an.rho2,
    "committee_corr": an.committee_corr,
}


def run_analytic(key):
    try:
        v = CALLS[key[0]](*key[1:])
        v = v if isinstance(v, dict) else float(v)
        return key, v, ""
    except Exception as e:  # report, do not stop the run
        return key, np.nan, f"{type(e).__name__}: {e} | {traceback.format_exc(limit=2)!r}"


def _analytic_cost(key) -> float:
    name, a = key[0], key[1:]
    if name in ("precision_fixed_K", "overlap_fixed_K"):
        return a[1] ** 2 + 50
    if name == "containment_fixed_K":
        return a[1] * min(a[1], a[2]) + 50
    if name == "rejected_given_top":
        return a[1] ** 2 + 80
    if name == "winner_stats":
        return 300
    return 1


# ---------------------------------------------------------------------------
# What to compare
# ---------------------------------------------------------------------------


def specs_for(rho2: float, N: int) -> list[dict]:
    rho, r12 = float(np.sqrt(rho2)), float(rho2)
    m = model(rho2)
    A_ref = int(round(ALPHA_REF * N))
    M1, M5 = max(1, int(round(0.01 * N))), max(1, int(round(0.05 * N)))
    out: list[dict] = []

    def add(quantity, metric, sel, K, M, kind, role, fn, key, src="main", post=None, size=None):
        out.append(dict(quantity=quantity, metric=metric, selection=sel, K=K, M=M, kind=kind, role=role, analytic_fn=fn,
                        key=key, src=src, post=post, size=K if size is None else size, rho2=rho2, N=N))

    one_minus = lambda v: 1.0 - v

    # --- fixed-number selections ------------------------------------------------
    for K in FIXED_K:
        s, fk = f"K{K}", "fixed-K"
        add("precision", f"prec_{s}", s, K, K, fk, "exact", "precision_fixed_K", ("precision_fixed_K", N, K, rho))
        add("precision", f"prec_{s}", s, K, K, fk, "approx", "precision_fixed_K_hybrid", ("precision_fixed_K_hybrid", N, K, rho))
        for order, form in ((0, "bN"), (1, "bN"), (0, "logN"), (1, "logN")):
            add("precision", f"prec_{s}", s, K, K, fk, "approx", f"precision_fixed_K_asymptotic(order={order},form={form})",
                ("precision_fixed_K_asymptotic", N, K, rho, order, form))
        for mult, nm in ((2, "c2x"), (10, "c10x")):
            M = mult * K
            if M > N:
                continue
            add("containment", f"{nm}_{s}", s, K, M, fk, "exact", "containment_fixed_K", ("containment_fixed_K", N, K, M, rho))
            for order in (0, 1):
                add("containment", f"{nm}_{s}", s, K, M, fk, "approx", f"containment_fixed_K_asymptotic(order={order})",
                    ("containment_fixed_K_asymptotic", N, K, M, rho, order))
        for nm, M, p in (("c1pct", M1, 0.01), ("c5pct", M5, 0.05), ("cA", A_ref, ALPHA_REF)):
            add("containment", f"{nm}_{s}", s, K, M, fk, "exact", "containment_fixed_K", ("containment_fixed_K", N, K, M, rho))
            add("containment", f"{nm}_{s}", s, K, M, fk, "approx", "containment_limit(N=N)", ("containment_limit", K, p, rho, N))
            add("containment", f"{nm}_{s}", s, K, M, fk, "approx", "1-containment_miss_asymptotic",
                ("containment_miss_asymptotic", N, K, p, rho), post=one_minus)
        add("mean_true_percentile", f"pctl_{s}", s, K, None, fk, "exact", "mean_true_percentile", ("mean_true_percentile", N, K, rho))
        add("overlap", f"ovl_{s}", s, K, K, fk, "exact", "overlap_fixed_K", ("overlap_fixed_K", N, K, rho))
        add("rej2", f"rej2_{s}", s, K, A_ref, fk, "exact", "rejected_given_top", ("rejected_given_top", N, K, ALPHA_REF, rho))
    for K in BEST_K:
        s = f"K{K}"
        for src in ("best", "main"):
            add("best_paper", f"best_in_K{K}", s, K, None, "fixed-K", "exact", "best_paper_prob", ("best_paper_prob", N, K, rho, "exact"), src=src, size=1)
        add("best_paper", f"best_in_K{K}", s, K, None, "fixed-K", "approx", "best_paper_prob(method=poisson)",
            ("best_paper_prob", N, K, rho, "poisson"), src="best", size=1)
        add("best_paper", f"best_in_K{K}", s, K, None, "fixed-K", "approx", "best_paper_prob_asymptotic",
            ("best_paper_prob_asymptotic", N, K, rho), src="best", size=1)

    # --- fixed-percentile selections (N-free in the limit) --------------------------
    for p in PCTS:
        K = int(round(p * N))
        s, nf = f"p{100 * p:g}pct", "N-free"
        add("precision", f"prec_{s}", s, K, K, nf, "limit", "precision_pct", ("precision_pct", p, rho))
        add("precision", f"prec_{s}", s, K, K, nf, "closed", "precision_pct_finite", ("precision_pct_finite", N, p, rho))
        if K <= EXACT_KMAX:
            add("precision", f"prec_{s}", s, K, K, nf, "exact", "precision_fixed_K", ("precision_fixed_K", N, K, rho))
        for nm, M in (("c2x", 2 * K), ("c10x", 10 * K), ("c1pct", M1), ("c5pct", M5), ("cA", A_ref)):
            if M > N:
                continue
            add("containment", f"{nm}_{s}", s, K, M, nf, "limit", "P2(z_M,z_K;rho)/(K/N)", ("p2_share", N, K, M, rho))
            if K <= EXACT_KMAX:
                add("containment", f"{nm}_{s}", s, K, M, nf, "exact", "containment_fixed_K", ("containment_fixed_K", N, K, M, rho))
        add("mean_true_percentile", f"pctl_{s}", s, K, None, nf, "exact", "mean_true_percentile", ("mean_true_percentile", N, K, rho))
        add("overlap", f"ovl_{s}", s, K, K, nf, "limit", "precision_pct(p,rho^2)", ("precision_pct", p, r12))
        add("overlap", f"ovl_{s}", s, K, K, nf, "closed", "precision_pct_finite(N,p,rho^2)", ("precision_pct_finite", N, p, r12))
        if K <= EXACT_KMAX:
            add("overlap", f"ovl_{s}", s, K, K, nf, "exact", "overlap_fixed_K", ("overlap_fixed_K", N, K, rho))
        add("rej2", f"rej2_{s}", s, K, A_ref, nf, "limit", "1-P2(z_A,z_K;rho^2)/(K/N)", ("p2_share", N, K, A_ref, r12), post=one_minus)
        if K <= EXACT_KMAX:
            add("rej2", f"rej2_{s}", s, K, A_ref, nf, "exact", "rejected_given_top", ("rejected_given_top", N, K, ALPHA_REF, rho))

    # --- acceptance: swap fraction and two-committee disagreement --------------------
    for a in DEFAULT_ALPHAS:
        A = int(round(a * N))
        s, nf = f"acc{a:.2f}", "N-free"
        fa = 2.0 * A / N
        add("swap", f"swap_{s}", s, A, A, nf, "limit", "swap_fraction", ("swap_fraction", a, rho))
        add("swap", f"swap_{s}", s, A, A, nf, "closed", "1-precision_pct_finite", ("precision_pct_finite", N, a, rho), post=one_minus)
        add("disagreement", f"dis_{s}", s, A, A, nf, "limit", "disagreement(alpha,rho^2)", ("disagreement", a, r12))
        add("disagreement", f"dis_{s}", s, A, A, nf, "closed", "1-precision_pct_finite(N,alpha,rho^2)",
            ("precision_pct_finite", N, a, r12), post=one_minus)
        add("inconsistent", f"incons_{s}", s, A, A, nf, "limit", "inconsistent_share(alpha,rho^2)", ("inconsistent_share", a, r12))
        add("inconsistent", f"incons_{s}", s, A, A, nf, "closed", "2(A/N)(1-precision_pct_finite(N,alpha,rho^2))",
            ("precision_pct_finite", N, a, r12), post=lambda v, fa=fa: fa * (1.0 - v))
        if A <= EXACT_KMAX:
            add("swap", f"swap_{s}", s, A, A, nf, "exact", "1-precision_fixed_K", ("precision_fixed_K", N, A, rho), post=one_minus)
            add("disagreement", f"dis_{s}", s, A, A, nf, "exact", "1-precision_fixed_K(N,A,rho^2)", ("precision_fixed_K", N, A, r12), post=one_minus)
            add("inconsistent", f"incons_{s}", s, A, A, nf, "exact", "2(A/N)(1-precision_fixed_K(N,A,rho^2))",
                ("precision_fixed_K", N, A, r12), post=lambda v, fa=fa: fa * (1.0 - v))

    # --- correlations: sample correlation bias E r ~ r - r (1 - r^2) / (2 N) ---------------
    bias = lambda r: r - r * (1 - r * r) / (2.0 * N)
    add("corr_qs", "corr_qs", "-", None, None, "N-free", "limit", "sqrt(rho2)", ("rho2", m.sigma_eps, R, SIGMA_Q, 0.0), post=np.sqrt)
    add("corr_qs", "corr_qs", "-", None, None, "N-free", "approx", "sqrt(rho2) - small-sample bias",
        ("rho2", m.sigma_eps, R, SIGMA_Q, 0.0), post=lambda v: bias(np.sqrt(v)))
    add("corr_s12", "corr_s12", "-", None, None, "N-free", "limit", "committee_corr", ("committee_corr", m.sigma_eps, R, SIGMA_Q, 0.0))
    add("corr_s12", "corr_s12", "-", None, None, "N-free", "approx", "committee_corr - small-sample bias",
        ("committee_corr", m.sigma_eps, R, SIGMA_Q, 0.0), post=bias)

    # --- winner rank -------------------------------------------------------------------
    for src in ("best", "main"):
        add("winner_rank", "winner_median", "-", None, None, "fixed-K", "exact", "winner_rank_quantile(q=0.5)",
            ("winner_stats", N, rho), src=src)
    for form in ("semi", "power"):
        add("winner_rank", "winner_median", "-", None, None, "fixed-K", "approx", f"winner_rank_median_asymptotic({form})",
            ("winner_rank_median_asymptotic", N, rho, form), src="best")
    return out


# ---------------------------------------------------------------------------
# Assembly
# ---------------------------------------------------------------------------


def _z(diff, se):
    if not (np.isfinite(diff) and np.isfinite(se)):
        return np.nan
    if se > 0:
        return diff / se
    return 0.0 if abs(diff) < 1e-9 else np.sign(diff) * np.inf


def _poisson_z(obs: float, lam: float) -> float:
    """z of an observed rare count against Poisson(lam), from the mid-p tail (positive = more than expected)."""
    c = float(np.round(obs))
    if c > lam:
        return float(-stats.norm.ppf(stats.poisson.sf(c, lam) + 0.5 * stats.poisson.pmf(c, lam)))
    return float(stats.norm.ppf(stats.poisson.cdf(c, lam) - 0.5 * stats.poisson.pmf(c, lam)))


def _row(spec, an_val, sim, se_sim, reps, seed, se_model=np.nan, se=None, note="", error=""):
    diff = sim - an_val
    se = se_sim if se is None else se
    return dict(quantity=spec["quantity"], metric=spec["metric"], selection=spec["selection"], K=spec["K"], M=spec["M"],
                kind=spec["kind"], role=spec["role"], analytic_fn=spec["analytic_fn"], rho2=spec["rho2"], N=spec["N"],
                src=spec["src"], reps=reps, seed=seed, analytic=an_val, sim=sim, se=se, se_sim=se_sim, se_model=se_model,
                abs_err=abs(diff), rel_err=diff / abs(an_val) if an_val != 0 else np.nan, z=_z(diff, se), note=note, error=error)


def assemble(specs, results, errors, sims) -> pd.DataFrame:
    rows = []
    for sp in specs:
        simrow = sims[(sp["src"], sp["rho2"], sp["N"])]
        reps, seed = int(simrow["reps"]), int(simrow["seed"])
        val = results.get(sp["key"], np.nan)
        err = errors.get(sp["key"], "")
        if sp["metric"] == "winner_median":
            ranks = simrow["_winner_ranks"]
            n = ranks.size
            if sp["role"] == "approx":
                rows.append(_row(sp, float(val), float(np.median(ranks)), np.nan, n, seed, error=err))
                continue
            if not isinstance(val, dict):
                rows.append(_row(sp, np.nan, float(np.median(ranks)), np.nan, n, seed, error=err or "winner_stats failed"))
                continue
            med, dens, sim_med = val[0.5]["m"], val["density"], float(np.median(ranks))
            se_med = np.sqrt(0.25 / n) / dens if dens > 0 else np.nan
            r = _row(sp, float(med), sim_med, np.nan, n, seed, se=se_med, error=err)
            # The sample median of integer ranks is discrete, so z is the test of the exact cdf
            # where the simulated median crosses 1/2: at m if it lies above m, at m - 1 if below.
            F, Fm1 = val[0.5]["F"], val[0.5]["Fm1"]
            cnt = lambda m: np.searchsorted(ranks, m, side="right") / n
            if sim_med > med:
                r["z"] = (cnt(med) - F) / np.sqrt(F * (1 - F) / n)
            elif sim_med < med:
                r["z"] = (cnt(med - 1) - Fm1) / np.sqrt(Fm1 * (1 - Fm1) / n) if 0 < Fm1 < 1 else np.nan
            else:
                r["z"] = 0.0
            r["note"] = "z = exact-cdf test at the median bracket; se = SE of a sample median"
            rows.append(r)
            for q in WINNER_Q:
                mq, F = val[q]["m"], val[q]["F"]
                Fhat = float(np.searchsorted(ranks, mq, side="right") / n)
                se_F = np.sqrt(F * (1 - F) / n)
                spq = dict(sp, metric=f"winner_cdf_q{int(100 * q)}", analytic_fn=f"winner_rank_cdf(N,rho,m_{q:g})", M=mq)
                rows.append(_row(spq, F, Fhat, np.nan, n, seed, se_model=se_F, se=se_F, note=f"m_q={mq}"))
            continue
        if sp["metric"] not in simrow:
            continue
        a = sp["post"](val) if (sp["post"] is not None and np.isfinite(val)) else val
        a = float(a)
        sim, se_sim = float(simrow[sp["metric"]]), float(simrow.get(sp["metric"] + "_se", np.nan))
        if not np.isfinite(sim):
            continue
        se_model, use_model, z_rare = np.nan, False, np.nan
        if sp["quantity"] not in ("mean_true_percentile", "corr_qs", "corr_s12") and np.isfinite(a):
            size = sp["size"]
            to_share = sp["N"] / (2.0 * size) if sp["quantity"] == "inconsistent" else 1.0  # back to the disagreement scale
            pa = min(max(a * to_share, 0.0), 1.0)
            se_model = np.sqrt(pa * (1 - pa) / (size * reps)) / to_share
            trials = size * reps
            use_model = min(pa, 1 - pa) * trials < 25
            if use_model:
                # Rare hits (or rare misses): exact Poisson tail of the observed count.
                ps = sim * to_share
                z_rare = _poisson_z(ps * trials, pa * trials) if pa < 0.5 else -_poisson_z((1 - ps) * trials, (1 - pa) * trials)
        r = _row(sp, a, sim, se_sim, reps, seed, se_model=se_model, se=se_model if use_model else se_sim, error=err,
                 note="rare outcome: se = binomial SE at the analytic value, z = Poisson mid-p tail" if use_model else "")
        if use_model:
            r["z"] = z_rare
        rows.append(r)
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------


def _fmt_rows(d: pd.DataFrame, cols) -> str:
    with pd.option_context("display.width", 200, "display.max_columns", 30, "display.max_colwidth", 48):
        return d[cols].to_string(index=False, float_format=lambda x: f"{x:.6g}")


def summarise(df: pd.DataFrame) -> None:
    print("\n=== Agreement by role (z = (sim - analytic) / SE) ===")
    g = []
    for role, d in df.groupby("role"):
        z = d["z"][np.isfinite(d["z"])]
        g.append(dict(role=role, rows=len(d), finite_z=len(z), mean_z=z.mean(), rms_z=np.sqrt((z**2).mean()),
                      max_abs_z=z.abs().max(), n_gt3=int((z.abs() > 3).sum()), n_gt4=int((z.abs() > 4).sum())))
    print(pd.DataFrame(g).to_string(index=False, float_format=lambda x: f"{x:.3f}"))

    ex = df[df.role.isin(["exact", "closed"])]
    cols = ["metric", "role", "analytic_fn", "rho2", "N", "src", "reps", "analytic", "sim", "se", "rel_err", "z"]
    print("\n=== Worst 15 exact/closed cells by |z| ===")
    print(_fmt_rows(ex.reindex(ex.z.abs().sort_values(ascending=False).index).head(15), cols))

    print("\n=== Exact/closed: mean z by quantity (cells within one run are correlated) ===")
    t = ex[np.isfinite(ex.z)].groupby(["quantity", "role"]).z.agg(["count", "mean", lambda v: np.sqrt((v**2).mean()), lambda v: v.abs().max()])
    t.columns = ["cells", "mean_z", "rms_z", "max_abs_z"]
    print(t.to_string(float_format=lambda x: f"{x:.3f}"))
    print("\n=== Exact/closed: mean z by N and by rho2 ===")
    for col in ("N", "rho2"):
        t = ex[np.isfinite(ex.z)].groupby(col).z.agg(["count", "mean", lambda v: np.sqrt((v**2).mean()), lambda v: (v > 0).mean()])
        t.columns = ["cells", "mean_z", "rms_z", "share_z_pos"]
        print(t.to_string(float_format=lambda x: f"{x:.3f}"))

    fk = ex[(ex.kind == "fixed-K") & (ex.metric != "winner_median")]
    rel_se = fk.se / fk.analytic.abs()
    print("\n=== Fixed-K quantities, exact: relative error ===")
    for lab, d in (("all cells", fk), ("cells with SE/analytic < 1%", fk[rel_se < 0.01]), ("cells with SE/analytic < 5%", fk[rel_se < 0.05])):
        r = d.rel_err.abs()
        print(f"  {lab:32s} n={len(d):4d}  median |rel| = {r.median():.2e}  90th pct = {r.quantile(0.9):.2e}  max = {r.max():.2e}")
    for N, d in fk.groupby("N"):
        r = d.rel_err.abs()
        print(f"  N={N:>8d}: n={len(d):3d}  median |rel| = {r.median():.2e}  max = {r.max():.2e}  median SE/analytic = {(d.se / d.analytic.abs()).median():.2e}")

    nfree = df[df.kind == "N-free"]
    print("\n=== N-free quantities: absolute error ===")
    for role, d in nfree.groupby("role"):
        print(f"  {role:7s} n={len(d):4d}  median |err| = {d.abs_err.median():.2e}  max |err| = {d.abs_err.max():.2e}  "
              f"RMS z = {np.sqrt((d.z[np.isfinite(d.z)] ** 2).mean()):.2f}")
    lim = nfree[nfree.role == "limit"]
    print("  limit rows, worst |z| (finite-N bias of the N-free value):")
    print(_fmt_rows(lim.reindex(lim.z.abs().sort_values(ascending=False).index).head(8), cols))
    for N, d in lim.groupby("N"):
        z = d.z[np.isfinite(d.z)]
        print(f"  limit N={N:>8d}: mean z = {z.mean():+.2f}, RMS z = {np.sqrt((z**2).mean()):.2f}, max |err| = {d.abs_err.max():.2e}")

    ap = df[df.role == "approx"]
    print("\n=== Approximate laws (information): |approx - exact| / exact, no Monte Carlo noise; median / max per N ===")
    t = ap.assign(arel=ap.vs_exact_rel.abs()).pivot_table(index="analytic_fn", columns="N", values="arel", aggfunc=["median", "max"])
    print(t.to_string(float_format=lambda x: f"{x:.2e}"))
    print("  (corr rows have no exact counterpart; their |rel err| against the simulator:",
          ap[ap.quantity.str.startswith("corr")].groupby("analytic_fn").rel_err.apply(lambda v: v.abs().max()).to_dict(), ")")

    bad = df[df.error.astype(str).str.len() > 0]
    if len(bad):
        print("\n=== Analytic calls that raised ===")
        print(_fmt_rows(bad.drop_duplicates("analytic_fn"), ["analytic_fn", "rho2", "N", "error"]))
    else:
        print("\nNo analytic call raised an exception.")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=MAX_WORKERS)
    ap.add_argument("--salt", default="v1", help="changes every seed")
    ap.add_argument("--cache", default=None, help="pickle of raw results; reused when present")
    ap.add_argument("--out", default=OUT)
    ap.add_argument("--rho2", type=float, nargs="*", default=list(RHO2S))
    ap.add_argument("--N", type=int, nargs="*", default=list(NS))
    ap.add_argument("--kinds", nargs="*", default=["main", "best"], choices=["main", "best"], help="which simulations to run")
    args = ap.parse_args()
    workers = max(1, min(args.workers, MAX_WORKERS))

    # Setup checks: the inversion hits the target reliability, and analytic.rho2 equals the model's.
    for r2 in args.rho2:
        m = model(r2)
        assert abs(m.reliability - r2) < 1e-12 and abs(float(an.rho2(m.sigma_eps, R, SIGMA_Q)) - r2) < 1e-12
        assert abs(float(an.committee_corr(m.sigma_eps, R, SIGMA_Q)) - r2) < 1e-12

    specs = [s for r2 in args.rho2 for N in args.N for s in specs_for(r2, N) if s["src"] in args.kinds]
    keys = list(dict.fromkeys(s["key"] for s in specs))
    sim_tasks = [(k, r2, N, args.salt) for r2 in args.rho2 for N in args.N for k in args.kinds]

    cache = {}
    if args.cache and os.path.exists(args.cache):
        with open(args.cache, "rb") as f:
            cache = pickle.load(f)
    results, errors, allsims = cache.get("results", {}), cache.get("errors", {}), cache.get("sims", {})
    # Simulations are cached per salt; analytic values do not depend on the salt.
    allsims = {(k if len(k) == 4 else (*k, "v1")): v for k, v in allsims.items()}
    sims = {k[:3]: v for k, v in allsims.items() if k[3] == args.salt}
    todo_keys = [k for k in keys if k not in results]
    todo_sims = [t for t in sim_tasks if (t[0], t[1], t[2]) not in sims]

    def sim_cost(t):
        return t[2] * (simmod.default_reps(t[2]) * 2.0 if t[0] == "main" else best_reps(t[2]) * 0.3)

    todo_sims.sort(key=sim_cost, reverse=True)
    todo_keys.sort(key=_analytic_cost, reverse=True)
    total = len(todo_sims) + len(todo_keys)
    print(f"{len(sim_tasks)} simulations ({len(todo_sims)} to run), {len(keys)} analytic calls ({len(todo_keys)} to run), {workers} workers",
          flush=True)

    def save():
        if args.cache:
            with open(args.cache, "wb") as f:
                allsims.update({(*k, args.salt): v for k, v in sims.items()})
                pickle.dump(dict(results=results, errors=errors, sims=allsims), f)

    if total:
        with ProcessPoolExecutor(max_workers=workers) as ex:
            futs = [ex.submit(run_sim, t) for t in todo_sims] + [ex.submit(run_analytic, k) for k in todo_keys]
            for i, f in enumerate(as_completed(futs), 1):
                res = f.result()
                if len(res) == 2:
                    (kind, r2, N, _), row = res
                    sims[(kind, r2, N)] = row
                    print(f"  sim {kind:4s} rho2={r2} N={N} reps={row['reps']} done ({i}/{total})", flush=True)
                    save()
                else:
                    key, v, err = res
                    results[key] = v
                    if err:
                        errors[key] = err
                    if i % 100 == 0:
                        save()
                        print(f"  {i}/{total} tasks done", flush=True)
        save()

    df = assemble(specs, results, errors, sims)
    ex = df[df.role == "exact"].drop_duplicates(["metric", "rho2", "N", "src"]).set_index(["metric", "rho2", "N", "src"]).analytic
    idx = pd.MultiIndex.from_frame(df[["metric", "rho2", "N", "src"]])
    ref = ex.reindex(idx).to_numpy()
    df["vs_exact_rel"] = np.where(df.role == "approx", (df.analytic - ref) / np.abs(ref), np.nan)
    df = df.sort_values(["quantity", "metric", "role", "analytic_fn", "rho2", "N", "src"]).reset_index(drop=True)
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    df.to_csv(args.out, index=False)
    print(f"\nwrote {args.out} ({len(df)} rows)")
    # The simulator's own pooled median equals the median of the raw ranks it kept.
    sims = {k: v for k, v in sims.items() if k[0] in args.kinds and k[1] in args.rho2 and k[2] in args.N}
    for (kind, r2, N), row in sims.items():
        assert row["winner_rank_median"] == float(np.median(row["_winner_ranks"])), (kind, r2, N)
    summarise(df)


if __name__ == "__main__":
    sys.exit(main())
