"""Does the score scale change the main results? The same model on every real review form
(data/review_forms.csv) and on continuous scores, each recalibrated at the central level.

Part "conference": the NeurIPS 2026 and 2014 conferences (submissions, acceptance rate, oral and
spotlight counts) under each form: where a second review places the first review's three Best Papers
(p2_*, the share of them in each tier; p2_best is the share it keeps among its own Best Papers).
Part "grid": a submissions grid 1K to 100K with the fitted tier sizes and 25% acceptance, for the
main form, the six-point form, the ICLR 2022-2025 form and continuous scores.

Writes results/scale_impact.csv.
Usage: uv run python scripts/run_scale_impact.py [--workers 2] [--grid-only --grid-reps 20000]  (the paper's grid: 20,000 replays per point)
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
from peerreview.tiers import tier_size
from run_best_paper import N_BEST

FORMS = (  # label, R, scale, who uses it
    ("Integer 1--10, 4 reviews", 4, "int10", "main form; NeurIPS 2014--2024, ICML 2023--2024, ICLR 2017--2019 and 2021"),
    ("Integer 1--10, 3 reviews", 3, "int10", "NeurIPS 2014--2019 and ICML before 2024, three reviews"),
    ("Six-point, 4 reviews", 4, "six", "NeurIPS 2025--2026 and ICML 2026"),
    ("Six-point, 3 reviews", 3, "six", "no venue; the six-point scale with three reviews"),
    ("Five-point, 4 reviews", 4, "five", "ICML 2025"),
    ("1/3/5/6/8/10, 4 reviews", 4, "iclr6", "ICLR 2022--2025"),
    ("0/2/4/6/8/10, 4 reviews", 4, "iclr2026", "ICLR 2026"),
    ("1/3/6/8, 3 reviews", 3, "iclr4", "ICLR 2020"),
    ("Continuous, 4 reviews", 4, "continuous", "no scale"),
)
GRID_FORMS = {"int10", "six", "iclr6", "continuous"}  # at R = 4
N_GRID = [1000, 2154, 4642, 10_000, 21_544, 46_416, 100_000]
REPS_CONF = {2026: 40_000, 2014: 100_000}


def job(spec: dict) -> dict:
    m = calibrated(main_model(R=spec["R"], scale=spec["scale"]), spec["level"])
    N, A = spec["N"], int(round(spec["alpha"] * spec["N"]))
    tiers = {"best": N_BEST, "oral": int(spec["orals"]), "spot": int(spec["orals"] + spec["spotlights"]), "accept": A}
    seed = stable_seed(m.as_dict(), N, spec["reps"], "scale_impact", spec["part"])
    t0 = time.perf_counter()
    r = simulate_best_paper(m, N, spec["reps"], best_K=(1,), seed=seed, winner_tiers=tiers,
                            second_committee=True, n_best=N_BEST)  # lean: no overlaps, which the paper does not use
    out = {**spec, "rho2": LEVELS[spec["level"]], "sigma_eps": m.sigma_eps, "accepted": A, "seed": seed}
    for name in ("best", "oral", "spot", "accept"):
        out[f"p2_{name}"] = r[f"winner_in2_{name}"]
        out[f"p2_{name}_se"] = r[f"winner_in2_{name}_se"]
        out[f"p_{name}"] = r[f"winner_in_{name}"]
    out["p2_reject"] = 1.0 - out["p2_accept"]
    out["p2_reject_se"] = out["p2_accept_se"]
    out["winner_rank2_median"] = r["winner_rank2_median"]
    out["wall_s"] = time.perf_counter() - t0
    return out


def specs(grid_reps: int | None = None, grid_only: bool = False) -> list[dict]:
    v = pd.read_csv(os.path.join(ROOT, "data", "venues.csv"))
    sp = pd.read_csv(os.path.join(ROOT, "data", "spotlights.csv"))[["venue", "year", "spotlights"]]
    v = v[(v.venue == "NeurIPS") & (v.denominator != "decided")].merge(sp, on=["venue", "year"])
    fits = pd.read_csv(os.path.join(ROOT, "results", "tier_sizes.csv"))
    out = []
    for year, reps in ({} if grid_only else REPS_CONF).items():
        x = v[v.year == year].iloc[0]
        for label, R, scale, who in FORMS:
            out.append({"part": "conference", "form": label, "used_by": who, "R": R, "scale": scale, "year": year,
                        "N": int(x.N_used), "alpha": float(x.acc_rate_used), "orals": int(x.orals_used),
                        "spotlights": int(x.spotlights), "level": "central", "reps": reps})
    for label, R, scale, who in FORMS:
        if scale not in GRID_FORMS or R != MAIN_FORM["R"]:
            continue
        for N in N_GRID:
            out.append({"part": "grid", "form": label, "used_by": who, "R": R, "scale": scale, "year": np.nan, "N": N,
                        "alpha": 0.25, "orals": tier_size(fits, "orals", N), "spotlights": tier_size(fits, "spotlights", N),
                        "level": "central", "reps": grid_reps or (5000 if N <= 10_000 else 2000)})
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=2)
    ap.add_argument("--grid-reps", type=int, default=None, help="replays per grid point (default 5,000 up to 10K submissions, 2,000 above)")
    ap.add_argument("--grid-only", action="store_true", help="re-simulate only the grid rows and replace them in the existing table")
    args = ap.parse_args()
    sp = sorted(specs(args.grid_reps, args.grid_only), key=lambda s: -s["N"] * s["R"] * s["reps"])
    rows, t0 = [], time.perf_counter()
    with ProcessPoolExecutor(max_workers=args.workers) as ex:
        futs = [ex.submit(job, s) for s in sp]
        for i, f in enumerate(as_completed(futs), 1):
            r = f.result()
            rows.append(r)
            print(f"[{i}/{len(sp)} {time.perf_counter() - t0:.0f}s] {r['part']} {r['form']} N={r['N']}: p2_best={r['p2_best']:.4f} "
                  f"p2_reject={r['p2_reject']:.3f} ({r['wall_s']:.0f}s)", flush=True)
    out = pd.DataFrame(rows)
    path = os.path.join(ROOT, "results", "scale_impact.csv")
    if args.grid_only:  # keep the conference rows of the existing table
        old = pd.read_csv(path)
        out = pd.concat([old[old.part != "grid"], out], ignore_index=True)
    out = out.sort_values(["part", "year", "N", "form"])
    out["year"] = out["year"].astype("Int64")
    out.to_csv(path, index=False)
    print(f"wrote {path}: {len(out)} rows")


if __name__ == "__main__":
    main()
