"""Where do the Best Papers land under a second review, tier by tier, as conferences grow?
And how much of each tier and each "or Better" set does a second review reproduce?

Tier sizes follow NeurIPS's own trends (peerreview.tiers): Accepted or Better is the grid's fixed
proportion, the Oral or Better and Spotlight counts grow as fitted power laws of N, and the Best Papers
are a constant number, the first three papers of the award ordering. The tiers are separate. At each N of the grid and each
reliability level this script computes, for continuous scores without the chairs' call, in the
rerun framing (a paper's two scores correlate at rho^2):

- p2_best and p2_{oral,spot,accept}_or_better: the probability that a second review ranks a paper
  among the first review's Best Papers within its top M, for M = 3 and the sizes of Oral or Better,
  Spotlight or Better and Accepted or Better (exact finite-N integrals); p2_best is also the Best
  Papers' overlap. p2_{oral,spot,accept,reject}: the separate tiers, their differences.
- ovl_{oral,spot,accept}_or_better: the proportion of one review's "or Better" set that the other also
  puts in that set. Exact for M < 30; for larger M the closed-form fixed-percentile formula
  (precision_pct_finite at rho^2), whose relative error is below 0.01% from M = 30 up.

Writes results/tier_sizes.csv (the fits) and results/tier_scaling.csv (the curves).
Usage: uv run python scripts/make_tier_scaling.py
"""

from __future__ import annotations

import os
import sys

import pandas as pd

sys.path.insert(0, os.path.dirname(__file__))
from make_figures import venue_counts  # noqa: E402

from peerreview import analytic as an  # noqa: E402
from peerreview.levels import LEVELS, ROOT  # noqa: E402
from peerreview.tiers import ACCEPT_SHARE, add_separate, fit_tier_sizes, fitted_count  # noqa: E402
from run_best_paper import N_BEST  # noqa: E402

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
            M_oral_or_better = fitted_count(fits, "oral_or_better", N)  # the size of Oral or Better
            M_spot_or_better = M_oral_or_better + fitted_count(fits, "spot", N)  # the size of Spotlight or Better
            A = int(round(ACCEPT_SHARE * N))  # the grid's fixed proportion; the fitted exponent is 1.05
            rows.append(add_separate(dict(
                level=level, rho2=rho2, N=N, M_oral_or_better=M_oral_or_better, M_spot_or_better=M_spot_or_better, A=A,
                p2_best=an.containment_fixed_K(N, N_BEST, N_BEST, rho2),  # = the Best Papers' overlap
                p2_oral_or_better=an.containment_fixed_K(N, N_BEST, M_oral_or_better, rho2),
                p2_spot_or_better=an.containment_fixed_K(N, N_BEST, M_spot_or_better, rho2),
                p2_accept_or_better=an.containment_fixed_K(N, N_BEST, A, rho2),
                ovl_oral_or_better=overlap(N, M_oral_or_better, rho2),
                ovl_spot_or_better=overlap(N, M_spot_or_better, rho2),
                ovl_accept_or_better=overlap(N, A, rho2),
            ), "p2"))
            print(level, N, flush=True)
    df = pd.DataFrame(rows)
    df.to_csv(os.path.join(ROOT, "results", "tier_scaling.csv"), index=False)
    print(df[df.level == "central"].round(4).to_string(index=False))


if __name__ == "__main__":
    main()
