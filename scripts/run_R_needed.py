"""How many reviews per paper keep the top-10 overlap of two reviews at its 1,000-submission value as
conferences grow, on the main review form (integer 1-10 scores)?

The target is the overlap at N = 1,000 with the form's four reviews per paper, central level. For
each N the script simulates the overlap with R reviews per paper, the per-review noise held at its
R = 4 calibration (more reviewers of the same kind), and finds by bisection on integer R the
smallest R whose overlap reaches the target; R_needed interpolates linearly between that R and the
one below. Without shared noise (sigma_u = 0) and with it (sigma_u = 0.5, recalibrated at R = 4),
where a ceiling can make the target unreachable (R_needed = inf once R > R_MAX fails).

Writes results/R_needed.csv.
Usage: uv run python scripts/run_R_needed.py [--workers 2] [--reps 1000]
"""
from __future__ import annotations

import argparse
import os
import time
from concurrent.futures import ProcessPoolExecutor

import numpy as np
import pandas as pd

from peerreview.levels import ROOT, calibrated
from peerreview.model import MAIN_FORM, ReviewModel
from peerreview.simulate import simulate_best_paper, stable_seed

K = 10
N_GRID = [1000, 2154, 4642, 10_000, 21_544, 46_416, 100_000]
R_MAX = 64
FORM = MAIN_FORM  # integer 1-10 scores, four reviews per paper


def overlap(m: ReviewModel, N: int, R: int, reps: int) -> float:
    mR = m.replace(R=R)
    r = simulate_best_paper(mR, N, reps, best_K=(1,), seed=stable_seed(mR.as_dict(), N, reps, "R_needed"),
                            second_committee=True, overlap_tiers={"top10": K})
    return float(r["overlap_top10"])


def job(spec: tuple) -> dict:
    su, N, reps = spec
    m = calibrated(ReviewModel(**FORM, sigma_u=su), "central")
    t0 = time.perf_counter()
    target = overlap(m, N_GRID[0], FORM["R"], reps)
    evals = {}

    def f(R: int) -> float:
        if R not in evals:
            evals[R] = overlap(m, N, R, reps)
        return evals[R]

    lo, hi = FORM["R"], FORM["R"]
    if f(lo) >= target:
        R_needed = float(lo)
    else:
        while f(hi) < target and hi < R_MAX:
            lo, hi = hi, min(2 * hi, R_MAX)
        if f(hi) < target:
            R_needed = np.inf
        else:
            while hi - lo > 1:  # bisection on integer R: f(lo) < target <= f(hi)
                mid = (lo + hi) // 2
                if f(mid) < target:
                    lo = mid
                else:
                    hi = mid
            R_needed = lo + (target - f(lo)) / (f(hi) - f(lo))  # linear interpolation
    return {"metric": "overlap", "sigma_u": su, "N": N, "target": target, "R_needed": R_needed, "reps": reps,
            "sigma_eps": m.sigma_eps, "scale": m.scale, "evals": len(evals),
            "evals_detail": ";".join(f"{R}:{v:.4f}" for R, v in sorted(evals.items())),
            "wall_s": time.perf_counter() - t0}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=2)
    ap.add_argument("--reps", type=int, default=1000)
    args = ap.parse_args()
    specs = [(su, N, args.reps) for su in (0.0, 0.5) for N in N_GRID]
    specs.sort(key=lambda s: -s[1])
    t0 = time.perf_counter()
    rows = []
    with ProcessPoolExecutor(max_workers=args.workers) as ex:
        for r in ex.map(job, specs):
            rows.append(r)
            print(f"[{time.perf_counter() - t0:.0f}s] sigma_u={r['sigma_u']} N={r['N']}: R_needed={r['R_needed']:.2f} "
                  f"(target {r['target']:.4f}, {r['evals']} evals, {r['wall_s']:.0f}s)", flush=True)
    df = pd.DataFrame(rows).sort_values(["sigma_u", "N"])
    path = os.path.join(ROOT, "results", "R_needed.csv")
    df.to_csv(path, index=False)
    print(f"wrote {path}")


if __name__ == "__main__":
    main()
