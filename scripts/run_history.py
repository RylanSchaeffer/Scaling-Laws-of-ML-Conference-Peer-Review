"""§8.4: the calibrated model at each real venue-year (N, acceptance rate, oral count).

For every row of data/venues.csv (the *_used columns; scripts/build_venues_used.py) and every reliability level: fixed-number precision
at K = 5, 10, 30 and at that year's oral count, the swap fraction and the count of
wrong accepts, and the two-committee disagreement. Gaussian base model (only rho^2
matters there).

Writes results/history.csv.
Usage: uv run python scripts/run_history.py [--workers 5]
"""

from __future__ import annotations

import argparse
import os

import numpy as np
import pandas as pd

from peerreview.levels import LEVELS, ROOT, calibrated
from peerreview.model import ReviewModel
from peerreview.runner import run_tasks


def tasks(venues: pd.DataFrame) -> list[dict]:
    out = []
    for _, v in venues.iterrows():
        N = int(v["N_used"])
        if N < 1000:  # the study's range is N = 1,000 to 1,000,000 (handoff §1)
            continue
        alpha = float(v["acc_rate_used"])
        orals = int(v["orals_used"]) if pd.notna(v.get("orals_used")) else None
        Ks = sorted({5, 10, 30} | ({orals} if orals else set()))
        for lev in LEVELS:
            m = calibrated(ReviewModel(R=3), lev)
            d = m.as_dict()
            d["scale_points"] = ()
            out.append(dict(
                sweep="history", kind="simulate", model=d, N=N, reps=10_000,
                sel=dict(fixed_K=Ks, pct=[], alphas=[alpha], best_K=[1, 5, 10, 30], alpha_ref=alpha),
                two_committees=True,
                extra=dict(venue=v["venue"], year=int(v["year"]), denominator=v.get("denominator", "submissions"),
                           level=lev, alpha=alpha, orals=orals if orals else np.nan),
            ))
    return out


def tidy(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for _, r in df.iterrows():
        a = f"acc{r['alpha']:.2f}"
        A = int(round(r["alpha"] * r["N"]))
        o = r["orals"]
        rows.append(dict(
            venue=r["venue"], year=r["year"], denominator=r["denominator"], level=r["level"], N=r["N"],
            alpha=r["alpha"], accepted=A, orals=o, reps=r["reps"], seed=r["seed"],
            prec_K5=r["prec_K5"], prec_K10=r["prec_K10"], prec_K30=r["prec_K30"],
            prec_orals=r.get(f"prec_K{int(o)}", np.nan) if pd.notna(o) else np.nan,
            ovl_orals=r.get(f"ovl_K{int(o)}", np.nan) if pd.notna(o) else np.nan,
            best_in_K1=r["best_in_K1"], best_in_K10=r["best_in_K10"],
            swap=r[f"swap_{a}"], swap_se=r[f"swap_{a}_se"], wrong_accepts=r[f"swap_{a}"] * A,
            dis=r[f"dis_{a}"], incons=r[f"incons_{a}"], winner_rank_median=r["winner_rank_median"],
        ))
    return pd.DataFrame(rows).sort_values(["venue", "denominator", "year", "level"])


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=5)
    args = ap.parse_args()
    venues = pd.read_csv(os.path.join(ROOT, "data", "venues.csv"))
    raw = run_tasks(tasks(venues), os.path.join(ROOT, "results", "history_raw.csv"), workers=args.workers)
    out = tidy(raw)
    out.to_csv(os.path.join(ROOT, "results", "history.csv"), index=False)
    print(out[out.level == "central"].round(3).to_string(index=False))


if __name__ == "__main__":
    main()
