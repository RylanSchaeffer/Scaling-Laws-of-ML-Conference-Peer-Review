"""Where a second review would place the Best Papers, simulated on the main review form
(peerreview.model.MAIN_FORM: integer 1-10 scores, four reviews per paper), at the three reliability levels.

For every venue-year in data/venues.csv (with its submissions, acceptance rate, oral and
spotlight counts) and for a grid of submissions N with the fitted tier sizes (results/tier_sizes.csv)
and acceptance at 25%, each replay draws one conference, reviews it twice, and records the tier the
second review gives each of the first review's three Best Papers, the first three papers of its award ordering
(p2_{best,oral,spot,accept,reject} for the separate tiers and p2_*_or_better for the "or Better" sets, averaged over
the three), the overlap of the two reviews' tiers (overlap_*; overlap_best equals p2_best),
and the second review's score for those papers against its own third-best score (z2_*).

Writes results/best_paper.csv.
Usage: uv run python scripts/run_best_paper.py [--workers 2] [--reps 10000]
       uv run python scripts/run_best_paper.py --cited [--reps 50000]   # re-simulate only the cited NeurIPS
       years (2014, 2021, 2026) at every level with more replays and write them back into the table
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
from peerreview.tiers import CUTS, add_separate, cuts, tier_size

N_GRID = [int(round(x)) for x in np.geomspace(1e3, 1e5, 13)]
CITED_YEARS = (2014, 2021, 2026)  # the NeurIPS years the paper quotes (--cited)
GRID_ALPHA = 0.25
N_BEST = 3  # the Best Papers: the first three papers of the award ordering, at every size
SCALE, R = MAIN_FORM["scale"], MAIN_FORM["R"]


def job(spec: dict) -> dict:
    scale, R, level = spec["scale"], spec["R"], spec["level"]
    m = calibrated(main_model(R=R, scale=scale), level)
    N, A = spec["N"], int(round(spec["alpha"] * spec["N"]))
    if not np.isfinite(m.sigma_eps):  # the level is unreachable on this form (coarse scale: ties floor the disagreement)
        return {**spec, "rho2": LEVELS[level], "sigma_eps": np.nan, "accepted": A, "wall_s": 0.0}
    tiers = cuts(N_BEST, spec["orals"], spec["spotlights"], A)  # the cutoffs; a venue-year with no Spotlight count has no Spotlight tier
    overlap = {**tiers, "top0p3pct": max(1, int(round(0.003 * N)))}  # a fixed proportion as large as the Best Papers at 1,000
    seed = stable_seed(m.as_dict(), N, spec["reps"], "best_paper_forms", spec["source"], level)
    t0 = time.perf_counter()
    r = simulate_best_paper(m, N, spec["reps"], best_K=(1,), seed=seed, winner_tiers=tiers,
                            second_committee=True, overlap_tiers=overlap, n_best=N_BEST)
    out = {**spec, "rho2": LEVELS[level], "sigma_eps": m.sigma_eps, "accepted": A, "seed": seed}
    for name in CUTS:  # "or Better" probabilities and overlaps; the Best Papers are their own
        out[f"p2_{name}"] = r.get(f"winner_in2_{name}", np.nan)
        out[f"p2_{name}_se"] = r.get(f"winner_in2_{name}_se", np.nan)
        out[f"p_{name}"] = r.get(f"winner_in_{name}", np.nan)
        out[f"overlap_{name}"] = r.get(f"overlap_{name}", np.nan)
        out[f"overlap_{name}_se"] = r.get(f"overlap_{name}_se", np.nan)
    for tier in ("oral", "spot", "accept"):  # separate tiers' overlaps, counted directly
        out[f"overlap_{tier}"] = r.get(f"overlap_{tier}", np.nan)
        out[f"overlap_{tier}_se"] = r.get(f"overlap_{tier}_se", np.nan)
    add_separate(out, "p2")  # p2_oral, p2_spot, p2_accept, p2_reject: the separate tiers
    add_separate(out, "p")
    out["overlap_top0p3pct"] = r["overlap_top0p3pct"]
    out["overlap_top0p3pct_se"] = r["overlap_top0p3pct_se"]
    for k in ("winner_rank2_median", "winner_rank2_q10", "winner_rank2_q90", "winner_rank_median",
              "z2_winner", "z2_winner_sd", "z2_winner_se", "z2_cut", "z2_cut_sd", "z2_cut_se"):
        out[k] = r[k]
    out["wall_s"] = time.perf_counter() - t0
    return out


def specs(reps: int) -> list[dict]:
    v = pd.read_csv(os.path.join(ROOT, "data", "venues.csv"))
    v = v[v.denominator != "decided"]
    sp = pd.read_csv(os.path.join(ROOT, "data", "spotlights.csv"))[["venue", "year", "spotlights"]]
    v = v.merge(sp, on=["venue", "year"], how="left")
    fits = pd.read_csv(os.path.join(ROOT, "results", "tier_sizes.csv"))
    out = []
    for _, x in v.iterrows():
        for level in LEVELS:
            out.append({"source": "venue", "venue": x.venue, "year": int(x.year), "N": int(x.N_used),
                        "alpha": float(x.acc_rate_used), "orals": x.orals_used, "spotlights": x.spotlights,
                        "scale": SCALE, "R": R, "level": level, "reps": reps})
    for N in N_GRID:
        for level in LEVELS:
            o = tier_size(fits, "oral_or_better", N)
            out.append({"source": "grid", "venue": "", "year": np.nan, "N": N, "alpha": GRID_ALPHA,
                        "orals": o, "spotlights": tier_size(fits, "spot", N),
                        "scale": SCALE, "R": R, "level": level, "reps": reps if N <= 10_000 else max(2000, reps // 2)})
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=2)
    ap.add_argument("--reps", type=int, default=10_000)
    ap.add_argument("--cited", action="store_true", help="only NeurIPS 2014, 2021 and 2026; write the rows back into the table")
    ap.add_argument("--levels", default="", help="comma-separated levels to (re)simulate; the rows are written back into the table")
    args = ap.parse_args()
    sp = sorted(specs(args.reps), key=lambda s: -s["N"] * s["R"] * s["reps"])  # longest first
    levels = tuple(x for x in args.levels.split(",") if x)
    if args.cited:
        sp = [s for s in sp if s["source"] == "venue" and s["venue"] == "NeurIPS" and s["year"] in CITED_YEARS]
    if levels:
        sp = [s for s in sp if s["level"] in levels]
    rows = []
    t0 = time.perf_counter()
    with ProcessPoolExecutor(max_workers=args.workers) as ex:
        futs = [ex.submit(job, s) for s in sp]
        for i, f in enumerate(as_completed(futs), 1):
            r = f.result()
            rows.append(r)
            print(f"[{i}/{len(sp)} {time.perf_counter() - t0:.0f}s] {r['source']} {r['venue']} {r['year']} N={r['N']} "
                  f"{r['scale']} R={r['R']} {r['level']}: p2_best={r['p2_best']:.4f} "
                  f"p2_accept_or_better={r['p2_accept_or_better']:.3f} ({r['wall_s']:.0f}s)", flush=True)
    out = pd.DataFrame(rows).sort_values(["source", "venue", "year", "N", "level"])
    out["year"] = out["year"].astype("Int64")
    path = os.path.join(ROOT, "results", "best_paper.csv")
    if args.cited or levels:  # replace the simulated rows in the existing table; every column of those rows comes from this run
        old = pd.read_csv(path)
        done = {(r.source, str(r.venue) if r.source == "venue" else "", int(r.N), r.level) for r in out.itertuples()}
        keep = ~pd.Series([(r.source, str(r.venue) if r.source == "venue" else "", int(r.N), r.level) in done for r in old.itertuples()], index=old.index)
        out["reps_best"], out["seed_best"] = out["reps"], out["seed"]
        out = pd.concat([old[keep], out], ignore_index=True).sort_values(["source", "venue", "year", "N", "level"])
    out.to_csv(path, index=False)
    print(f"wrote {path}: {len(out)} rows in {time.perf_counter() - t0:.0f}s")


if __name__ == "__main__":
    main()
