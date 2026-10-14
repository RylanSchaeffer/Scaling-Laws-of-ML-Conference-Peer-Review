"""More replays for the two smallest tiers on the submissions grid. The grid rows of
results/best_paper.csv come from 10,000 replays (5,000 above 10K submissions), enough for the
overlaps and the large tiers but not for the Best Paper and top-ten probabilities, which fall to
0.1% and 1% at 100K. This script re-simulates those two on the main form with many more replays
(lean: no overlaps) and writes them back into the grid rows, with the replay count in reps_best.

Usage: uv run python scripts/run_best_paper_hirep.py [--workers 2] [--venues]
  --venues does the same for the cited venue-years (NeurIPS 2014, 2021, 2026; ICML and ICLR 2026).
"""
from __future__ import annotations

import argparse
import os
import time
from concurrent.futures import ProcessPoolExecutor, as_completed

import numpy as np
import pandas as pd

from peerreview.levels import ROOT, calibrated, main_model
from peerreview.simulate import simulate_best_paper, stable_seed

PATH = os.path.join(ROOT, "results", "best_paper.csv")


def reps_for(N: int) -> int:
    return 50_000 if N <= 10_000 else 30_000 if N <= 32_000 else 20_000


VENUE_YEARS = (("NeurIPS", 2014), ("NeurIPS", 2021), ("NeurIPS", 2026), ("ICML", 2026), ("ICLR", 2026))  # the cited ones


def job(spec: tuple) -> dict:
    N, level, key = spec
    m = calibrated(main_model(), level)
    reps = reps_for(N)
    seed = stable_seed(m.as_dict(), N, reps, "best_paper_hirep", level, key)
    t0 = time.perf_counter()
    r = simulate_best_paper(m, N, reps, best_K=(1,), seed=seed, winner_tiers={"best": 1, "top10": 10}, second_committee=True)
    return {"N": N, "level": level, "key": key, "p2_best": r["winner_in2_best"], "p2_best_se": r["winner_in2_best_se"],
            "p2_top10": r["winner_in2_top10"], "p2_top10_se": r["winner_in2_top10_se"],
            "overlap_best": r["winner_in2_best"], "overlap_best_se": r["winner_in2_best_se"],
            "winner_rank2_median": r["winner_rank2_median"], "reps_best": reps, "seed_best": seed,
            "wall_s": time.perf_counter() - t0}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=2)
    ap.add_argument("--venues", action="store_true", help="the cited venue-years (VENUE_YEARS) instead of the grid")
    ap.add_argument("--levels", default="", help="comma-separated levels to re-simulate (default: all)")
    args = ap.parse_args()
    b = pd.read_csv(PATH)
    if args.venues:
        cited = pd.Series([(v, int(y)) in VENUE_YEARS if y == y else False for v, y in zip(b.venue, b.year)], index=b.index)
        rows = b[(b.source == "venue") & cited]
        specs = sorted({(int(r.N), r.level, f"{r.venue}{int(r.year)}") for r in rows.itertuples()}, key=lambda s: -s[0])
    else:
        grid = b[b.source == "grid"]
        specs = sorted({(int(N), lev, "grid") for N, lev in zip(grid.N, grid.level)}, key=lambda s: -s[0])
    if args.levels:
        specs = [s for s in specs if s[1] in args.levels.split(",")]
    t0 = time.perf_counter()
    with ProcessPoolExecutor(max_workers=args.workers) as ex:
        futs = [ex.submit(job, s) for s in specs]
        for i, f in enumerate(as_completed(futs), 1):
            r = f.result()
            mask = (b.source == ("grid" if r["key"] == "grid" else "venue")) & (b.N == r["N"]) & (b.level == r["level"])
            if r["key"] != "grid":
                mask &= (b.venue + b.year.astype("Int64").astype(str)) == r["key"]
            assert mask.sum() == 1
            for k, v in r.items():
                if k not in ("N", "level", "key", "wall_s"):
                    b.loc[mask, k] = v
            print(f"[{i}/{len(specs)} {time.perf_counter() - t0:.0f}s] N={r['N']} {r['level']}: p2_best={r['p2_best']:.5f}"
                  f"+-{r['p2_best_se']:.5f} p2_top10={r['p2_top10']:.4f} ({r['reps_best']} reps, {r['wall_s']:.0f}s)", flush=True)
            b.to_csv(PATH, index=False)  # checkpoint after every job
    print(f"updated {PATH}")


if __name__ == "__main__":
    main()
