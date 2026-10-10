"""Where does the Best Paper land under a second review, tier by tier, as conferences grow?
And how much of each tier does a second committee reproduce?

Tier sizes follow NeurIPS's own trends (peerreview.tiers): acceptance is the grid's fixed
proportion, orals and spotlights grow as fitted power laws of N, the top ten and the award are
fixed numbers. At each N of the grid and each reliability level this script computes, in
the rerun framing (two committees' scores correlate at rho^2):

- p2_{best,top10,oral,spot,accept}: the probability that a second committee ranks the first
  committee's Best Paper within its top M, for M = 1, 10, the oral count, the oral plus
  spotlight count, and the accepted count (exact finite-N integrals).
- ovl_{top10,oral,spot,accept}: the share of one committee's tier that the other also puts
  in its tier. Exact for M < 30; for larger M the closed-form fixed-percentile formula
  (precision_pct_finite at rho^2), whose relative error is below 0.01% from M = 30 up.

Writes results/tier_sizes.csv (the fits) and results/tier_scaling.csv (the curves).
Usage: uv run python scripts/make_tier_scaling.py
"""

from __future__ import annotations

import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(__file__))
from make_figures import venue_counts  # noqa: E402

from peerreview import analytic as an  # noqa: E402
from peerreview.levels import LEVELS, ROOT  # noqa: E402
from peerreview.tiers import ACCEPT_SHARE, fit_tier_sizes, tier_size  # noqa: E402

N_GRID = [1000, 1500, 2000, 3000, 5000, 7000, 10_000, 15_000, 20_000, 30_000, 50_000, 70_000, 100_000]
EXACT_BELOW = 30  # exact 2-D integral below this set size; closed form above


def overlap(N: int, M: int, rho2: float) -> float:
    if M < EXACT_BELOW:
        return float(an.precision_fixed_K(N, M, rho2))
    return float(an.precision_pct_finite(N, M / N, rho2))


def main() -> None:
    fits = fit_tier_sizes(venue_counts())
    fits.to_csv(os.path.join(ROOT, "results", "tier_sizes.csv"), index=False)
    print(fits.to_string(index=False))
    rows = []
    for level, rho2 in LEVELS.items():
        for N in N_GRID:
            M_oral = tier_size(fits, "orals", N)
            M_spot = M_oral + tier_size(fits, "spotlights", N)
            A = int(round(ACCEPT_SHARE * N))  # the grid's fixed proportion; the fitted exponent is 1.05
            rows.append(dict(
                level=level, rho2=rho2, N=N, M_oral=M_oral, M_spot=M_spot, A=A,
                p2_best=an.containment_fixed_K(N, 1, 1, rho2),
                p2_top10=an.containment_fixed_K(N, 1, 10, rho2),
                p2_oral=an.containment_fixed_K(N, 1, M_oral, rho2),
                p2_spot=an.containment_fixed_K(N, 1, M_spot, rho2),
                p2_accept=an.containment_fixed_K(N, 1, A, rho2),
                ovl_top10=overlap(N, 10, rho2),
                ovl_oral=overlap(N, M_oral, rho2),
                ovl_spot=overlap(N, M_spot, rho2),
                ovl_accept=overlap(N, A, rho2),
            ))
            print(level, N, flush=True)
    df = pd.DataFrame(rows)
    df.to_csv(os.path.join(ROOT, "results", "tier_scaling.csv"), index=False)
    print(df[df.level == "central"].round(4).to_string(index=False))


if __name__ == "__main__":
    main()
