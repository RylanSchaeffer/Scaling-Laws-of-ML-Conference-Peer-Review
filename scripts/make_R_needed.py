"""How many reviews per paper keep the top-10 as accurate as conferences grow?

Target: the central model's top-10 precision at N = 1,000 with R = 3. For each N, find
the reliability rho^2 that gives the same precision (precision_fixed_K is increasing in
rho), then the R that gives that rho^2 with the per-review noise held at its R = 3
calibration, without and with shared noise sigma_u = 0.5. R is infinite once the
target exceeds the shared-noise ceiling sigma_q^2 / (sigma_q^2 + sigma_u^2).

Writes results/analytic_R_needed.csv.
Usage: uv run python scripts/make_R_needed.py
"""

from __future__ import annotations

import os

import numpy as np
import pandas as pd
from scipy import optimize

from peerreview import analytic as an
from peerreview.levels import ROOT, calibrated
from peerreview.model import ReviewModel

K = 10
N_GRID = [1000, 2000, 5000, 10_000, 20_000, 50_000, 100_000, 200_000, 500_000, 1_000_000]


def main() -> None:
    base = calibrated(ReviewModel(R=3), "central")
    target = float(an.precision_fixed_K(1000, K, np.sqrt(base.reliability)))
    rows = []
    for N in N_GRID:
        f = lambda r: float(an.precision_fixed_K(N, K, r)) - target
        rho = optimize.brentq(f, 0.05, 0.9999, xtol=1e-6)
        r2 = rho**2
        for su in (0.0, 0.5):
            m = calibrated(ReviewModel(R=3, sigma_u=su), "central")
            denom = m.sigma_q**2 / r2 - m.sigma_q**2 - su**2
            R = m.sigma_eps**2 / denom if denom > 0 else np.inf
            rows.append(dict(N=N, K=K, target_precision=target, rho2_needed=r2, sigma_u=su,
                             sigma_eps=m.sigma_eps, R_needed=R, rho2_ceiling=an.rho2_limit(m.sigma_q, su)))
        print(rows[-2], rows[-1], flush=True)
    pd.DataFrame(rows).to_csv(os.path.join(ROOT, "results", "analytic_R_needed.csv"), index=False)


if __name__ == "__main__":
    main()
