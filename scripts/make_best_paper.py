"""Continuous-score closed forms (the Gaussian model without a score scale), the former main
table. The main results are now simulated on the real review form by scripts/run_best_paper.py;
this table remains for the power-law explanation and as a check.

What would a second review make of the Best Papers? And what did they truly deserve?

The model's Best Papers are the three papers with the highest mean score (N_BEST). For each real venue-year
(submissions, acceptance rate, main-track oral count from data/venues.csv) and for a grid
of N at 25% acceptance, compute exactly, at the three reliability levels:

- p2_*: the rerun framing the paper reports. A second, independent review covers
  every paper (u and eps redrawn; its scores correlate with the first review's at rho^2).
  p2_{best,oral,spot,accept} is the share of the Best Papers that it ranks in its top M,
  for M = 3 (Best Papers again), the oral count, the oral plus spotlight count and the accepted count; p2_reject is one
  minus the last. In the Gaussian model the
  pair of review scores is bivariate normal with correlation rho^2, so these are the
  true-rank integrals with rho replaced by rho^2.
- p_*: the true-rank framing. The share of the Best Papers truly in the top M, for the same M
  and for 10% of submissions; p_reject is one minus p_accept.

Writes results/best_paper.csv.
Usage: uv run python scripts/make_best_paper.py
"""

from __future__ import annotations

import os

import numpy as np
import pandas as pd

from peerreview import analytic as an
from peerreview.levels import LEVELS, ROOT
from run_best_paper import N_BEST

N_GRID = [1000, 2000, 5000, 10_000, 20_000, 50_000, 100_000, 200_000, 500_000, 1_000_000]


def tiers(N: int, alpha: float, orals: float | None, spotlights: float | None, rho2: float) -> dict:
    r = float(np.sqrt(rho2))
    A = int(round(alpha * N))
    M_oral = int(orals) if orals == orals and orals else None
    # The spotlight tier holds orals plus spotlights (each tier includes the tiers above it).
    M_spot = M_oral + int(spotlights) if M_oral and spotlights == spotlights and spotlights else None
    out = {"accepted": A}
    # Rerun framing: the second review's scores correlate with the first review's at rho^2.
    K = N_BEST
    out["p2_best"] = an.containment_fixed_K(N, K, K, rho2)
    out["p2_oral"] = an.containment_fixed_K(N, K, M_oral, rho2) if M_oral else np.nan
    out["p2_spot"] = an.containment_fixed_K(N, K, M_spot, rho2) if M_spot else np.nan
    out["p2_accept"] = an.containment_fixed_K(N, K, A, rho2)
    out["p2_reject"] = 1.0 - out["p2_accept"]
    # True-rank framing.
    out["p_best"] = an.containment_fixed_K(N, K, K, r)
    out["p_top10pct"] = an.containment_fixed_K(N, K, int(round(0.10 * N)), r)
    out["p_accept"] = an.containment_fixed_K(N, K, A, r)
    out["p_rejected_by_committee2"] = an.rejected_given_top(N, K, alpha, r)
    out["p_oral"] = an.containment_fixed_K(N, K, M_oral, r) if M_oral else np.nan
    out["p_spot"] = an.containment_fixed_K(N, K, M_spot, r) if M_spot else np.nan
    out["p_reject"] = 1.0 - out["p_accept"]
    assert abs(out["p2_reject"] - out["p_rejected_by_committee2"]) < 1e-9
    return out


def main() -> None:
    v = pd.read_csv(os.path.join(ROOT, "data", "venues.csv"))
    v = v[v.denominator != "decided"]
    sp = pd.read_csv(os.path.join(ROOT, "data", "spotlights.csv"))[["venue", "year", "spotlights"]]
    v = v.merge(sp, on=["venue", "year"], how="left")
    rows = []
    for _, x in v.iterrows():
        for level, rho2 in LEVELS.items():
            rows.append({"source": "venue", "venue": x.venue, "year": int(x.year), "N": int(x.N_used),
                         "alpha": float(x.acc_rate_used), "orals": x.orals_used, "spotlights": x.spotlights,
                         "level": level, "rho2": rho2,
                         **tiers(int(x.N_used), float(x.acc_rate_used), x.orals_used, x.spotlights, rho2)})
    for N in N_GRID:
        for level, rho2 in LEVELS.items():
            rows.append({"source": "grid", "venue": "", "year": np.nan, "N": N, "alpha": 0.25, "orals": np.nan,
                         "spotlights": np.nan, "level": level, "rho2": rho2, **tiers(N, 0.25, None, None, rho2)})
    out = pd.DataFrame(rows)
    out["year"] = out["year"].astype("Int64")
    path = os.path.join(ROOT, "results", "best_paper_continuous.csv")
    out.to_csv(path, index=False)
    print(f"wrote {path}: {len(out)} rows")


if __name__ == "__main__":
    main()
