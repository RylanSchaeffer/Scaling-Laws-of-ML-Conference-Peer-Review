"""Reviews per paper that hold two reviews' top-ten overlap at its NeurIPS 2014 value, year by year.

For each NeurIPS year 2014-2026 (submissions from data/venues.csv), and for the main model with the
chairs' call (sigma_eta = 0.59) and without it (sigma_eta = 0, awards by the reviews alone), the
smallest number of reviews per paper R whose top-ten overlap reaches the 2014 value with four reviews
(bisection on integer R, linear interpolation between the bracketing integers; inf once R = R_MAX
fails). Acceptance is 25% of submissions, as on the submissions grid. The R -> infinity limit of each
model is also simulated: with infinitely many reviewers a paper's score is the expected snapped review
g(q), the same in both reviews, so two reviews differ only by the chair noise; this is the ceiling that
more reviews cannot pass.

Writes results/R_needed_years.csv. Usage: uv run python scripts/run_R_needed_years.py [--workers 8] [--reps 1000]
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
from peerreview.model import MAIN_FORM, ReviewModel, sample_quality
from peerreview.simulate import simulate_best_paper, stable_seed

K = 10
R_MAX = 64
FORM = MAIN_FORM
VARIANTS = {"chairs' call": 0.59, "reviews alone": 0.0}  # sigma_eta


def years() -> list[tuple[int, int]]:
    v = pd.read_csv(os.path.join(ROOT, "data", "venues.csv"))
    v = v[(v.venue == "NeurIPS") & (v.denominator != "decided")].sort_values("year")
    return [(int(y), int(n)) for y, n in zip(v.year, v.N_used)]


def overlap(m: ReviewModel, N: int, R: int, reps: int) -> float:
    mR = m.replace(R=R)
    r = simulate_best_paper(mR, N, reps, best_K=(1,), seed=stable_seed(mR.as_dict(), N, reps, "R_needed_years"),
                            second_committee=True, overlap_tiers={"top10": K}, accept=int(round(0.25 * N)))
    return float(r["overlap_top10"])


def expected_snapped(q: np.ndarray, m: ReviewModel) -> np.ndarray:
    """E[snap(q + eps)] on the model's integer scale: a paper's score with infinitely many reviewers."""
    pts = m.points
    mids = (pts[:-1] + pts[1:]) / 2.0
    cdf = ndtr((mids[None, :] - q[..., None]) / m.sigma_eps)  # P(review below each midpoint)
    probs = np.diff(np.concatenate([np.zeros(q.shape + (1,)), cdf, np.ones(q.shape + (1,))], axis=-1), axis=-1)
    return (probs * pts).sum(-1)


def limit_overlap(m: ReviewModel, N: int, reps: int, seed: int) -> float:
    """Top-ten overlap of two reviews with infinitely many reviewers each: same g(q), new chair noise."""
    rng = np.random.default_rng(seed)
    A = int(round(0.25 * N))
    out = 0.0
    for _ in range(reps):
        q = sample_quality(rng, (N,), m)
        g = expected_snapped(q, m)
        acc = np.argsort(-g)[:A]  # accepted by score, identical in both reviews
        t1 = g[acc] + m.sigma_award * rng.standard_normal(A)
        t2 = g[acc] + m.sigma_award * rng.standard_normal(A)
        top1 = set(np.argpartition(-t1, K - 1)[:K]) if m.sigma_award > 0 else set(np.argsort(-g[acc])[:K])
        top2 = set(np.argpartition(-t2, K - 1)[:K]) if m.sigma_award > 0 else top1
        out += len(top1 & top2) / K
    return out / reps


def job(spec: tuple) -> dict:
    name, sigma_eta, year, N, N0, reps = spec
    m = calibrated(main_model(sigma_u=0.0, sigma_award=sigma_eta), "central")
    t0 = time.perf_counter()
    target = overlap(m, N0, FORM["R"], reps)
    evals: dict[int, float] = {}

    def f(R: int) -> float:
        if R not in evals:
            evals[R] = overlap(m, N, R, reps)
        return evals[R]

    lo, hi = FORM["R"], FORM["R"]
    if f(lo) >= target:
        R_needed = float(lo)
    else:
        while f(hi) < target and hi < R_MAX:
            lo, hi = hi, min(2 * hi, R_MAX)
        if f(hi) < target:
            R_needed = np.inf
        else:
            while hi - lo > 1:
                mid = (lo + hi) // 2
                if f(mid) < target:
                    lo = mid
                else:
                    hi = mid
            R_needed = lo + (target - f(lo)) / (f(hi) - f(lo))
    lim = limit_overlap(m, N, 400, stable_seed(m.as_dict(), N, 400, "R_needed_years_limit"))
    return {"variant": name, "sigma_eta": sigma_eta, "year": year, "N": N, "target": target, "R_needed": R_needed,
            "limit_overlap": lim, "reachable": bool(lim >= target), "reps": reps, "sigma_eps": m.sigma_eps,
            "evals": len(evals), "evals_detail": ";".join(f"{R}:{v:.4f}" for R, v in sorted(evals.items())),
            "wall_s": time.perf_counter() - t0}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--reps", type=int, default=1000)
    args = ap.parse_args()
    ys = years()
    N0 = dict(ys)[2014]
    specs = [(name, se, y, n, N0, args.reps) for name, se in VARIANTS.items() for y, n in ys]
    specs.sort(key=lambda s: -s[3])
    rows, t0 = [], time.perf_counter()
    with ProcessPoolExecutor(max_workers=args.workers) as ex:
        futs = [ex.submit(job, s) for s in specs]
        for i, fu in enumerate(as_completed(futs), 1):
            r = fu.result()
            rows.append(r)
            print(f"[{i}/{len(specs)} {time.perf_counter() - t0:.0f}s] {r['variant']} {r['year']} N={r['N']}: R_needed={r['R_needed']:.1f} "
                  f"target={r['target']:.4f} limit={r['limit_overlap']:.4f} ({r['wall_s']:.0f}s)", flush=True)
    out = pd.DataFrame(rows).sort_values(["variant", "year"])
    path = os.path.join(ROOT, "results", "R_needed_years.csv")
    out.to_csv(path, index=False)
    print(f"wrote {path}: {len(out)} rows")


if __name__ == "__main__":
    main()
