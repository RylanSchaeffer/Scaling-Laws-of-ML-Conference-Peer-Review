"""Reviews per paper that hold each tier's overlap at its 1,000-submission value, as conferences grow.

For each N on the submissions grid and each R on a ladder of reviews per paper, one simulation gives
the overlap of two reviews' tiers (the proportion of one review's tier that the other also puts there):
the top ten (a constant number), the orals and the spotlights (NeurIPS's fitted trends,
results/tier_sizes.csv) and the accepted papers (25% of N). The target for each tier is its overlap at
N = 1,000 with four reviews. R_needed is where the overlap-against-R curve crosses the target,
interpolated in log R between ladder rungs; inf once the top rung (R_MAX = 64) falls short. Main
model: the per-review noise held at its R = 4 calibration, the chairs' call on (sigma_eta = 0.59).

Writes results/R_needed_tiers.csv: one row per (N, R) with every overlap, and results/R_needed_tiers_summary.csv:
one row per (tier, N) with target, R_needed and the ladder's overlaps.
Usage: uv run python scripts/run_R_needed_tiers.py [--workers 8] [--reps 1000]
"""
from __future__ import annotations

import argparse
import os
import time
from concurrent.futures import ProcessPoolExecutor, as_completed

import numpy as np
import pandas as pd

from peerreview.levels import ROOT, calibrated, main_model
from peerreview.model import MAIN_FORM
from peerreview.simulate import simulate_best_paper, stable_seed
from peerreview.tiers import tier_size

N_GRID = [1000, 2154, 4642, 10_000, 21_544, 46_416, 100_000]
R_LADDER = [4, 5, 6, 8, 10, 12, 16, 20, 24, 32, 40, 48, 64]
R_MAX = R_LADDER[-1]
TIERS = ("top10", "oral", "spot", "accept")


def job(spec: dict) -> dict:
    m = calibrated(main_model(sigma_u=0.0), "central").replace(R=spec["R"])
    N = spec["N"]
    tiers = {"top10": 10, "oral": spec["orals"], "spot": spec["orals"] + spec["spotlights"], "accept": int(round(0.25 * N))}
    t0 = time.perf_counter()
    r = simulate_best_paper(m, N, spec["reps"], best_K=(1,), seed=stable_seed(m.as_dict(), N, spec["reps"], "R_needed_tiers"),
                            second_committee=True, overlap_tiers=tiers)
    out = dict(spec)
    out.update({f"overlap_{t}": float(r[f"overlap_{t}"]) for t in TIERS})
    out.update({f"overlap_{t}_se": float(r.get(f"overlap_{t}_se", np.nan)) for t in TIERS})
    out["sigma_eps"] = m.sigma_eps
    out["wall_s"] = time.perf_counter() - t0
    return out


def r_needed(Rs: np.ndarray, ov: np.ndarray, target: float) -> float:
    """Smallest R at which the overlap reaches the target, interpolated in log R; inf if R_MAX falls short."""
    if ov[0] >= target:
        return float(Rs[0])
    for i in range(1, len(Rs)):
        if ov[i] >= target:
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
             for N in N_GRID for R in R_LADDER]
    specs.sort(key=lambda s: -s["N"] * s["R"])
    rows, t0 = [], time.perf_counter()
    with ProcessPoolExecutor(max_workers=args.workers) as ex:
        futs = [ex.submit(job, s) for s in specs]
        for i, fu in enumerate(as_completed(futs), 1):
            r = fu.result()
            rows.append(r)
            print(f"[{i}/{len(specs)} {time.perf_counter() - t0:.0f}s] N={r['N']} R={r['R']}: top10 {r['overlap_top10']:.3f} oral {r['overlap_oral']:.3f} "
                  f"spot {r['overlap_spot']:.3f} accept {r['overlap_accept']:.3f} ({r['wall_s']:.0f}s)", flush=True)
    df = pd.DataFrame(rows).sort_values(["N", "R"])
    df.to_csv(os.path.join(ROOT, "results", "R_needed_tiers.csv"), index=False)
    base = df[(df.N == N_GRID[0]) & (df.R == MAIN_FORM["R"])].iloc[0]
    summary = []
    for t in TIERS:
        target = float(base[f"overlap_{t}"])
        for N in N_GRID:
            d = df[df.N == N].sort_values("R")
            summary.append({"tier": t, "N": N, "target": target, "R_needed": r_needed(d.R.values, d[f"overlap_{t}"].values, target),
                            "overlap_at_4": float(d[f"overlap_{t}"].iloc[0]), "overlap_at_64": float(d[f"overlap_{t}"].iloc[-1]),
                            "size": int({"top10": 10, "oral": d.orals.iloc[0], "spot": d.orals.iloc[0] + d.spotlights.iloc[0], "accept": round(0.25 * N)}[t])})
    s = pd.DataFrame(summary)
    s.to_csv(os.path.join(ROOT, "results", "R_needed_tiers_summary.csv"), index=False)
    print(s.pivot(index="N", columns="tier", values="R_needed").round(1).to_string())


if __name__ == "__main__":
    main()
