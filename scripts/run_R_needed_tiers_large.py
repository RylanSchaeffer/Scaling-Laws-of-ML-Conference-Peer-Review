"""The reviews ladder beyond 32 reviews per paper, and in the limit of infinitely many.

A paper's mean snapped score over R reviews is g(q) + sd(q) z / sqrt(R) to a very good approximation
for R >= 32 (a mean of R bounded, independent reviews), where g(q) = E[snap(q + eps)] and sd(q) is the
SD of one snapped review, both on the 1-10 scale. Two reviews draw their own z and their own chair
noise eta; with R = inf they share g(q) and differ only by eta, so the overlap that remains is the
agreement the chairs' call allows at best. Every rung of the ladder is evaluated on the same draws
(common random numbers), so the overlap rises smoothly with R and the crossing of a target is
well determined where the curve is flat.

Pass 1: the R = inf overlaps on a fine grid of sizes, 20,000 to 100,000 submissions, which locates N*,
the size from which the top ten's target (its overlap at 1,000 submissions with four reviews) is out of
reach for any number of reviews. Pass 2: the ladder R = 32 ... 4096 and inf on the dense submissions
grid of run_R_needed_tiers.py plus three sizes approaching N*.

Writes results/R_needed_tiers_limit.csv (pass 1) and results/R_needed_tiers_clt.csv (pass 2).
summarize_R_needed_tiers.py merges them with the exact rows.
Usage: uv run python scripts/run_R_needed_tiers_large.py [--workers 8] [--reps 2000] [--limit-reps 5000] [--chunk 500] [--base-reps 50000] [--reuse-limit]
"""
from __future__ import annotations

import argparse
import os
import time
from concurrent.futures import ProcessPoolExecutor, as_completed

import numpy as np
import pandas as pd
from scipy.special import ndtr

from peerreview.levels import ROOT, calibrated, main_model
from peerreview.model import MAIN_FORM, sample_quality
from peerreview.simulate import simulate_best_paper, stable_seed
from peerreview.tiers import tier_size
from run_R_needed_tiers import N_GRID, TIERS, aggregate, tiers_at

R_LARGE = [32, 64, 96, 128, 192, 256, 512, 1024, 2048, 4096, np.inf]  # 32 and 64 repeat exact rungs as a check
N_FINE = [int(round(x)) for x in np.geomspace(20_000, 100_000, 12)]  # pass 1: where does the top ten's target leave reach?
APPROACH = (0.80, 0.90, 0.95)  # pass 2 adds N* times these


def snapped_moments(q: np.ndarray, m) -> tuple[np.ndarray, np.ndarray]:
    """Mean and SD of one snapped review given quality q, on the model's scale."""
    pts = m.points
    mids = (pts[:-1] + pts[1:]) / 2.0
    cdf = ndtr((mids[None, :] - q[..., None]) / m.sigma_eps)
    probs = np.diff(np.concatenate([np.zeros(q.shape + (1,)), cdf, np.ones(q.shape + (1,))], axis=-1), axis=-1)
    mean = (probs * pts).sum(-1)
    var = (probs * pts ** 2).sum(-1) - mean ** 2
    return mean, np.sqrt(np.maximum(var, 0.0))


def overlaps(g, sd, z, eta, R, sizes, A) -> dict:
    """One pair of reviews with R reviewers each on shared draws z (2 x N) and eta (2 x N); overlap per tier."""
    accs, tops = [], []
    for k in range(2):
        sbar = g + (sd * z[k] / np.sqrt(R) if np.isfinite(R) else 0.0)
        acc = np.argpartition(-sbar, A - 1)[:A]
        t = sbar[acc] + eta[k][acc]  # the award ordering within the accepted set
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
    N, reps, chunk, Rs = spec["N"], spec["reps"], spec["chunk"], spec["Rs"]
    sizes = dict(spec["sizes"])
    A = sizes["accept"]
    rng = np.random.default_rng(stable_seed(m.as_dict(), N, reps, chunk, "R_needed_tiers_clt"))
    t0 = time.perf_counter()
    acc = {R: {t: 0.0 for t in TIERS} for R in Rs}
    for _ in range(reps):
        q = sample_quality(rng, (N,), m)
        g, sd = snapped_moments(q, m)
        z = rng.standard_normal((2, N))
        eta = m.sigma_award * rng.standard_normal((2, N))
        for R in Rs:
            o = overlaps(g, sd, z, eta, R, sizes, A)
            for t in TIERS:
                acc[R][t] += o[t]
    wall = time.perf_counter() - t0
    return [{"N": N, "R": R, "orals": sizes["oral"], "spotlights": sizes["spot"] - sizes["oral"], "reps": reps, "chunk": chunk,
             **{f"overlap_{t}": acc[R][t] / reps for t in TIERS}, "sigma_eps": m.sigma_eps,
             "method": "clt" if np.isfinite(R) else "limit", "wall_s": wall / len(Rs)} for R in Rs]


