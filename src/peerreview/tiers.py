"""The tiers, and how large each is as a conference grows.

THE TIERS ARE SEPARATE, like gold, silver and bronze (docs/terminology.md). Every paper gets
exactly one; no tier contains another:

    best    Best Papers  gold    the first three papers of the award ordering
    oral    Oral         silver  an Oral that is not one of the Best Papers
    spot    Spotlight    bronze  a Spotlight, nothing higher
    accept  Accepted             accepted with no award
    reject  Rejected

A tier together with every tier above it is an "or Better" set, and its key says so:
oral_or_better (Oral or Better), spot_or_better (Spotlight or Better) and accept_or_better
(Accepted or Better, every accepted paper). A bare key is always the separate tier.

The model sizes the "or Better" sets (CUTS) and reads each separate tier off as the gap between
two consecutive cuts (GAPS). NeurIPS presents its Best Papers as Orals, so its fitted Oral count is
the size of Oral or Better; its Spotlight count counts Spotlights only.

Tier sizes: the Best Papers are a constant number, three. Acceptance is a fixed proportion. The
Oral and Spotlight counts grew more slowly than submissions at NeurIPS (Fig. 1b of the paper), so we
fit each count to a power law in N, count = a N^gamma, by least squares in log-log over the
venue-years with a positive count, and use the fitted size at every N of the grid.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

ACCEPT_SHARE = 0.25  # the grid's acceptance rate (results/best_paper.csv, source == "grid")

TIERS = ("best", "oral", "spot", "accept", "reject")  # separate, gold to last
TIER_LABEL = {"best": "Best Papers", "oral": "Oral", "spot": "Spotlight", "accept": "Accepted", "reject": "Rejected"}
OR_BETTER = ("oral_or_better", "spot_or_better", "accept_or_better")  # a tier and every tier above it
OR_BETTER_LABEL = {"oral_or_better": "Oral or Better", "spot_or_better": "Spotlight or Better",
                   "accept_or_better": "Accepted or Better"}
LABEL = {**TIER_LABEL, **OR_BETTER_LABEL}
CUTS = ("best", "oral_or_better", "spot_or_better", "accept_or_better")  # the cutoffs on the ranking, top first
GAPS = {"best": (None, "best"), "oral": ("best", "oral_or_better"), "spot": ("oral_or_better", "spot_or_better"),
        "accept": ("spot_or_better", "accept_or_better"), "reject": ("accept_or_better", None)}  # tier: (cut above, cut below)

# fitted count series -> column of scripts.make_figures.venue_counts(). accept_or_better is N_used * acc_rate_used,
# every accepted paper; oral_or_better is NeurIPS's Oral count, which includes its Best Papers; spot counts
# Spotlights only; best counts Best Papers.
SERIES_COLUMNS = {"accept_or_better": "accepted", "spot": "spotlights", "oral_or_better": "orals_used", "best": "awards_used",
                  "oral": "orals_alone"}  # the Oral tier alone: orals_used - awards_used, years with both counts


def cuts(n_best: int, n_oral_or_better: int | None = None, n_spot: int | None = None, n_accepted: int | None = None) -> dict:
    """The cutoffs on the award ordering from a venue's counts: the Best Papers, then the size of each "or Better"
    set. `n_oral_or_better` is the Oral count including the Best Papers (NeurIPS presents its Best Papers as Orals),
    `n_spot` the Spotlight count, `n_accepted` every accepted paper (Accepted or Better). A missing count (None or NaN) drops its cut, and with it the separate tiers next to it."""
    ok = lambda x: x is not None and x == x  # noqa: E731  (NaN != NaN)
    out = {"best": int(n_best)}
    if ok(n_oral_or_better):
        out["oral_or_better"] = int(n_oral_or_better)
        if ok(n_spot):
            out["spot_or_better"] = int(n_oral_or_better) + int(n_spot)
    if ok(n_accepted):
        out["accept_or_better"] = int(n_accepted)
    return out


def spotlight_counts(root: str) -> pd.DataFrame:
    """Main-track Spotlight counts per venue-year from data/spotlights.csv (columns venue, year, spotlights). A venue-year
    with no Spotlight tier (tier == "no spotlight tier") has 0 Spotlights, so its Accepted tier runs from Oral or Better
    to Accepted or Better; the count is NaN only where it is unknown."""
    import os
    sp = pd.read_csv(os.path.join(root, "data", "spotlights.csv"))
    sp.loc[sp.tier == "no spotlight tier", "spotlights"] = 0
    return sp[["venue", "year", "spotlights"]]


def bands(c: dict, N: int) -> dict[str, tuple[int, int]]:
    """Each separate tier as a range of 0-based ranks [lo, hi) from the cutoffs `c` (keys of CUTS): only the tiers
    whose cuts above and below are both known."""
    out = {}
    for tier, (above, below) in GAPS.items():
        if (above is None or above in c) and (below is None or below in c):
            out[tier] = (0 if above is None else int(c[above]), int(N) if below is None else int(c[below]))
    return out


def add_separate(row, prefix: str):
    """Add the separate tiers' columns {prefix}_{oral, spot, accept, reject} to `row` (a dict or a DataFrame) from
    {prefix}_best and the "or Better" columns, as differences of probabilities for the same papers. Each _se is the
    upper bound sqrt(se_hi^2 + se_lo^2): one "or Better" set contains the other, so the two indicators correlate positively."""
    def get(k):
        return row[k] if k in row else None
    for tier, (above, below) in GAPS.items():
        if tier == "best" or below is None and get(f"{prefix}_{above}") is None:
            continue
        hi = 1.0 if below is None else get(f"{prefix}_{below}")
        lo = get(f"{prefix}_{above}")
        if hi is None or lo is None:
            continue
        row[f"{prefix}_{tier}"] = hi - lo
        se_hi = 0.0 if below is None else get(f"{prefix}_{below}_se")
        se_lo = get(f"{prefix}_{above}_se")
        if se_hi is not None and se_lo is not None:
            row[f"{prefix}_{tier}_se"] = (se_hi ** 2 + se_lo ** 2) ** 0.5
    return row


def fit_tier_sizes(counts: pd.DataFrame, venue: str = "NeurIPS") -> pd.DataFrame:
    """One row per count series (SERIES_COLUMNS: accept_or_better, spot, oral_or_better, best, oral): count = a * N^gamma fitted
    on `venue`'s years with a positive count.

    gamma = 1 is a fixed proportion of submissions, gamma = 0 a constant number. `counts` has
    columns venue, year, N_used, acc_rate_used, orals_used, spotlights, awards_used. The N grid
    (scripts/make_tier_scaling.py) uses the fitted Oral or Better and Spotlight counts and ACCEPT_SHARE * N
    for Accepted or Better, whose fitted exponent is close to 1.
    """
    v = counts[counts.venue == venue].assign(accepted=lambda d: d.N_used * d.acc_rate_used, orals_alone=lambda d: d.orals_used - d.awards_used)
    rows = []
    for series, col in SERIES_COLUMNS.items():
        d = v[v[col].notna() & (v[col] > 0)]
        x, y = np.log10(d.N_used.to_numpy(float)), np.log10(d[col].to_numpy(float))
        gamma, log_a = np.polyfit(x, y, 1)
        resid = y - (log_a + gamma * x)
        rows.append(dict(series=series, a=10 ** log_a, gamma=gamma, n_years=len(d), year_min=int(d.year.min()),
                         year_max=int(d.year.max()), rmse_log10=float(np.sqrt(np.mean(resid**2))),
                         note=f"log-log least squares on {venue} {int(d.year.min())}-{int(d.year.max())}"))
    return pd.DataFrame(rows).astype({"year_min": "Int64", "year_max": "Int64"})


def fitted_count(fits: pd.DataFrame, series: str, N: float) -> int:
    """Fitted number of papers in the count series `series` (a key of SERIES_COLUMNS) at N submissions, at least 1."""
    r = fits[fits.series == series].iloc[0]
    return max(1, int(round(r.a * float(N) ** r.gamma)))
