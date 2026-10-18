"""Merge the two parts of the reviews ladder and compute the reviews per paper that hold each tier.

Reads results/R_needed_tiers_exact.csv (R <= 32, every review drawn; run_R_needed_tiers.py),
results/R_needed_tiers_clt.csv (R >= 32 and inf by the normal approximation; run_R_needed_tiers_large.py)
and results/R_needed_tiers_limit.csv (R = inf on a fine grid of sizes).

The target for each tier is its overlap at 1,000 submissions with four reviews. R_needed(N) is where
the ladder's overlap crosses the target, interpolated in log R between rungs: the exact rungs up to 32,
the approximate ones above. It is inf where even R = inf falls short. N* is the size at which the
R = inf overlap falls to the target: from there on no number of reviews holds that tier.

Writes results/R_needed_tiers.csv (every rung, column method: exact / clt / limit) and
results/R_needed_tiers_summary.csv (one row per tier and size, with N_star), and prints the check of
the approximation against the exact rungs at 32 and 64. The figure's curve, results/R_needed_tiers_curve.csv,
is smooth in N: each exact rung's overlap and the R = inf overlap are fitted across sizes (log overlap quadratic
in log N, weighted by 1/SE^2); at each size the exact rungs give the curve up to 32 reviews and above 32 the deficit
below the limit falls as R^-b (b pooled from the approximate rungs, about 0.9), so that Monte Carlo noise near the
vertical asymptote at N* does not bend the curve; N* is where the fitted R = inf overlap meets the target.
Usage: uv run python scripts/summarize_R_needed_tiers.py
"""
from __future__ import annotations

import os

import numpy as np
import pandas as pd
from scipy.interpolate import PchipInterpolator
from scipy.optimize import brentq

from peerreview.levels import ROOT
from peerreview.model import MAIN_FORM
from run_R_needed_tiers import N_GRID, R_LADDER, TIERS
from run_R_needed_tiers_large import n_star
from run_best_paper import N_BEST


def r_needed(Rs: np.ndarray, ov: np.ndarray, target: float) -> float:
    """Smallest R at which the overlap reaches the target: a monotone cubic through the finite rungs in log R, solved for the
    target between the two rungs that bracket it; inf when even R = inf falls short (or the target is reached only in the limit)."""
    if ov[0] >= target:
        return float(Rs[0]) if Rs[0] <= MAIN_FORM["R"] else float("nan")  # nan: the target lies below the ladder's first rung
    fin = np.isfinite(Rs)
    x, y = np.log(Rs[fin]), ov[fin]
    for i in range(1, len(x)):
        if y[i] >= target:
            if i >= 2 and np.all(np.diff(y[: i + 1]) > 0):  # smooth where the ladder up to the bracketing rung is monotone
                f = PchipInterpolator(x[: i + 1], y[: i + 1])
                return float(np.exp(brentq(lambda v: f(v) - target, x[i - 1], x[i])))
            frac = (target - y[i - 1]) / (y[i] - y[i - 1])
            return float(np.exp(x[i - 1] + frac * (x[i] - x[i - 1])))
    return float("inf")


def fit_rung(N: np.ndarray, y: np.ndarray, se: np.ndarray):
    """log overlap as a quadratic in log N across the sizes of one rung, weighted by 1/SE^2; returns overlap(N)."""
    w = 1.0 / np.maximum(np.nan_to_num(se, nan=np.nanmedian(se) if np.isfinite(se).any() else 1.0), 1e-4)
    coef = np.polyfit(np.log(N), np.log(np.maximum(y, 1e-6)), 2, w=w)
    return lambda n: np.exp(np.polyval(coef, np.log(n)))


def deficit_exponent(clt: pd.DataFrame, limit_of: dict, R_max: int = 256) -> float:
    """b in overlap(R) = limit - a R^-b, pooled over tiers and sizes from the approximate rungs 32 to R_max whose deficit
    below the limit is well resolved (more than 3 SE); a is free per tier and size."""
    xs, ys = [], []
    for t in TIERS:
        if t == "accept":
            continue
        for N, g in clt[np.isfinite(clt.R) & (clt.R <= R_max)].groupby("N"):
            d = limit_of[t](N) - g[f"overlap_{t}"].values
            ok = d > 3 * g[f"overlap_{t}_se"].values
            if ok.sum() >= 3:
                x, y = np.log(g.R.values[ok]), np.log(d[ok])
                xs.append(x - x.mean())
                ys.append(y - y.mean())
    x, y = np.concatenate(xs), np.concatenate(ys)
    return float(-(x @ y) / (x @ x))