def run(specs: list[dict], workers: int, tag: str) -> pd.DataFrame:
    rows, t0 = [], time.perf_counter()
    with ProcessPoolExecutor(max_workers=workers) as ex:
        futs = [ex.submit(job, s) for s in specs]
        for i, fu in enumerate(as_completed(futs), 1):
            rs = fu.result()
            rows.extend(rs)
            r = rs[-1]
            print(f"[{tag} {i}/{len(specs)} {time.perf_counter() - t0:.0f}s] N={r['N']} chunk {r['chunk']}: R={r['R']} top10 {r['overlap_top10']:.3f} "
                  f"oral {r['overlap_oral']:.3f} ({r['wall_s'] * len(rs):.0f}s)", flush=True)
    return aggregate(pd.DataFrame(rows))


def top10_target(reps: int) -> float:
    """The top ten's overlap at 1,000 submissions with four reviews: the exact ladder's base row when it exists, else simulated."""
    path = os.path.join(ROOT, "results", "R_needed_tiers_exact.csv")
    if os.path.exists(path):
        e = pd.read_csv(path)
        row = e[(e.N == N_GRID[0]) & (e.R == MAIN_FORM["R"])]
        if len(row):
            return float(row.overlap_top10.iloc[0])
    m = calibrated(main_model(sigma_u=0.0), "central")
    fits = pd.read_csv(os.path.join(ROOT, "results", "tier_sizes.csv"))
    r = simulate_best_paper(m, N_GRID[0], reps, best_K=(1,), seed=stable_seed(m.as_dict(), N_GRID[0], reps, "R_needed_tiers"),
                            second_committee=True, overlap_tiers=tiers_at(fits, N_GRID[0]))
    return float(r["overlap_top10"])


def n_star(N: np.ndarray, limit: np.ndarray, target: float) -> float:
    """The size at which the R = inf top-ten overlap falls to the target, interpolated in log N; inf if it never does."""
    order = np.argsort(N)
    N, limit = N[order], limit[order]
    for i in range(1, len(N)):
        if limit[i - 1] >= target > limit[i]:
            f = (limit[i - 1] - target) / (limit[i - 1] - limit[i])
            return float(np.exp(np.log(N[i - 1]) + f * (np.log(N[i]) - np.log(N[i - 1]))))
    return float("inf")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--reps", type=int, default=2000, help="replays per (N, R) on the ladder, split into chunks")
    ap.add_argument("--limit-reps", type=int, default=5000, help="replays per size in the R = inf pass")
    ap.add_argument("--chunk", type=int, default=500)
    ap.add_argument("--reuse-limit", action="store_true", help="skip pass 1 and read results/R_needed_tiers_limit.csv")
    ap.add_argument("--base-reps", type=int, default=50_000, help="replays of run_R_needed_tiers.py at 1,000 submissions, which set the target")
    args = ap.parse_args()
    fits = pd.read_csv(os.path.join(ROOT, "results", "tier_sizes.csv"))

    def specs(Ns, Rs, reps):
        return sorted([{"N": N, "Rs": Rs, "sizes": tiers_at(fits, N), "reps": args.chunk, "chunk": c}
                       for N in Ns for c in range(int(np.ceil(reps / args.chunk)))], key=lambda s: -s["N"])

    path = os.path.join(ROOT, "results", "R_needed_tiers_limit.csv")
    if args.reuse_limit:
        lim = pd.read_csv(path)
        target = float(lim.target_top10.iloc[0])
    else:
        target = top10_target(args.base_reps)
        print(f"top-ten target (1,000 submissions, 4 reviews): {target:.4f}")
        lim = run(specs(N_FINE, [np.inf], args.limit_reps), args.workers, "limit")
        lim["target_top10"] = target
        lim.to_csv(path, index=False)
    ns = n_star(lim.N.values.astype(float), lim.overlap_top10.values, target)
    print(f"{path}; target {target:.4f}; N* = {ns:,.0f}")
    print(lim[["N", "overlap_top10", "overlap_top10_se", "overlap_oral", "overlap_spot"]].round(4).to_string(index=False))

    Ns = sorted(set(N_GRID) | ({int(round(ns * f)) for f in APPROACH} if np.isfinite(ns) else set()))
    clt = run(specs(Ns, R_LARGE, args.reps), args.workers, "ladder")
    path = os.path.join(ROOT, "results", "R_needed_tiers_clt.csv")
    clt.to_csv(path, index=False)
    print(f"wrote {path}: {len(clt)} rows")


if __name__ == "__main__":
    main()
