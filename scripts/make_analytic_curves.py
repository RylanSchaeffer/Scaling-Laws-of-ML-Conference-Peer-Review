"""Evaluate the analytic results (peerreview.analytic) on the grids the figures use.

Writes results/analytic_curves.csv in long form: one row per
(quantity, level, rho2, K, p, N) with its value. The figures read this file, so every
analytic number in the paper traces to a row here.

Usage: uv run python scripts/make_analytic_curves.py [--workers 6]
"""

from __future__ import annotations

import argparse
import os
from concurrent.futures import ProcessPoolExecutor, as_completed

import numpy as np
import pandas as pd

from peerreview import analytic as an
from peerreview.levels import LEVELS, ROOT

N_FINE = np.geomspace(1e3, 1e6, 46)
RHO2_GRID = np.round(np.linspace(0.05, 0.95, 37), 4)


def _row(q, level, r2, N, v, K=np.nan, p=np.nan):
    return dict(quantity=q, level=level, rho2=float(r2), K=K, p=p, N=float(N), value=float(v))


def job(spec: tuple) -> list[dict]:
    kind, level, r2, arg = spec
    rho = np.sqrt(r2)
    out = []
    if kind == "prec_K":
        v = an.precision_fixed_K(N_FINE, arg, rho)
        out += [_row("prec_K", level, r2, n, x, K=arg) for n, x in zip(N_FINE, v)]
        a0 = an.precision_fixed_K_asymptotic(N_FINE, arg, rho, order=0)
        out += [_row("prec_K_asym0", level, r2, n, x, K=arg) for n, x in zip(N_FINE, a0)]
        sl = an.local_loglog_slope(N_FINE, arg, rho)
        out += [_row("local_slope", level, r2, n, x, K=arg) for n, x in zip(N_FINE, sl)]
    elif kind == "best":
        v = an.best_paper_prob(N_FINE, arg, rho)
        out += [_row("best_in_K", level, r2, n, x, K=arg) for n, x in zip(N_FINE, v)]
    elif kind == "winner":
        for q in (0.1, 0.5, 0.9):
            v = an.winner_rank_quantile(N_FINE, rho, q)
            out += [_row(f"winner_rank_q{int(100 * q)}", level, r2, n, x) for n, x in zip(N_FINE, v)]
    elif kind == "ovl_K":
        v = an.overlap_fixed_K(N_FINE, arg, rho)
        out += [_row("ovl_K", level, r2, n, x, K=arg) for n, x in zip(N_FINE, v)]
    elif kind == "c1pct_K":
        v = [an.containment_fixed_K(n, arg, int(round(0.01 * n)), rho) for n in N_FINE]
        out += [_row("c1pct_K", level, r2, n, x, K=arg) for n, x in zip(N_FINE, v)]
    elif kind == "rho2_curve":
        # precision at fixed N as a function of reliability (figure 3)
        N, K = arg
        v = an.precision_fixed_K(N, K, rho)
        out.append(_row("prec_K_vs_rho2", level, r2, N, v, K=K))
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=6)
    args = ap.parse_args()
    specs = []
    for level, r2 in LEVELS.items():
        specs += [("prec_K", level, r2, K) for K in (1, 5, 10, 30, 100)]
        specs += [("best", level, r2, K) for K in (1, 5, 10, 30)]
        specs += [("winner", level, r2, None)]
        specs += [("ovl_K", level, r2, K) for K in (10, 30)]
        specs += [("c1pct_K", level, r2, 10)]
    for r2 in RHO2_GRID:
        specs += [("rho2_curve", "grid", r2, (N, K)) for N in (1e3, 1e4, 1e5, 1e6) for K in (10,)]
    rows = []
    with ProcessPoolExecutor(max_workers=args.workers) as ex:
        futs = {ex.submit(job, s): s for s in specs}
        for i, f in enumerate(as_completed(futs), 1):
            rows += f.result()
            if i % 10 == 0 or i == len(specs):
                print(f"  {i}/{len(specs)} analytic jobs done", flush=True)

    # Closed forms that need no quadrature.
    for level, r2 in list(LEVELS.items()) + [("grid", r) for r in RHO2_GRID]:
        rho = np.sqrt(r2)
        for p in (0.003, 0.005, 0.01, 0.05, 0.2, 0.10, 0.15, 0.25, 0.30, 0.35, 0.40):
            rows.append(_row("prec_pct", level, r2, np.nan, an.precision_pct(p, rho), p=p))
            rows.append(_row("dis", level, r2, np.nan, an.disagreement(p, r2), p=p))
            # Two-committee overlap of the top-p sets: the precision formula at correlation rho^2.
            rows.append(_row("ovl_pct", level, r2, np.nan, an.precision_pct(p, r2), p=p))
        rows.append(_row("beta", level, r2, np.nan, (1 - rho) / (1 + rho)))
        rows.append(_row("beta2", level, r2, np.nan, (1 - r2) / (1 + r2)))  # decay exponent of two-committee overlap
    for level, r2 in LEVELS.items():
        rho = np.sqrt(r2)
        for K in (1, 10, 30):
            ek = an.expected_kth_best(N_FINE, K)
            rows += [_row("E_kth_best", level, r2, n, x, K=K) for n, x in zip(N_FINE, ek)]
        e1 = an.expected_kth_best(N_FINE, 1)
        rows += [_row("E_quality_top_score", level, r2, n, rho * x) for n, x in zip(N_FINE, e1)]
        rows.append(_row("cond_sd", level, r2, np.nan, an.conditional_quality_sd(rho)))
        # Rerun framing: the top-scored paper's expected standardised score under a second
        # committee is rho^2 E[S*_(1)], with conditional SD sqrt(1 - rho^4) (correlation rho^2).
        rows += [_row("E_score2_top_score", level, r2, n, r2 * x) for n, x in zip(N_FINE, e1)]
        rows.append(_row("cond_sd2", level, r2, np.nan, an.conditional_quality_sd(r2)))
        # Fixed-share precision at finite N (K = round(pN) >= 10 here, where the closed
        # form matches the exact integral to 0.1%); figure 1 draws these.
        for p in (0.01, 0.10):
            v = [an.precision_pct_finite(n, p, rho) for n in N_FINE]
            rows += [_row("prec_pct_finite", level, r2, n, x, p=p) for n, x in zip(N_FINE, v)]
            v = [an.precision_pct_finite(n, p, r2) for n in N_FINE]  # two-committee overlap at finite N
            rows += [_row("ovl_pct_finite", level, r2, n, x, p=p) for n, x in zip(N_FINE, v)]
    df = pd.DataFrame(rows)
    out = os.path.join(ROOT, "results", "analytic_curves.csv")
    df.to_csv(out, index=False)
    print(df.groupby("quantity").size())


if __name__ == "__main__":
    main()
