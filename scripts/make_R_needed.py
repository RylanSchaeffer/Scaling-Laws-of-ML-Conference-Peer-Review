"""How many reviews per paper keep the top-10 as accurate as conferences grow?

Two metrics. "overlap" (the paper's rerun framing): the share of one committee's top 10
that a second, independent committee also puts in its top 10, which is the precision
formula at correlation rho^2. "precision" (true-rank framing): the share of the top 10 by
score that are truly among the ten best, at correlation rho.

Target: the central model's value at N = 1,000 with R = 3. For each N, find the reliability
rho^2 that gives the same value (both metrics increase in rho), then the R that gives that
rho^2 with the per-review noise held at its R = 3 calibration, without and with shared
noise sigma_u = 0.5. R is infinite once the target exceeds the shared-noise ceiling
sigma_q^2 / (sigma_q^2 + sigma_u^2).

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
N_GRID = [int(round(x)) for x in np.geomspace(1e3, 1e5, 21)]  # 1K to 100K, smooth curves in Fig 4c


def main() -> None:
    base = calibrated(ReviewModel(R=3), "central")
    rows = []
    for metric in ("overlap", "precision"):
        # The metric is precision_fixed_K at correlation c, where c = rho^2 (overlap) or rho (precision).
        c0 = base.reliability if metric == "overlap" else np.sqrt(base.reliability)
        target = float(an.precision_fixed_K(1000, K, c0))
        for N in N_GRID:
            f = lambda c: float(an.precision_fixed_K(N, K, c)) - target
            c = optimize.brentq(f, 0.05, 0.9999, xtol=1e-6)
            r2 = c if metric == "overlap" else c**2
            for su in (0.0, 0.5):
                m = calibrated(ReviewModel(R=3, sigma_u=su), "central")
                denom = m.sigma_q**2 / r2 - m.sigma_q**2 - su**2
                R = m.sigma_eps**2 / denom if denom > 0 else np.inf
                rows.append(dict(metric=metric, N=N, K=K, target=target, rho2_needed=r2, sigma_u=su,
                                 sigma_eps=m.sigma_eps, R_needed=R, rho2_ceiling=an.rho2_limit(m.sigma_q, su)))
            print(rows[-2], rows[-1], flush=True)
    pd.DataFrame(rows).to_csv(os.path.join(ROOT, "results", "analytic_R_needed.csv"), index=False)


if __name__ == "__main__":
    main()
