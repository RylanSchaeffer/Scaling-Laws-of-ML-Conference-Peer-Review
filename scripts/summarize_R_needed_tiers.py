"""Merge the two parts of the reviews ladder and compute the reviews per paper that hold each tier.

Reads results/R_needed_tiers_exact.csv (R <= 32, every review drawn; run_R_needed_tiers.py),
results/R_needed_tiers_clt.csv (R >= 32 and inf by the normal approximation; run_R_needed_tiers_large.py)
and results/R_needed_tiers_limit.csv (R = inf on a fine grid of sizes).

The tiers are separate (peerreview.tiers): Best Papers, Oral, Spotlight, Accepted (accepted with no award); the
"or Better" sets are summarised too. The target for each tier is its overlap at 1,000 submissions with four reviews. R_needed(N) is where
the ladder's overlap crosses the target, interpolated in log R between rungs: the exact rungs up to 32,
the approximate ones above. It is inf where even R = inf falls short. N* is the size at which the
R = inf overlap falls to the target: from there on no number of reviews holds that tier.

Writes results/R_needed_tiers.csv (every rung, column method: exact / clt / limit) and
results/R_needed_tiers_summary.csv (one row per tier and size, with N_star), and prints the check of
the approximation against the exact rungs at 32 and 64. The figure's curve, results/R_needed_tiers_curve.csv,
is smooth in N: the R = inf overlap is fitted across sizes (log overlap quadratic in log N, weighted by 1/SE^2), and
for the award groups the deficit below it is one smooth surface in N and R over every exact rung, falling as R^-b above
32 reviews (b pooled from the approximate rungs, about 0.75), so that neither Monte Carlo noise nor a change of rung
bends the curve (smooth_curve); N* is where the fitted R = inf overlap meets the target.
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
from run_R_needed_tiers import N_GRID, R_LADDER, GROUPS
from run_R_needed_tiers_large import n_star
from run_best_paper import N_BEST


def group_sizes(n_oral_or_better: int, n_spot: int, n_accepted: int) -> dict:
    """Papers per separate tier and per "or Better" set (NeurIPS's Orals include its Best Papers)."""
    return {"best": N_BEST, "oral": n_oral_or_better - N_BEST, "spot": n_spot, "accept": n_accepted - n_oral_or_better - n_spot,
            "oral_or_better": n_oral_or_better, "spot_or_better": n_oral_or_better + n_spot, "accept_or_better": n_accepted}


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
    for t in ("best", "oral", "spot", "accept"):  # the separate tiers; Accepted or Better reaches 100% in the limit, so it has no deficit to fit
        for N, g in clt[np.isfinite(clt.R) & (clt.R <= R_max)].groupby("N"):
            d = limit_of[t](N) - g[f"overlap_{t}"].values
            ok = d > 3 * g[f"overlap_{t}_se"].values
            if ok.sum() >= 3:
                x, y = np.log(g.R.values[ok]), np.log(d[ok])
                xs.append(x - x.mean())
                ys.append(y - y.mean())
    x, y = np.concatenate(xs), np.concatenate(ys)
    return float(-(x @ y) / (x @ x))


R_ABOVE = 32.0 * 2.0 ** (np.arange(1, 41) / 2)  # rungs above the exact ladder, 45 to 33 million reviews


SURFACE_GROUPS = ("best", "oral", "spot", "oral_or_better", "spot_or_better")  # the award groups, whose overlap falls with N


def fit_surface(exact: pd.DataFrame, t: str, limit, b: float):
    """log deficit below the R = inf limit as one smooth surface over the exact rungs (R = 4 to 32, every size):
    D(x, u) = P0(x) - b u + u^2 P2(x) + u^3 P3(x), x = log(N / 1e4), u = log(R / 32), each P quadratic, weighted by
    deficit / SE (1 / SE of log deficit); above 32 reviews D = P0(x) - b u, the pooled R^-b tail, with the same slope at
    32. Returns (overlap(N, log R), chi^2 per point)."""
    x = np.log(exact.N.values / 1e4)
    u = np.log(exact.R.values / exact.R.max())
    d = limit(exact.N.values) - exact[f"overlap_{t}"].values
    se = exact[f"overlap_{t}_se"].values
    ok = d > 2 * se  # the deficit is resolved
    basis = lambda x, u: np.stack([x ** k * u ** j for j in (0, 2, 3) for k in range(3)], -1)  # noqa: E731
    w = d[ok] / se[ok]
    z = np.log(d[ok]) + b * u[ok]
    A = basis(x[ok], u[ok])
    coef = np.linalg.lstsq(A * w[:, None], z * w, rcond=None)[0]
    chi2 = float(np.mean(((z - A @ coef) * w) ** 2))
    R_top = float(exact.R.max())

    def overlap(n: float, log_R: float) -> float:
        u = log_R - np.log(R_top)
        D = float(basis(np.array([np.log(n / 1e4)]), np.array([min(u, 0.0)]))[0] @ coef) - b * u
        return float(limit(n)) - np.exp(D)
    return overlap, chi2


def smooth_curve(exact: pd.DataFrame, clt: pd.DataFrame, limits: pd.DataFrame, targets: dict, N_fine: np.ndarray) -> tuple[pd.DataFrame, float]:
    """R_needed(N) on a fine grid of sizes, smooth in N.

    The R = inf overlap is fitted across sizes. For the award groups (SURFACE_GROUPS) the overlap below that limit is one
    smooth surface in N and R over every exact rung (fit_surface), with the deficit falling as R^-b above 32 reviews, b
    pooled from the approximate rungs; R_needed is where it meets the target, inf where the limit is below the target.
    Accepted and Accepted or Better hold their 1,000-submission overlap with four reviews at every size: their curve
    runs through each exact rung's fit across sizes (a monotone cubic in log R, with rungs above 32 whose deficit falls
    as R^-b). Either way R_needed(N) has a continuous slope: no kink where the target crosses a rung."""
    exact = exact[exact.R.isin(R_LADDER)]  # the 64-review rows are a check on the approximation, not a rung of the curve
    exact_R = np.array(sorted(exact.R.unique()))
    limit_of = {}
    for t in GROUPS:
        limit_of[t] = fit_rung(limits.N.values, limits[f"overlap_{t}"].values, limits[f"overlap_{t}_se"].values)
    b = deficit_exponent(clt, limit_of)
    rows = []
    for t in GROUPS:
        if t in SURFACE_GROUPS:
            surf, chi2 = fit_surface(exact, t, limit_of[t], b)
            print(f"surface {t}: chi^2 per point {chi2:.2f}")
        else:
            rung_of = {R: fit_rung(exact[exact.R == R].N.values, exact[exact.R == R][f"overlap_{t}"].values,
                                   exact[exact.R == R][f"overlap_{t}_se"].values) for R in exact_R}
        for n in N_fine:
            lim = float(limit_of[t](n))
            if t in SURFACE_GROUPS:
                ov4, ov32 = surf(n, np.log(exact_R[0])), surf(n, np.log(exact_R[-1]))
                if lim <= targets[t]:
                    R = float("inf")
                elif ov4 >= targets[t]:
                    R = float(exact_R[0])
                else:
                    R = float(np.exp(brentq(lambda v: surf(n, v) - targets[t], np.log(exact_R[0]), np.log(R_ABOVE[-1]))))
                rows.append({"group": t, "N": float(n), "R_needed": R, "limit_overlap": lim, "overlap_at_32": ov32})
                continue
            ov = np.array([rung_of[R](n) for R in exact_R])
            if lim <= targets[t]:
                R = float("inf")
            elif ov[0] >= targets[t]:
                R = float(exact_R[0])
            else:  # one monotone cubic in log R through the exact rungs and the R^-b rungs above them
                ov_above = lim - (lim - ov[-1]) * (R_ABOVE / exact_R[-1]) ** (-b)
                x, y = np.log(np.r_[exact_R.astype(float), R_ABOVE]), np.r_[ov, ov_above]
                f = PchipInterpolator(x, y)
                j = int(np.argmax(y >= targets[t]))
                R = float(np.exp(brentq(lambda v: f(v) - targets[t], x[j - 1], x[j]))) if y[j] >= targets[t] else float("inf")
            rows.append({"group": t, "N": float(n), "R_needed": R, "limit_overlap": lim, "overlap_at_32": float(ov[-1])})
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
        for t in GROUPS:
            d = (b.loc[common, f"overlap_{t}"] - a.loc[common, f"overlap_{t}"]).abs().max()
            print(f"check R={R:g} {t}: max |approx - exact| = {d:.4f} over {len(common)} sizes")
    ladder = pd.concat([exact, clt[~clt.R.isin(exact.R.unique()) | ~clt.N.isin(exact.N.unique())]], ignore_index=True)
    ladder = ladder.sort_values(["N", "R"])
    ladder.to_csv(os.path.join(res, "R_needed_tiers.csv"), index=False)

    base = exact[(exact.N == N_GRID[0]) & (exact.R == MAIN_FORM["R"])].iloc[0]
    targets = {t: float(base[f"overlap_{t}"]) for t in GROUPS}
    limits = pd.concat([lim, clt[clt.method == "limit"]], ignore_index=True)
    N_fine = np.geomspace(N_GRID[0], N_GRID[-1], 401)
    curve, b = smooth_curve(exact, clt, limits, targets, N_fine)
    print(f"deficit exponent b = {b:.3f} (overlap = limit - a R^-b above 32 reviews)")
    stars = {}
    for t in GROUPS:  # N*: where the fitted R = inf overlap falls to the target
        c = curve[curve.group == t]
        stars[t] = n_star(c.N.values, c.limit_overlap.values, targets[t])
    curve["N_star"] = curve.group.map(stars)
    curve["deficit_exponent"] = b
    curve.to_csv(os.path.join(res, "R_needed_tiers_curve.csv"), index=False)
    rows = []
    for t in GROUPS:
        target = targets[t]
        ns = stars[t]
        for N in sorted(ladder.N.unique()):
            d = ladder[ladder.N == N].sort_values("R")
            at4 = d[d.R == MAIN_FORM["R"]][f"overlap_{t}"]
            lim_row = d[~np.isfinite(d.R)][f"overlap_{t}"]
            lim_v = float(lim_row.iloc[0]) if len(lim_row) else np.nan
            rows.append({"group": t, "N": int(N), "target": target, "R_needed": r_needed(d.R.values.astype(float), d[f"overlap_{t}"].values, target),
                         "overlap_at_4": float(at4.iloc[0]) if len(at4) else np.nan, "limit_overlap": lim_v,
                         "reachable": bool(lim_v >= target) if np.isfinite(lim_v) else np.nan, "N_star": ns,
                         "size": int(group_sizes(d.n_oral_or_better.iloc[0], d.spotlights.iloc[0], round(0.25 * N))[t])})
    s = pd.DataFrame(rows)
    s.to_csv(os.path.join(res, "R_needed_tiers_summary.csv"), index=False)
    show = s.pivot(index="N", columns="group", values="R_needed").round(1)
    for t in GROUPS:  # the fitted curve at the same sizes, beside the point estimates
        c = curve[curve.group == t]
        show[f"{t}_fit"] = [float(np.interp(np.log(N), np.log(c.N.values), c.R_needed.values)) for N in show.index]
    print(show.round(1).to_string())
    print("N* (no number of reviews from here on):", {t: (f"{v:,.0f}" if np.isfinite(v) else "none up to 100,000") for t in GROUPS for v in [float(s[s.group == t].N_star.iloc[0])]})


if __name__ == "__main__":
    main()
