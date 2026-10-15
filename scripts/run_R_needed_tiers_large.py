"""Extend results/R_needed_tiers.csv to many reviews per paper, and to infinitely many.

With R reviews a paper's mean snapped score is g(q) + sd(q) z / sqrt(R) to a very good approximation
for R >= 32 (a mean of R bounded, independent reviews), where g(q) = E[snap(q + eps)] and sd(q) its SD
on the 1-10 scale. This script simulates two reviews that way for a ladder of large R and for R = inf
(two reviews share g(q) and differ only by the chair noise), on the same tiers as run_R_needed_tiers.py,
and appends the rows to results/R_needed_tiers.csv; it then recomputes results/R_needed_tiers_summary.csv,
where R_needed is inf only when the R = inf overlap is below the target. It also prints the exact and
approximate overlaps at R = 32 and 64 so the approximation can be checked.

Usage: uv run python scripts/run_R_needed_tiers_large.py [--workers 8] [--reps 1000]
"""
from __future__ import annotations

import argparse
import os
import time
from concurrent.futures import ProcessPoolExecutor, as_completed

import numpy as np
import pandas as pd
from scipy.special import ndtr

from peerreview.levels import ROOT, calibrated, main_model
from peerreview.model import MAIN_FORM, sample_quality
from peerreview.simulate import stable_seed
from peerreview.tiers import tier_size

N_GRID = [1000, 2154, 4642, 10_000, 21_544, 46_416, 100_000]
R_LARGE = [32, 64, 96, 128, 192, 256, 384, 512, 768, 1024, 2048, 4096, np.inf]  # 32 and 64 repeat the exact ladder as a check
TIERS = ("top10", "oral", "spot", "accept")
K10 = 10


def snapped_moments(q: np.ndarray, m) -> tuple[np.ndarray, np.ndarray]:
    """Mean and SD of one snapped review given quality q, on the model's scale."""
    pts = m.points
    mids = (pts[:-1] + pts[1:]) / 2.0
    cdf = ndtr((mids[None, :] - q[..., None]) / m.sigma_eps)
    probs = np.diff(np.concatenate([np.zeros(q.shape + (1,)), cdf, np.ones(q.shape + (1,))], axis=-1), axis=-1)
    mean = (probs * pts).sum(-1)
    var = (probs * pts ** 2).sum(-1) - mean ** 2
    return mean, np.sqrt(np.maximum(var, 0.0))


def overlaps(rng, q, g, sd, R, m, sizes, A):
    """One pair of reviews with R reviewers each (R = inf: no reviewer noise); overlap per tier."""
    N = q.shape[0]
    out = {}
    s = []
    for _ in range(2):
        sbar = g + (sd * rng.standard_normal(N) / np.sqrt(R) if np.isfinite(R) else 0.0)
        acc = np.argpartition(-sbar, A - 1)[:A]
        t = np.full(N, -np.inf)
        t[acc] = sbar[acc] + m.sigma_award * rng.standard_normal(A)
        s.append((sbar, t, set(acc.tolist())))
    (s1, t1, acc1), (s2, t2, acc2) = s
    for name, K in sizes.items():
        if name == "accept":
            out[name] = len(acc1 & acc2) / A
        else:
            top1 = np.argpartition(-t1, K - 1)[:K]
            top2 = np.argpartition(-t2, K - 1)[:K]
            out[name] = len(set(top1.tolist()) & set(top2.tolist())) / K
    return out


def job(spec: dict) -> dict:
    m = calibrated(main_model(sigma_u=0.0), "central")
    N, R, reps = spec["N"], spec["R"], spec["reps"]
    sizes = {"top10": K10, "oral": spec["orals"], "spot": spec["orals"] + spec["spotlights"]}
    A = int(round(0.25 * N))
    sizes["accept"] = A
    rng = np.random.default_rng(stable_seed(m.as_dict(), N, reps, "R_needed_tiers_large", str(R)))
    t0 = time.perf_counter()
    acc = {t: 0.0 for t in TIERS}
    for _ in range(reps):
        q = sample_quality(rng, (N,), m)
        g, sd = snapped_moments(q, m)
        o = overlaps(rng, q, g, sd, R, m, sizes, A)
        for t in TIERS:
            acc[t] += o[t]
    out = dict(spec)
    out.update({f"overlap_{t}": acc[t] / reps for t in TIERS})
    out["sigma_eps"] = m.sigma_eps
    out["method"] = "clt" if np.isfinite(R) else "limit"
    out["wall_s"] = time.perf_counter() - t0
    return out


