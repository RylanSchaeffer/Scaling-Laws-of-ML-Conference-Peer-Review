"""Does the number of Best Papers matter? Best Papers again for two, three and four Best Papers.

The paper holds the Best Papers at three, between NeurIPS's median (2.5) and mean (3.5) a year. This
script re-simulates Best Papers again (a second review also ranks a paper among the first review's Best
Papers among its own Best Papers) on the main form at the central level, on the submissions grid of
run_best_paper_hirep.py, for 2, 3 and 4 Best Papers. Each size uses the same seed, so the three tiers
are read off the same conferences, and the fitted power-law exponents can be compared directly.

Writes results/best_paper_size.csv.
Usage: uv run python scripts/run_best_paper_size.py [--workers 2]
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
from run_best_paper_hirep import reps_for

N_GRID = [1000, 2154, 4642, 10_000, 21_544, 46_416, 100_000]
SIZES = (2, 3, 4)


def job(spec: tuple) -> dict:
    N, k = spec
    m = calibrated(main_model(), "central")
    reps = reps_for(N)
    seed = stable_seed(m.as_dict(), N, reps, "best_paper_size")  # one seed per N: every size sees the same conferences
    t0 = time.perf_counter()
    r = simulate_best_paper(m, N, reps, best_K=(1,), seed=seed, winner_tiers={"best": k}, second_committee=True, n_best=k)
    return {"N": N, "n_best": k, "level": "central", "reps": reps, "seed": seed, "p2_best": r["winner_in2_best"],
            "p2_best_se": r["winner_in2_best_se"], "wall_s": time.perf_counter() - t0}


def exponent(d: pd.DataFrame) -> float:
    k, _ = np.polyfit(np.log(d.N.values), np.log(d.p2_best.values), 1)
    return -k


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=2)
    args = ap.parse_args()
    specs = sorted([(N, k) for N in N_GRID for k in SIZES], key=lambda s: -s[0])
    rows, t0 = [], time.perf_counter()
    with ProcessPoolExecutor(max_workers=args.workers) as ex:
        futs = [ex.submit(job, s) for s in specs]
        for i, f in enumerate(as_completed(futs), 1):
            r = f.result()
            rows.append(r)
            print(f"[{i}/{len(specs)} {time.perf_counter() - t0:.0f}s] N={r['N']} Best Papers {r['n_best']}: "
                  f"{r['p2_best']:.5f}+-{r['p2_best_se']:.5f} ({r['wall_s']:.0f}s)", flush=True)
    df = pd.DataFrame(rows).sort_values(["n_best", "N"])
    path = os.path.join(ROOT, "results", "best_paper_size.csv")
    df.to_csv(path, index=False)
    for k, d in df.groupby("n_best"):
        print(f"{k} Best Papers: {100 * d.p2_best.iloc[0]:.2f}% at 1,000, {100 * d.p2_best.iloc[-1]:.3f}% at 100,000; exponent {exponent(d):.2f}")
    print(f"wrote {path}")


if __name__ == "__main__":
    main()
