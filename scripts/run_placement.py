"""Where a second review places a paper that the first review put in a separate tier (Best Papers, Oral, Spotlight,
Accepted) or an "or Better" set, against submissions N, on the main review form (peerreview.model.MAIN_FORM) at
the three reliability levels. Companion to results/best_paper.csv, whose grid rows give the same
for the Best Papers (p2_*) with more replays.

For each N on the submissions grid (tier sizes from results/tier_sizes.csv, acceptance 25%) each
replay draws one conference, reviews it twice, and records, for every paper the first review put
in a tier, the tier the second review gives it: place_{first}_in_{second}, the proportion of the
first review's tier `first` (best, oral, spot, accept, or an "or Better" set such as accept_or_better)
that the second review puts in tier `second` (best, oral, spot, accept, reject). The tiers are separate (peerreview.tiers), so each first tier's
five placements sum to 1 and place_X_in_X is the tier's overlap, overlap_X. The "or Better" overlaps
are overlap_*_or_better.

Writes results/placement.csv.
Usage: uv run python scripts/run_placement.py [--workers 2] [--reps 4000]
"""
from __future__ import annotations

import argparse
import os
import time
from concurrent.futures import ProcessPoolExecutor, as_completed

import numpy as np
import pandas as pd

from peerreview.levels import LEVELS, ROOT, calibrated, main_model
from peerreview.model import MAIN_FORM
from peerreview.simulate import simulate_best_paper, stable_seed
from peerreview.tiers import cuts, fitted_count
from run_best_paper import N_BEST

N_GRID = [int(round(x)) for x in np.geomspace(1e3, 1e5, 13)]
GRID_ALPHA = 0.25


REPS_CENTRAL = 20_000  # the central level draws Fig. 1e-g: enough replays for smooth curves at every size


def job(spec: dict) -> dict:
    m = calibrated(main_model(), spec["level"])
    N, A = spec["N"], int(round(GRID_ALPHA * spec["N"]))
    cut_sizes = cuts(N_BEST, int(spec["n_oral_or_better"]), int(spec["spotlights"]), A)
    seed = stable_seed(m.as_dict(), N, spec["reps"], "placement", spec["level"])
    t0 = time.perf_counter()
    r = simulate_best_paper(m, N, spec["reps"], best_K=(1,), seed=seed, second_committee=True, overlap_cuts=cut_sizes,
                            place=True, n_best=N_BEST)
    out = {**spec, "alpha": GRID_ALPHA, "accepted": A, "rho2": LEVELS[spec["level"]], "sigma_eps": m.sigma_eps, "seed": seed}
    for k, v in r.items():
        if k.startswith("place_") or k.startswith("overlap_"):
            out[k] = v
    out["wall_s"] = time.perf_counter() - t0
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=2)
    ap.add_argument("--reps", type=int, default=4000)
    ap.add_argument("--levels", default="", help="comma-separated levels to (re)simulate; merged into the existing table")
    args = ap.parse_args()
    levels = tuple(x for x in args.levels.split(",") if x) or tuple(LEVELS)
    fits = pd.read_csv(os.path.join(ROOT, "results", "tier_sizes.csv"))
    specs = [{"N": N, "level": lev, "n_oral_or_better": fitted_count(fits, "oral_or_better", N), "spotlights": fitted_count(fits, "spot", N),
              "reps": REPS_CENTRAL if lev == "central" else args.reps if N <= 10_000 else max(1000, args.reps // 2), "scale": MAIN_FORM["scale"], "R": MAIN_FORM["R"]}
             for N in N_GRID for lev in levels]
    specs.sort(key=lambda s: -s["N"])
    rows, t0 = [], time.perf_counter()
    with ProcessPoolExecutor(max_workers=args.workers) as ex:
        futs = [ex.submit(job, s) for s in specs]
        for i, f in enumerate(as_completed(futs), 1):
            r = f.result(); rows.append(r)
            print(f"[{i}/{len(specs)} {time.perf_counter() - t0:.0f}s] N={r['N']} {r['level']}: Oral->Oral {r['place_oral_in_oral']:.3f} "
                  f"Spotlight->Spotlight {r['place_spot_in_spot']:.3f} Accepted->Rejected {r['place_accept_in_reject']:.3f} ({r['wall_s']:.0f}s)", flush=True)
    out = pd.DataFrame(rows)
    path = os.path.join(ROOT, "results", "placement.csv")
    if args.levels and os.path.exists(path):
        old = pd.read_csv(path)
        out = pd.concat([old[~old.level.isin(levels)], out], ignore_index=True)
    out = out.sort_values(["N", "level"])
    out.to_csv(path, index=False)
    print(f"wrote {path}: {len(out)} rows in {time.perf_counter() - t0:.0f}s")


if __name__ == "__main__":
    main()