def smooth_curve(exact: pd.DataFrame, clt: pd.DataFrame, limits: pd.DataFrame, targets: dict, N_fine: np.ndarray) -> tuple[pd.DataFrame, float]:
    """R_needed(N) on a fine grid of sizes, smooth in N.

    Every exact rung's overlap (R = 4 to 32) and the R = inf overlap are fitted across sizes; at each size the exact rungs
    give the overlap-against-R curve up to 32 reviews (monotone cubic in log R), and above 32 the deficit below the
    R = inf limit falls as R^-b, anchored at the 32-review rung, with b pooled from the approximate rungs. R_needed is
    where that curve meets the target; inf where the limit itself is below the target."""
    exact = exact[exact.R.isin(R_LADDER)]  # the 64-review rows are a check on the approximation, not a rung of the curve
    exact_R = np.array(sorted(exact.R.unique()))
    limit_of = {}
    for t in TIERS:
        limit_of[t] = fit_rung(limits.N.values, limits[f"overlap_{t}"].values, limits[f"overlap_{t}_se"].values)
    b = deficit_exponent(clt, limit_of)
    rows = []
    for t in TIERS:
        rung_of = {R: fit_rung(exact[exact.R == R].N.values, exact[exact.R == R][f"overlap_{t}"].values, exact[exact.R == R][f"overlap_{t}_se"].values)
                   for R in exact_R}
        for n in N_fine:
            ov = np.array([rung_of[R](n) for R in exact_R])
            lim = float(limit_of[t](n))
            if targets[t] <= ov[-1]:
                R = r_needed(exact_R.astype(float), ov, targets[t])
            elif lim <= targets[t]:
                R = float("inf")
            else:
                R = float(exact_R[-1] * ((lim - ov[-1]) / (lim - targets[t])) ** (1.0 / b))
            rows.append({"tier": t, "N": float(n), "R_needed": R, "limit_overlap": lim, "overlap_at_32": float(ov[-1])})
    return pd.DataFrame(rows), b


def main() -> None:
    res = os.path.join(ROOT, "results")
    exact = pd.read_csv(os.path.join(res, "R_needed_tiers_exact.csv"))
    clt = pd.read_csv(os.path.join(res, "R_needed_tiers_clt.csv"))
    lim = pd.read_csv(os.path.join(res, "R_needed_tiers_limit.csv"))
    for R in sorted(set(exact.R) & set(clt.R)):
        a = exact[exact.R == R].set_index("N")
        b = clt[clt.R == R].set_index("N")
        common = a.index.intersection(b.index)
        for t in TIERS:
            d = (b.loc[common, f"overlap_{t}"] - a.loc[common, f"overlap_{t}"]).abs().max()
            print(f"check R={R:g} {t}: max |approx - exact| = {d:.4f} over {len(common)} sizes")
    ladder = pd.concat([exact, clt[~clt.R.isin(exact.R.unique()) | ~clt.N.isin(exact.N.unique())]], ignore_index=True)
    ladder = ladder.sort_values(["N", "R"])
    ladder.to_csv(os.path.join(res, "R_needed_tiers.csv"), index=False)

    base = exact[(exact.N == N_GRID[0]) & (exact.R == MAIN_FORM["R"])].iloc[0]
    targets = {t: float(base[f"overlap_{t}"]) for t in TIERS}
    limits = pd.concat([lim, clt[clt.method == "limit"]], ignore_index=True)
    N_fine = np.geomspace(N_GRID[0], N_GRID[-1], 401)
    curve, b = smooth_curve(exact, clt, limits, targets, N_fine)
    print(f"deficit exponent b = {b:.3f} (overlap = limit - a R^-b above 32 reviews)")
    stars = {}
    for t in TIERS:  # N*: where the fitted R = inf overlap falls to the target
        c = curve[curve.tier == t]
        stars[t] = n_star(c.N.values, c.limit_overlap.values, targets[t])
    curve["N_star"] = curve.tier.map(stars)
    curve["deficit_exponent"] = b
    curve.to_csv(os.path.join(res, "R_needed_tiers_curve.csv"), index=False)
    rows = []
    for t in TIERS:
        target = targets[t]
        ns = stars[t]
        for N in sorted(ladder.N.unique()):
            d = ladder[ladder.N == N].sort_values("R")
            at4 = d[d.R == MAIN_FORM["R"]][f"overlap_{t}"]
            lim_row = d[~np.isfinite(d.R)][f"overlap_{t}"]
            lim_v = float(lim_row.iloc[0]) if len(lim_row) else np.nan
            rows.append({"tier": t, "N": int(N), "target": target, "R_needed": r_needed(d.R.values.astype(float), d[f"overlap_{t}"].values, target),
                         "overlap_at_4": float(at4.iloc[0]) if len(at4) else np.nan, "limit_overlap": lim_v,
                         "reachable": bool(lim_v >= target) if np.isfinite(lim_v) else np.nan, "N_star": ns,
                         "size": int({"best": N_BEST, "oral": d.orals.iloc[0], "spot": d.orals.iloc[0] + d.spotlights.iloc[0], "accept": round(0.25 * N)}[t])})
    s = pd.DataFrame(rows)
    s.to_csv(os.path.join(res, "R_needed_tiers_summary.csv"), index=False)
    show = s.pivot(index="N", columns="tier", values="R_needed").round(1)
    for t in TIERS:  # the fitted curve at the same sizes, beside the point estimates
        c = curve[curve.tier == t]
        show[f"{t}_fit"] = [float(np.interp(np.log(N), np.log(c.N.values), c.R_needed.values)) for N in show.index]
    print(show.round(1).to_string())
    print("N* (no number of reviews from here on):", {t: (f"{v:,.0f}" if np.isfinite(v) else "none up to 100,000") for t in TIERS for v in [float(s[s.tier == t].N_star.iloc[0])]})


if __name__ == "__main__":
    main()
