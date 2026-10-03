"""What did the Best Paper deserve? The true rank of the top-scored paper, in tiers.

The model's Best Paper is the paper with the highest mean score. For each real venue-year
(submissions, acceptance rate, main-track oral count from data/venues.csv) and for a grid
of N at 25% acceptance, compute exactly, at the three reliability levels, the probability
that it is truly in the top M papers, for M = 1 (the best), 10, the oral count, 10% of
submissions and the accepted count. One minus the last is the probability that it should
have been rejected. Also: the probability that a second, independent committee would reject
it (rejected_given_top with K = 1).

Writes results/best_paper.csv.
Usage: uv run python scripts/make_best_paper.py
"""

from __future__ import annotations

import os

import numpy as np
import pandas as pd

from peerreview import analytic as an
from peerreview.levels import LEVELS, ROOT

N_GRID = [1000, 2000, 5000, 10_000, 20_000, 50_000, 100_000, 200_000, 500_000, 1_000_000]


def tiers(N: int, alpha: float, orals: float | None, rho2: float) -> dict:
    r = float(np.sqrt(rho2))
    A = int(round(alpha * N))
    out = {
        "accepted": A,
        "p_best": an.containment_fixed_K(N, 1, 1, r),
        "p_top10": an.containment_fixed_K(N, 1, 10, r),
        "p_top10pct": an.containment_fixed_K(N, 1, int(round(0.10 * N)), r),
        "p_accept": an.containment_fixed_K(N, 1, A, r),
        "p_rejected_by_committee2": an.rejected_given_top(N, 1, alpha, r),
    }
    out["p_oral"] = an.containment_fixed_K(N, 1, int(orals), r) if orals == orals and orals else np.nan
    out["p_reject"] = 1.0 - out["p_accept"]
    return out


def main() -> None:
    v = pd.read_csv(os.path.join(ROOT, "data", "venues.csv"))
    v = v[v.denominator != "decided"]
    rows = []
    for _, x in v.iterrows():
        for level, rho2 in LEVELS.items():
            rows.append({"source": "venue", "venue": x.venue, "year": int(x.year), "N": int(x.N_used),
                         "alpha": float(x.acc_rate_used), "orals": x.orals_used, "level": level, "rho2": rho2,
                         **tiers(int(x.N_used), float(x.acc_rate_used), x.orals_used, rho2)})
    for N in N_GRID:
        for level, rho2 in LEVELS.items():
            rows.append({"source": "grid", "venue": "", "year": np.nan, "N": N, "alpha": 0.25, "orals": np.nan,
                         "level": level, "rho2": rho2, **tiers(N, 0.25, None, rho2)})
    out = pd.DataFrame(rows)
    out["year"] = out["year"].astype("Int64")
    path = os.path.join(ROOT, "results", "best_paper.csv")
    out.to_csv(path, index=False)
    print(f"wrote {path}: {len(out)} rows")


if __name__ == "__main__":
    main()
