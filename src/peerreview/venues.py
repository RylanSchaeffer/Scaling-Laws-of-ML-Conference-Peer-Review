"""Venue-year facts of handoff §10.4: data/venues.csv.

One row per (venue, year, denominator). `denominator` is "submissions", except for ICLR
2026, which has a "valid" row (N = 19,525) and a "decided" row (N = 13,763).
N, acc_rate (a fraction), orals and awards hold the handoff values, even where the
2026-10-02 check found a different primary value; check_value then holds that value.
`accepted` holds a count where a source gives one that agrees with N x acc_rate to
rounding; otherwise it is blank, and the accepted count is round(acc_rate * N).
`status` is the handoff key (V/P/S/U). check_outcome is the worst outcome over the
row's handoff claims. docs/claims.md lists the contradictions.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

VENUES_CSV = Path(__file__).resolve().parents[2] / "data" / "venues.csv"

_INT_COLS = ("accepted", "orals", "awards")


def load_venues(path: str | Path = VENUES_CSV) -> pd.DataFrame:
    """Return data/venues.csv as a DataFrame; blank counts are <NA> (nullable Int64)."""
    df = pd.read_csv(path, keep_default_na=False, na_values=[""])
    for c in _INT_COLS:
        df[c] = df[c].astype("Int64")
    text = df.select_dtypes(exclude="number").columns
    df[text] = df[text].fillna("")
    return df
