"""The control for Fig 2a: where a second review places the first review's Best Paper when the target is a
fixed proportion of submissions, the top 1%, rather than a constant number, the top ten.

Main model, central level, on the dense submissions grid of run_R_needed_tiers.py. For each size the
probability that the second review ranks the first review's Best Paper within its top 1% (ten papers at
1,000 submissions, one thousand at 100,000), beside the probability for the top ten as a check against
results/best_paper.csv.

Writes results/top1pct_control.csv.
Usage: uv run python scripts/run_top1pct_control.py [--workers 6] [--reps 5000]
"""
from __future__ import annotations

import argparse
import os
import time
from concurrent.futures import ProcessPoolExecutor, as_completed

import pandas as pd

from peerreview.levels import ROOT, calibrated, main_model
from peerreview.simulate import simulate_best_paper, stable_seed
from run_R_needed_tiers import N_GRID


def job(spec: dict) -> dict:
    m = calibrated(main_model(sigma_u=0.0), "central")
    N, reps = spec["N"], spec["reps"]
    tiers = {"top1pct": max(1, int(round(0.01 * N))), "top10": 10, "accept": int(round(0.25 * N))}
    t0 = time.perf_counter()
    r = simulate_best_paper(m, N, reps, best_K=(1,), seed=stable_seed(m.as_dict(), N, reps, "top1pct_control"),
                            winner_tiers=tiers, second_committee=True)
    return {"N": N, "reps": reps, "top1pct_size": tiers["top1pct"], "p2_top1pct": float(r["winner_in2_top1pct"]),
            "p2_top1pct_se": float(r["winner_in2_top1pct_se"]), "p2_top10": float(r["winner_in2_top10"]),
            "p2_top10_se": float(r["winner_in2_top10_se"]), "level": "central", "wall_s": time.perf_counter() - t0}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--reps", type=int, default=5000)
    args = ap.parse_args()
    specs = sorted([{"N": N, "reps": args.reps} for N in N_GRID], key=lambda s: -s["N"])
    rows, t0 = [], time.perf_counter()
    with ProcessPoolExecutor(max_workers=args.workers) as ex:
        for i, fu in enumerate(as_completed([ex.submit(job, s) for s in specs]), 1):
            r = fu.result()
            rows.append(r)
            print(f"[{i}/{len(specs)} {time.perf_counter() - t0:.0f}s] N={r['N']}: top 1% {r['p2_top1pct']:.4f} top 10 {r['p2_top10']:.4f} ({r['wall_s']:.0f}s)", flush=True)
    df = pd.DataFrame(rows).sort_values("N")
    path = os.path.join(ROOT, "results", "top1pct_control.csv")
    df.to_csv(path, index=False)
    print(f"wrote {path}")


if __name__ == "__main__":
    main()
