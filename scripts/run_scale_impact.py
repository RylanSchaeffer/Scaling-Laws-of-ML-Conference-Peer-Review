"""Does the score scale change the main results? The same model on every real review form
(data/review_forms.csv) and on continuous scores, each recalibrated at the central level.

Part "conference": the NeurIPS 2026 and 2014 conferences (submissions, acceptance rate, oral and
spotlight counts) under each form: where a second review places the first review's three Best Papers
(p2_* for each separate tier and p2_*_or_better for each "or Better" set; p2_best is the share it keeps among its own Best Papers).
Part "grid": a submissions grid 1K to 100K with the fitted tier sizes and 25% acceptance, for the
main form, the six-point form, the ICLR 2022-2025 form and continuous scores.

The grid uses the replays of run_best_paper_hirep.py's central grid (50,000 up to 10K submissions, 120,000 above), in
chunks of 10,000 with one seed each; the main form's grid rows are read from results/best_paper.csv (the same draws),
so its curve is the one of Fig. 1d.

Writes results/scale_impact.csv.
Usage: uv run python scripts/run_scale_impact.py [--workers 2] [--grid-only]
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
from peerreview.tiers import CUTS, add_separate, cuts, fitted_count
from run_best_paper import N_BEST, N_GRID  # the submissions grid of results/best_paper.csv
from run_best_paper_hirep import CHUNK, reps_hirep

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
REPS_CONF = {2026: 40_000, 2014: 100_000}


def job(spec: dict) -> dict:
    m = calibrated(main_model(R=spec["R"], scale=spec["scale"]), spec["level"])
    N, A = spec["N"], int(round(spec["alpha"] * spec["N"]))
    cut_sizes = cuts(N_BEST, int(spec["n_oral_or_better"]), int(spec["spotlights"]), A)
    if spec["part"] == "grid":  # one chunk of the grid point's replays
        main_form = spec["scale"] == MAIN_FORM["scale"] and spec["R"] == MAIN_FORM["R"]
        seed = (stable_seed(m.as_dict(), N, spec["reps"], "best_paper_hirep", "central", "grid", spec["chunk"]) if main_form
                else stable_seed(m.as_dict(), N, spec["reps"], "scale_impact", "grid", spec["chunk"]))
        reps = CHUNK
    else:
        seed = stable_seed(m.as_dict(), N, spec["reps"], "scale_impact", spec["part"])
        reps = spec["reps"]
    t0 = time.perf_counter()
    r = simulate_best_paper(m, N, reps, best_K=(1,), seed=seed, best_papers_cuts=cut_sizes,
                            second_committee=True, n_best=N_BEST)  # lean: no overlaps, which the paper does not use
    out = {**spec, "rho2": LEVELS[spec["level"]], "sigma_eps": m.sigma_eps, "accepted": A, "seed": seed}
    for name in CUTS:  # "or Better" probabilities; the Best Papers are their own
        out[f"p2_{name}"] = r[f"best_papers_in2_{name}"]
        out[f"p2_{name}_se"] = r[f"best_papers_in2_{name}_se"]
        out[f"p_{name}"] = r[f"best_papers_in_{name}"]
    add_separate(out, "p2")  # the separate tiers: p2_oral, p2_spot, p2_accept, p2_reject
    add_separate(out, "p")
    out["best_papers_rank2_median"] = r["best_papers_rank2_median"]
    out["wall_s"] = time.perf_counter() - t0
    return out


def specs(grid_only: bool = False) -> list[dict]:
    v = pd.read_csv(os.path.join(ROOT, "data", "venues.csv"))
    sp = pd.read_csv(os.path.join(ROOT, "data", "spotlights.csv"))[["venue", "year", "spotlights"]]
    v = v[(v.venue == "NeurIPS") & (v.denominator != "decided")].merge(sp, on=["venue", "year"])
    fits = pd.read_csv(os.path.join(ROOT, "results", "tier_sizes.csv"))
    out = []
    for year, reps in ({} if grid_only else REPS_CONF).items():
        x = v[v.year == year].iloc[0]
        for label, R, scale, who in FORMS:
            out.append({"part": "conference", "form": label, "used_by": who, "R": R, "scale": scale, "year": year,
                        "N": int(x.N_used), "alpha": float(x.acc_rate_used), "n_oral_or_better": int(x.orals_used),
                        "spotlights": int(x.spotlights), "level": "central", "reps": reps})
    for label, R, scale, who in FORMS:
        if scale not in GRID_FORMS or R != MAIN_FORM["R"]:
            continue
        for N in N_GRID:
            out.append({"part": "grid", "form": label, "used_by": who, "R": R, "scale": scale, "year": np.nan, "N": N,
                        "alpha": 0.25, "n_oral_or_better": fitted_count(fits, "oral_or_better", N), "spotlights": fitted_count(fits, "spot", N),
                        "level": "central", "reps": reps_hirep(N, "central", "grid")})
    grid = [s for s in out if s["part"] == "grid" and not (s["scale"] == MAIN_FORM["scale"] and s["R"] == MAIN_FORM["R"])]  # main form: read
    out = [s for s in out if s["part"] != "grid"] + [{**s, "chunk": c} for s in grid for c in range(s["reps"] // CHUNK)]
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=2)
    ap.add_argument("--grid-only", action="store_true", help="re-simulate only the grid rows and replace them in the existing table")
    args = ap.parse_args()
    sp = sorted(specs(args.grid_only), key=lambda s: -s["N"] * s["R"] * (CHUNK if s["part"] == "grid" else s["reps"]))
    rows, t0 = [], time.perf_counter()
    with ProcessPoolExecutor(max_workers=args.workers) as ex:
        futs = [ex.submit(job, s) for s in sp]
        for i, f in enumerate(as_completed(futs), 1):
            r = f.result()
            rows.append(r)
            print(f"[{i}/{len(sp)} {time.perf_counter() - t0:.0f}s] {r['part']} {r['form']} N={r['N']}: p2_best={r['p2_best']:.4f} "
                  f"p2_reject={r['p2_reject']:.3f} ({r['wall_s']:.0f}s)", flush=True)
    out = pd.DataFrame(rows)
    if "chunk" in out:  # grid points: equal chunks, so the mean of their means and the SE of that mean
        g, conf = out[out.part == "grid"], out[out.part != "grid"].drop(columns="chunk")
        keys = ["part", "form", "used_by", "R", "scale", "N", "alpha", "n_oral_or_better", "spotlights", "level", "reps", "rho2", "sigma_eps", "accepted"]
        agg = []
        for _, d in g.groupby(["form", "N"]):
            row = {k: d[k].iloc[0] for k in keys}
            row["year"], row["seed"], row["wall_s"] = np.nan, int(d.seed.min()), d.wall_s.sum()
            for c in CUTS:
                row[f"p2_{c}"], row[f"p_{c}"] = d[f"p2_{c}"].mean(), d[f"p_{c}"].mean()
                row[f"p2_{c}_se"] = float(np.sqrt((d[f"p2_{c}_se"] ** 2).sum()) / len(d))
            add_separate(row, "p2")
            add_separate(row, "p")
            agg.append(row)
        b = pd.read_csv(os.path.join(ROOT, "results", "best_paper.csv"))  # the main form's grid: the same draws, so read, not re-run
        b = b[(b.source == "grid") & (b.level == "central") & b.N.isin(N_GRID)]
        label, R, scale, who = next(f for f in FORMS if f[2] == MAIN_FORM["scale"] and f[1] == MAIN_FORM["R"])
        main = [{"part": "grid", "form": label, "used_by": who, "R": R, "scale": scale, "year": np.nan, "N": int(r.N), "alpha": r.alpha,
                 "n_oral_or_better": r.n_oral_or_better, "spotlights": r.spotlights, "level": "central", "reps": int(r.reps_best),
                 "rho2": r.rho2, "sigma_eps": r.sigma_eps, "accepted": r.accepted, "seed": int(r.seed_best), "wall_s": np.nan,
                 **{k: getattr(r, k) for k in b.columns if k.startswith("p2_") or k.startswith("p_")}} for r in b.itertuples()]
        out = pd.concat([conf, pd.DataFrame(agg), pd.DataFrame(main)], ignore_index=True)
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
