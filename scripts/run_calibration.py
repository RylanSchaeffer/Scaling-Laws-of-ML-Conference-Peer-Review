"""Calibration (handoff §7): reliability estimates, the three levels, and per-variant
recalibration of sigma_eps by bisection.

Writes
  results/calibration_reliability.csv  every rho^2 estimate of §7.1 and §7.2
  results/calibration_levels.csv       the three levels and their analytic sigma_eps
  results/calibration_variants.csv     calibrated sigma_eps per (variant, level)

Usage: uv run python scripts/run_calibration.py [--workers 5]
"""

from __future__ import annotations

import argparse
import os
import time
from concurrent.futures import ProcessPoolExecutor, as_completed

import numpy as np
import pandas as pd

from peerreview import analytic as an
from peerreview.calibrate import calibrate_sigma_eps, reliability_table
from peerreview.levels import CAL_ALPHA, CALIB_CSV, LEVELS, ROOT, target_dis
from peerreview.model import ReviewModel
from peerreview.simulate import stable_seed

CAL_N, CAL_REPS, CAL_TOL = 5000, 2000, 5e-4


def placement_variants() -> list[ReviewModel]:
    """Alternative placements of coarse scales on the latent axis (§3.2), central level only."""
    out = []
    # Native range: points 1..k with the latent distribution mapped affinely onto [1, k].
    for k, name in ((6, "six"), (5, "five")):
        f = (k - 1) / 9.0
        out.append(ReviewModel(R=4, scale="custom", scale_points=tuple(float(i) for i in range(1, k + 1)),
                               mu_q=1 + 4.0 * f, sigma_q=1.2 * f))
    # Latent mean shifted by half a grid step relative to the points.
    for scale, shift in (("int10", 0.5), ("six", 0.9), ("iclr6", 0.5), ("five", 1.125)):
        out.append(ReviewModel(R=4, scale=scale, mu_q=5.0 + shift))
    return out


def bisection_variants() -> list[tuple[ReviewModel, tuple[str, ...]]]:
    v: list[tuple[ReviewModel, tuple[str, ...]]] = []
    all_levels = tuple(LEVELS)
    # (e) score scales at R = 4, plus a continuous bisection check of the analytic inverse.
    for scale in ("int10", "six", "iclr6", "five", "continuous"):
        v.append((ReviewModel(R=4, scale=scale), all_levels))
    for m in placement_variants():
        v.append((m, ("central",)))
    # (d) quality tails at R = 3, Gaussian and t3 noise.
    for qd in ("beta", "exp", "t3", "lognormal"):
        v.append((ReviewModel(R=3, quality=qd), all_levels))
    for qd in ("gaussian", "beta", "exp", "t3", "lognormal"):
        v.append((ReviewModel(R=3, quality=qd, noise="t3"), all_levels))
    # §3.5 validation variants at R = 4 (Gaussian ones are analytic).
    for qd, nz in (("gaussian", "t3"), ("beta", "gaussian"), ("beta", "t3"), ("exp", "gaussian")):
        v.append((ReviewModel(R=4, quality=qd, noise=nz), all_levels))
    return v


def _job(m: ReviewModel, level: str) -> dict:
    seed = stable_seed(m.as_dict(), level, "calibration")
    t0 = time.perf_counter()
    res = calibrate_sigma_eps(m, target_dis(level), alpha=CAL_ALPHA, N=CAL_N, reps=CAL_REPS, seed=seed, tol=CAL_TOL)
    d = m.as_dict()
    d.pop("sigma_eps")
    return {**d, "level": level, "rho2_level": LEVELS[level], "target_dis": target_dis(level),
            "method": "bisection", **res, "wall_s": time.perf_counter() - t0}


def analytic_rows() -> list[dict]:
    rows = []
    for R in (1, 2, 3, 4, 5, 6, 8, 10, 15, 20, 50):
        for su in (0.0, 0.5):
            for level, r2 in LEVELS.items():
                m = ReviewModel(R=R, sigma_u=su)
                d = m.as_dict()
                d.pop("sigma_eps")
                rows.append({**d, "level": level, "rho2_level": r2, "target_dis": target_dis(level),
                             "method": "analytic", "sigma_eps": float(an.sigma_eps_for_rho2(r2, R, 1.2, su)),
                             "achieved": target_dis(level), "converged": True, "alpha": CAL_ALPHA})
    return rows


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=5)
    args = ap.parse_args()
    os.makedirs(os.path.join(ROOT, "results"), exist_ok=True)

    pd.DataFrame(reliability_table()).to_csv(os.path.join(ROOT, "results", "calibration_reliability.csv"), index=False)
    lv = []
    for level, r2 in LEVELS.items():
        row = {"level": level, "rho2": r2, "rho": np.sqrt(r2), "cal_alpha": CAL_ALPHA, "target_dis": target_dis(level),
               "target_incons": 2 * CAL_ALPHA * target_dis(level)}
        for R in (3, 4):
            for su in (0.0, 0.5):
                row[f"sigma_eps_R{R}_su{su:g}"] = float(an.sigma_eps_for_rho2(r2, R, 1.2, su))
        lv.append(row)
    pd.DataFrame(lv).to_csv(os.path.join(ROOT, "results", "calibration_levels.csv"), index=False)
    print(pd.DataFrame(lv).round(4).to_string(index=False))

    jobs = [(m, lev) for m, levels in bisection_variants() for lev in levels]
    rows = analytic_rows()
    t0 = time.perf_counter()
    with ProcessPoolExecutor(max_workers=args.workers) as ex:
        futs = [ex.submit(_job, m, lev) for m, lev in jobs]
        for i, f in enumerate(as_completed(futs), 1):
            r = f.result()
            rows.append(r)
            print(f"[{i}/{len(jobs)} {time.perf_counter() - t0:.0f}s] R={r['R']} {r['scale']} {r['quality']}/{r['noise']} "
                  f"mu={r['mu_q']} {r['level']}: sigma_eps={r['sigma_eps']:.4f} dis={r['achieved']:.4f} "
                  f"(target {r['target_dis']:.4f}) converged={r['converged']}", flush=True)
    df = pd.DataFrame(rows)
    df.to_csv(CALIB_CSV, index=False)
    bad = df[~df["converged"].astype(bool)]
    if len(bad):
        print("NOT CONVERGED:\n", bad.to_string())


if __name__ == "__main__":
    main()
