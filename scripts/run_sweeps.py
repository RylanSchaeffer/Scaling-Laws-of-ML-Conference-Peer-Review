"""Parameter sweeps (a) to (h) of handoff §5. One CSV per sweep in results/.

  a  N at several sigma_eps (coarse grid + the three calibrated levels), R = 3
  b  R with and without shared noise at N = 2,000 and 20,000 (per-review noise fixed at
     its R = 3 calibration, so both variants match the data at R = 3)
  c  fine sigma_eps grid at N = 1e3, 1e4, 1e5
  d  quality tails (x Gaussian / t3 noise) over N, each recalibrated, R = 3
  e  score scales over N at R = 4, each recalibrated; plus placement checks
  f  acceptance rate at N = 1e4 (10,000 conferences)
  g  main sweep at the calibrated levels over N
  h  high-replication best-paper probability over N

Usage: uv run python scripts/run_sweeps.py a b c ... [--workers 5]
"""

from __future__ import annotations

import argparse
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from peerreview.levels import LEVELS, ROOT, calibrated  # noqa: E402
from peerreview.model import ReviewModel  # noqa: E402
from peerreview.runner import run_tasks  # noqa: E402

N_GRID = [1000, 2000, 5000, 10_000, 20_000, 50_000, 100_000, 200_000, 500_000, 1_000_000]
COARSE = [1.0, 1.5, 2.0, 2.5]
FINE = [round(float(x), 4) for x in np.linspace(0.25, 3.5, 14)]
R_GRID = [1, 2, 3, 4, 5, 6, 8, 10, 15, 20, 50]
SEL = dict(fixed_K=[1, 5, 10, 30, 100], pct=[0.003, 0.005, 0.01, 0.05, 0.2])


def md(m: ReviewModel) -> dict:
    d = m.as_dict()
    d["scale_points"] = tuple(m.scale_points)
    return d


def sim(sweep, m, N, reps=None, **extra):
    return dict(sweep=sweep, kind="simulate", model=md(m), N=N, reps=reps, sel=SEL, two_committees=True, extra=extra)


def sweep_a():
    t = []
    for N in N_GRID:
        for se in COARSE:
            t.append(sim("a", ReviewModel(R=3, sigma_eps=se), N, level="grid"))
        for lev in LEVELS:
            t.append(sim("a", calibrated(ReviewModel(R=3), lev), N, level=lev))
    return t


def sweep_b():
    t = []
    for N in (2000, 20_000):
        for su in (0.0, 0.5):
            for lev in LEVELS:
                se = calibrated(ReviewModel(R=3, sigma_u=su), lev).sigma_eps
                for R in R_GRID:
                    t.append(sim("b", ReviewModel(R=R, sigma_eps=se, sigma_u=su), N, level=lev))
    return t


def sweep_c():
    return [sim("c", ReviewModel(R=3, sigma_eps=se), N, level="grid") for N in (1000, 10_000, 100_000) for se in FINE]


def sweep_d():
    t = []
    for noise in ("gaussian", "t3"):
        for qd in ("gaussian", "beta", "exp", "t3", "lognormal"):
            for lev in LEVELS:
                m = calibrated(ReviewModel(R=3, quality=qd, noise=noise), lev)
                t += [sim("d", m, N, level=lev) for N in N_GRID]
    return t


def sweep_e():
    from run_calibration import placement_variants

    t = []
    for scale in ("continuous", "int10", "six", "iclr6", "five"):
        for lev in LEVELS:
            m = calibrated(ReviewModel(R=4, scale=scale), lev)
            t += [sim("e", m, N, level=lev, placement="standard") for N in N_GRID]
    for m in placement_variants():
        m = calibrated(m, "central")
        label = "native" if m.scale == "custom" else "shifted"
        t += [sim("e", m, N, level="central", placement=label) for N in N_GRID]
    return t


def sweep_f():
    t = [sim("f", calibrated(ReviewModel(R=3), lev), 10_000, reps=10_000, level=lev) for lev in LEVELS]
    t += [sim("f", ReviewModel(R=3, sigma_eps=se), 10_000, reps=10_000, level="grid") for se in COARSE]
    return t


def sweep_g():
    # The headline sweep: a larger budget (1e9 paper draws, at least 2,000 conferences)
    # so the fixed-K curves have no visible Monte Carlo kinks at large N.
    reps = lambda N: int(np.clip(1e9 // N, 2000, 10_000))
    return [sim("g", calibrated(ReviewModel(R=3), lev), N, reps=reps(N), level=lev) for lev in LEVELS for N in N_GRID]


def sweep_h():
    t = []
    for N in N_GRID:
        for lev in LEVELS:
            m = calibrated(ReviewModel(R=3), lev)
            t.append(dict(sweep="h", kind="best", model=md(m), N=N, reps=10_000, best_K=[1, 5, 10, 30],
                          extra=dict(level=lev)))
        for se in COARSE:
            t.append(dict(sweep="h", kind="best", model=md(ReviewModel(R=3, sigma_eps=se)), N=N, reps=4000,
                          best_K=[1, 5, 10, 30], extra=dict(level="grid")))
    return t


SWEEPS = dict(a=sweep_a, b=sweep_b, c=sweep_c, d=sweep_d, e=sweep_e, f=sweep_f, g=sweep_g, h=sweep_h)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("sweeps", nargs="+", choices=sorted(SWEEPS))
    ap.add_argument("--workers", type=int, default=5)
    args = ap.parse_args()
    for s in args.sweeps:
        run_tasks(SWEEPS[s](), os.path.join(ROOT, "results", f"sweep_{s}.csv"), workers=args.workers)


if __name__ == "__main__":
    main()