def r_needed(Rs: np.ndarray, ov: np.ndarray, target: float) -> float:
    """Smallest R at which the overlap reaches the target, interpolated in log R between rungs; inf when even R = inf falls short."""
    finite = np.isfinite(Rs)
    if ov[0] >= target:
        return float(Rs[0])
    for i in range(1, len(Rs)):
        if ov[i] >= target:
            if not finite[i]:
                return float("inf") if ov[i] < target else float(Rs[i - 1]) * 4.0  # reached only in the limit: beyond the last finite rung
            lo, hi = np.log(Rs[i - 1]), np.log(Rs[i])
            f = (target - ov[i - 1]) / (ov[i] - ov[i - 1])
            return float(np.exp(lo + f * (hi - lo)))
    return float("inf")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--reps", type=int, default=1000)
    args = ap.parse_args()
    fits = pd.read_csv(os.path.join(ROOT, "results", "tier_sizes.csv"))
    specs = [{"N": N, "R": R, "orals": tier_size(fits, "orals", N), "spotlights": tier_size(fits, "spotlights", N), "reps": args.reps}
             for N in N_GRID for R in R_LARGE]
    specs.sort(key=lambda s: -s["N"])
    rows, t0 = [], time.perf_counter()
    with ProcessPoolExecutor(max_workers=args.workers) as ex:
        futs = [ex.submit(job, s) for s in specs]
        for i, fu in enumerate(as_completed(futs), 1):
            r = fu.result()
            rows.append(r)
            print(f"[{i}/{len(specs)} {time.perf_counter() - t0:.0f}s] N={r['N']} R={r['R']}: top10 {r['overlap_top10']:.3f} oral {r['overlap_oral']:.3f} "
                  f"spot {r['overlap_spot']:.3f} accept {r['overlap_accept']:.3f} ({r['wall_s']:.0f}s)", flush=True)
    new = pd.DataFrame(rows)
    path = os.path.join(ROOT, "results", "R_needed_tiers.csv")
    old = pd.read_csv(path)
    old = old[old.get("method", pd.Series(["exact"] * len(old))).fillna("exact") == "exact"] if "method" in old else old
    old["method"] = "exact"
    # the check: exact against approximate at R = 32 and 64
    for R in (32, 64):
        a = old[old.R == R].set_index("N"); b = new[new.R == R].set_index("N")
        for t in TIERS:
            d = (b[f"overlap_{t}"] - a[f"overlap_{t}"]).abs().max()
            print(f"check R={R} {t}: max |clt - exact| = {d:.4f}")
    keep = new[~new.R.isin([32, 64])]  # the exact rows stand at 32 and 64
    df = pd.concat([old, keep], ignore_index=True).sort_values(["N", "R"])
    df.to_csv(path, index=False)
    base = df[(df.N == N_GRID[0]) & (df.R == MAIN_FORM["R"])].iloc[0]
    summary = []
    for t in TIERS:
        target = float(base[f"overlap_{t}"])
        for N in N_GRID:
            d = df[df.N == N].sort_values("R")
            lim = float(d[~np.isfinite(d.R)][f"overlap_{t}"].iloc[0])
            summary.append({"tier": t, "N": N, "target": target, "R_needed": r_needed(d.R.values.astype(float), d[f"overlap_{t}"].values, target),
                            "overlap_at_4": float(d[f"overlap_{t}"].iloc[0]), "limit_overlap": lim, "reachable": bool(lim >= target),
                            "size": int({"top10": K10, "oral": d.orals.iloc[0], "spot": d.orals.iloc[0] + d.spotlights.iloc[0], "accept": round(0.25 * N)}[t])})
    s = pd.DataFrame(summary)
    s.to_csv(os.path.join(ROOT, "results", "R_needed_tiers_summary.csv"), index=False)
    print(s.pivot(index="N", columns="tier", values="R_needed").round(1).to_string())
    print(s.pivot(index="N", columns="tier", values="limit_overlap").round(3).to_string())


if __name__ == "__main__":
    main()
