"""Two levers at the top, at 100,000 submissions: more reviews per paper against more independent chair calls.

The award ordering is the score plus the chair noise eta, one draw per paper per review. If k chairs judged
each accepted paper independently and their calls were averaged, the chair noise would shrink to
sigma_eta / sqrt(k); k = inf is the award ordering by score alone. This script simulates the main model
(central level) at 100,000 submissions, and at 1,000 for the reference, with R reviews per paper and k
chair calls, and records the overlap of two reviews' separate tiers (Best Papers, Oral, Spotlight, Accepted) and "or Better" sets.

Writes results/chair_calls.csv.
Usage: uv run python scripts/run_chair_calls.py [--workers 8] [--reps 1000] [--chunk 250]
"""
from __future__ import annotations

import argparse
import os
import time
from concurrent.futures import ProcessPoolExecutor, as_completed

import numpy as np
import pandas as pd

from peerreview.levels import ROOT, calibrated, main_model
from run_R_needed_tiers import GROUPS, job, cuts_at

K_CALLS = [1, 2, 4, 16, np.inf]
RS = [4, 16]
NS = [1000, 100_000]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--reps", type=int, default=1000)
    ap.add_argument("--chunk", type=int, default=250)
    args = ap.parse_args()
    fits = pd.read_csv(os.path.join(ROOT, "results", "tier_sizes.csv"))
    base = calibrated(main_model(sigma_u=0.0), "central")
    specs = []
    for N in NS:
        for k in K_CALLS:
            sigma = 0.0 if not np.isfinite(k) else base.sigma_award / np.sqrt(k)
            for c in range(int(np.ceil(args.reps / args.chunk))):
                specs.append({"N": N, "Rs": RS, "sizes": cuts_at(fits, N), "reps": args.chunk, "chunk": c, "sigma_award": sigma, "k": k})
    specs.sort(key=lambda s: -s["N"])
    rows, t0 = [], time.perf_counter()
    with ProcessPoolExecutor(max_workers=args.workers) as ex:
        futs = {ex.submit(job, s): s for s in specs}
        for i, fu in enumerate(as_completed(futs), 1):
            s = futs[fu]
            for r in fu.result():
                r["k"] = s["k"]
                r["sigma_award"] = s["sigma_award"]
                rows.append(r)
            r = rows[-1]
            print(f"[{i}/{len(specs)} {time.perf_counter() - t0:.0f}s] N={s['N']} k={s['k']} chunk {s['chunk']}: R={r['R']} best {r['overlap_best']:.3f}", flush=True)
    df = pd.DataFrame(rows)
    keys = ["N", "R", "n_oral_or_better", "spotlights", "sigma_eps", "method", "k", "sigma_award"]
    agg = {f"overlap_{t}": "mean" for t in GROUPS}
    agg.update({"reps": "sum", "wall_s": "sum"})
    g = df.groupby(keys, dropna=False)
    out = g.agg(agg).reset_index()
    for t in GROUPS:
        out[f"overlap_{t}_se"] = (g[f"overlap_{t}"].std(ddof=1) / np.sqrt(g[f"overlap_{t}"].size())).values
    out = out.sort_values(["N", "R", "k"])
    path = os.path.join(ROOT, "results", "chair_calls.csv")
    out.to_csv(path, index=False)
    print(f"wrote {path}")
    print(out.pivot_table(index=["N", "R"], columns="k", values="overlap_best").round(4).to_string())


if __name__ == "__main__":
    main()
