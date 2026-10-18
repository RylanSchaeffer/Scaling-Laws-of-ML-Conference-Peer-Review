"""Exact part of the reviews ladder: two reviews of every paper with R reviewers each, for R up to 32.

For each N on the dense submissions grid (13 points, 1,000 to 100,000) the main model (per-review noise
at its R = 4 calibration, the chairs' call on, sigma_eta = 0.59) is simulated with 32 integer reviews
per paper and per review; the mean of the first R of them is the paper's score with R reviews, so every
rung of the ladder is evaluated on the same draws (common random numbers) and the overlap rises
smoothly with R. The overlap of two reviews' tiers is the proportion of one review's tier that the
other also puts there: the three Best Papers (a constant number), the orals and the spotlights (NeurIPS's fitted
trends, results/tier_sizes.csv) and the accepted papers (25% of N). R = 64 is also run at three sizes
as a check on the normal approximation of run_R_needed_tiers_large.py, which carries the ladder beyond
32 reviews and to the limit of infinitely many.

Writes results/R_needed_tiers_exact.csv, one row per (N, R). summarize_R_needed_tiers.py merges the two
parts into results/R_needed_tiers.csv and results/R_needed_tiers_summary.csv.
Usage: uv run python scripts/run_R_needed_tiers.py [--workers 8] [--reps 2000] [--base-reps 50000] [--chunk 250]
The 1,000-submission rows, which set every tier's target, have base-reps replays.
"""
from __future__ import annotations

import argparse
import os
import time
from concurrent.futures import ProcessPoolExecutor, as_completed

import numpy as np
import pandas as pd

from peerreview.levels import ROOT, calibrated, main_model
from peerreview.model import sample_quality, snap
from peerreview.simulate import stable_seed
from peerreview.tiers import tier_size
from run_best_paper import N_BEST

N_GRID = [int(round(10 ** (3 + k / 6))) for k in range(13)]  # 1000, 1468, 2154, ... 68129, 100000
R_LADDER = [4, 5, 6, 8, 10, 12, 16, 20, 24, 32]
R_CHECK = {64: [10_000, 46_416, 100_000]}  # exact rungs beyond the ladder, as a check on the approximation
TIERS = ("best", "oral", "spot", "accept")


def tiers_at(fits: pd.DataFrame, N: int) -> dict:
    orals = tier_size(fits, "orals", N)
    return {"best": N_BEST, "oral": orals, "spot": orals + tier_size(fits, "spotlights", N), "accept": int(round(0.25 * N))}


def snap_scores(x: np.ndarray, pts: np.ndarray) -> np.ndarray:
    """model.snap, with the fast path for an integer scale: the nearest integer, midpoints up."""
    if np.array_equal(pts, np.arange(pts[0], pts[-1] + 1)):
        return np.clip(np.floor(x + 0.5), pts[0], pts[-1])
    return snap(x, pts)


def tier_overlaps(reviews: list[tuple], R: int, sizes: dict, A: int) -> dict:
    """Overlap per tier of two reviews' tiers with R reviewers each, from the prefix sums of their scores."""
    accs, tops = [], []
    for cs, jit, eta in reviews:
        sbar = cs[:, R - 1] / R + jit  # the jitter breaks ties uniformly at random, as model.jitter does
        acc = np.argpartition(-sbar, A - 1)[:A]
        t = sbar[acc] + eta[acc]  # the award ordering within the accepted set (model.award_order)
        accs.append(acc)
        tops.append(acc[np.argsort(-t)])
    out = {}
    for name, K in sizes.items():
        if name == "accept":
            out[name] = np.intersect1d(accs[0], accs[1], assume_unique=True).size / A
        else:
            out[name] = np.intersect1d(tops[0][:K], tops[1][:K], assume_unique=True).size / K
    return out


