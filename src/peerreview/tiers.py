"""How large is each tier as a conference grows? Empirical scaling laws for tier sizes.

The Best Paper's fate under a second review depends on how many papers each tier holds at
size N. Awards and the top ten are fixed numbers. Acceptance is a fixed share. Orals and
spotlights lie in between: at NeurIPS their counts grew more slowly than submissions
(Fig. 1b of the paper), so we fit each count to a power law in N, count = a N^gamma, by
least squares in log-log over the venue-years with a positive count, and use the fitted
size at every N of the grid.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

ACCEPT_SHARE = 0.25  # the grid's acceptance rate (results/best_paper.csv, source == "grid")

# tier -> column of scripts.make_figures.venue_counts(); "accepted" is N_used * acc_rate_used
TIER_COLUMNS = {"accepted": "accepted", "spotlights": "spotlights", "orals": "orals_used", "awards": "awards"}


def fit_tier_sizes(counts: pd.DataFrame, venue: str = "NeurIPS") -> pd.DataFrame:
    """One row per tier: count = a * N^gamma fitted on `venue`'s years with a positive count.

    gamma = 1 is a fixed proportion of submissions, gamma = 0 a fixed number. `counts` has
    columns venue, year, N_used, acc_rate_used, orals_used, spotlights, awards. The N grid
    (scripts/make_tier_scaling.py) uses the fitted oral and spotlight counts and ACCEPT_SHARE * N
    for acceptance, whose fitted exponent is close to 1.
    """
    v = counts[counts.venue == venue].assign(accepted=lambda d: d.N_used * d.acc_rate_used)
    rows = []
    for tier, col in TIER_COLUMNS.items():
        d = v[v[col].notna() & (v[col] > 0)]
        x, y = np.log10(d.N_used.to_numpy(float)), np.log10(d[col].to_numpy(float))
        gamma, log_a = np.polyfit(x, y, 1)
        resid = y - (log_a + gamma * x)
        rows.append(dict(tier=tier, a=10 ** log_a, gamma=gamma, n_years=len(d), year_min=int(d.year.min()),
                         year_max=int(d.year.max()), rmse_log10=float(np.sqrt(np.mean(resid**2))),
                         note=f"log-log least squares on {venue} {int(d.year.min())}-{int(d.year.max())}"))
    return pd.DataFrame(rows).astype({"year_min": "Int64", "year_max": "Int64"})


def tier_size(fits: pd.DataFrame, tier: str, N: float) -> int:
    """Fitted number of papers in `tier` at N submissions, at least 1."""
    r = fits[fits.tier == tier].iloc[0]
    return max(1, int(round(r.a * float(N) ** r.gamma)))