def job(spec: dict) -> list[dict]:
    m = calibrated(main_model(sigma_u=0.0), "central")
    if "sigma_award" in spec:  # run_chair_calls.py: the chair noise of k averaged calls
        m = m.replace(sigma_award=float(spec["sigma_award"]))
    assert m.noise == "gaussian" and m.sigma_u == 0 and m.careless == 0, "the ladder is the main model"
    N, reps, chunk, Rs = spec["N"], spec["reps"], spec["chunk"], list(spec["Rs"])
    Rmax = max(Rs)
    sizes = dict(spec["sizes"])
    A = sizes["accept"]
    pts = m.points
    rng = np.random.default_rng(stable_seed(m.as_dict(), N, reps, chunk, Rmax, "R_needed_tiers_exact"))
    t0 = time.perf_counter()
    acc = {R: {t: 0.0 for t in TIERS} for R in Rs}
    for _ in range(reps):
        q = sample_quality(rng, (N,), m)
        reviews = []
        for _k in range(2):
            s = snap_scores(q[:, None] + m.sigma_eps * rng.standard_normal((N, Rmax)), pts)
            cs = np.cumsum(s, axis=1)
            jit = 1e-6 / Rmax * rng.random(N)
            eta = m.sigma_award * rng.standard_normal(N)
            reviews.append((cs, jit, eta))
        for R in Rs:
            o = tier_overlaps(reviews, R, sizes, A)
            for t in TIERS:
                acc[R][t] += o[t]
    wall = time.perf_counter() - t0
    return [{"N": N, "R": R, "orals": sizes["oral"], "spotlights": sizes["spot"] - sizes["oral"], "reps": reps, "chunk": chunk,
             **{f"overlap_{t}": acc[R][t] / reps for t in TIERS}, "sigma_eps": m.sigma_eps, "method": "exact", "wall_s": wall / len(Rs)}
            for R in Rs]


def aggregate(df: pd.DataFrame) -> pd.DataFrame:
    """Average the chunks of equal size; the SE is across chunks."""
    keys = ["N", "R", "orals", "spotlights", "sigma_eps", "method"]
    agg = {f"overlap_{t}": "mean" for t in TIERS}
    agg.update({"reps": "sum", "wall_s": "sum"})
    g = df.groupby(keys, dropna=False)
    out = g.agg(agg).reset_index()
    for t in TIERS:
        out[f"overlap_{t}_se"] = (g[f"overlap_{t}"].std(ddof=1) / np.sqrt(g[f"overlap_{t}"].size())).values
    return out.sort_values(["N", "R"]).reset_index(drop=True)


def run(specs: list[dict], workers: int, tag: str) -> pd.DataFrame:
    rows, t0 = [], time.perf_counter()
    with ProcessPoolExecutor(max_workers=workers) as ex:
        futs = [ex.submit(job, s) for s in specs]
        for i, fu in enumerate(as_completed(futs), 1):
            rs = fu.result()
            rows.extend(rs)
            r = rs[0]
            print(f"[{tag} {i}/{len(specs)} {time.perf_counter() - t0:.0f}s] N={r['N']} chunk {r['chunk']}: R={r['R']} best {r['overlap_best']:.3f} "
                  f"oral {r['overlap_oral']:.3f} spot {r['overlap_spot']:.3f} accept {r['overlap_accept']:.3f} ({r['wall_s'] * len(rs):.0f}s)", flush=True)
    return aggregate(pd.DataFrame(rows))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--reps", type=int, default=2000)
    ap.add_argument("--base-reps", type=int, default=50_000, help="replays at 1,000 submissions, which set every tier's target")
    ap.add_argument("--chunk", type=int, default=250)
    args = ap.parse_args()
    fits = pd.read_csv(os.path.join(ROOT, "results", "tier_sizes.csv"))
    specs = []
    for N in N_GRID:
        reps = args.base_reps if N == N_GRID[0] else args.reps
        chunk = args.chunk * (args.base_reps // args.reps) if N == N_GRID[0] else args.chunk
        Rs = R_LADDER + [R for R, Ns in R_CHECK.items() if N in Ns]
        for c in range(int(np.ceil(reps / chunk))):
            specs.append({"N": N, "Rs": Rs, "sizes": tiers_at(fits, N), "reps": chunk, "chunk": c})
    specs.sort(key=lambda s: -s["N"] * max(s["Rs"]))
    df = run(specs, args.workers, "exact")
    path = os.path.join(ROOT, "results", "R_needed_tiers_exact.csv")
    df.to_csv(path, index=False)
    print(f"wrote {path}: {len(df)} rows")
    print(df.pivot(index="N", columns="R", values="overlap_best").round(3).to_string())


if __name__ == "__main__":
    main()
