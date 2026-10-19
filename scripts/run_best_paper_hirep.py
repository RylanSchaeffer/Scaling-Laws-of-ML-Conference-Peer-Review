"""More replays for where a second review places the Best Papers. The rows of results/best_paper.csv come
from 10,000 replays (5,000 above 10K submissions on the grid), enough for the overlaps but not for the
Best Papers' small probabilities, which fall below 1% at 100K. This script re-simulates every p2_* of
those rows on the main form with many more replays (lean: no overlaps) and writes them back: p2_best,
p2_oral_or_better, p2_spot_or_better, p2_accept_or_better and, from them, the separate tiers p2_oral,
p2_spot, p2_accept and p2_reject (peerreview.tiers.add_separate), with the replay count in reps_best.
The Best Papers are the first three papers of the award ordering; p2_best, the share of them a second
review also ranks in its top three, equals overlap_best. The replays run in chunks of CHUNK, each with
its own seed; a row's mean is the mean over its chunks and its SE combines theirs.

Usage: uv run python scripts/run_best_paper_hirep.py [--workers 2] [--venues]
  --venues does the same for the cited venue-years (NeurIPS 2014, 2021, 2026; ICML and ICLR 2026).
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
from peerreview.tiers import CUTS, add_separate, cuts
from run_best_paper import N_BEST

PATH = os.path.join(ROOT, "results", "best_paper.csv")
CHUNK = 10_000  # replays per job


def reps_for(N: int) -> int:
    """Replays per row (run_best_paper_size.py uses the same rule)."""
    return 50_000 if N <= 10_000 else 30_000 if N <= 32_000 else 20_000


def reps_hirep(N: int, level: str, key: str) -> int:
    """The central grid above 10K submissions draws Fig. 1d, so it gets enough replays for a smooth curve."""
    return 120_000 if key == "grid" and level == "central" and N > 10_000 else reps_for(N)


VENUE_YEARS = (("NeurIPS", 2014), ("NeurIPS", 2021), ("NeurIPS", 2026), ("ICML", 2026), ("ICLR", 2026))  # the cited ones


def job(spec: tuple) -> dict:
    N, level, key, c_items, reps, chunk = spec
    m = calibrated(main_model(), level)
    seed = stable_seed(m.as_dict(), N, reps, "best_paper_hirep", level, key, chunk)
    t0 = time.perf_counter()
    r = simulate_best_paper(m, N, CHUNK, best_K=(1,), seed=seed, best_papers_cuts=dict(c_items), second_committee=True,
                            n_best=N_BEST)
    out = {"N": N, "level": level, "key": key, "reps": reps, "chunk": chunk, "seed": seed, "wall_s": time.perf_counter() - t0}
    for c, _ in c_items:
        out[f"p2_{c}"], out[f"p2_{c}_se"] = r[f"best_papers_in2_{c}"], r[f"best_papers_in2_{c}_se"]
    return out


def combine(chunks: list[dict]) -> dict:
    """Equal-sized chunks: the mean of their means, and the SE of that mean from theirs."""
    k = len(chunks)
    out = {"reps_best": chunks[0]["reps"], "seed_best": min(c["seed"] for c in chunks)}
    for name in [x for x in chunks[0] if x.startswith("p2_") and not x.endswith("_se")]:
        out[name] = float(np.mean([c[name] for c in chunks]))
        out[f"{name}_se"] = float(np.sqrt(np.sum([c[f"{name}_se"] ** 2 for c in chunks])) / k)
    add_separate(out, "p2")
    out["overlap_best"], out["overlap_best_se"] = out["p2_best"], out["p2_best_se"]
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=2)
    ap.add_argument("--venues", action="store_true", help="the cited venue-years (VENUE_YEARS) instead of the grid")
    ap.add_argument("--levels", default="", help="comma-separated levels to re-simulate (default: all)")
    args = ap.parse_args()
    b = pd.read_csv(PATH)
    if args.venues:
        cited = pd.Series([(v, int(y)) in VENUE_YEARS if y == y else False for v, y in zip(b.venue, b.year)], index=b.index)
        rows = b[(b.source == "venue") & cited]
        keyof = lambda r: f"{r.venue}{int(r.year)}"  # noqa: E731
    else:
        rows = b[b.source == "grid"]
        keyof = lambda r: "grid"  # noqa: E731
    if args.levels:
        rows = rows[rows.level.isin(args.levels.split(","))]
    specs = []
    for r in rows.itertuples():
        c = cuts(N_BEST, r.n_oral_or_better, r.spotlights, r.accepted)
        reps = reps_hirep(int(r.N), r.level, keyof(r))
        assert reps % CHUNK == 0
        specs += [(int(r.N), r.level, keyof(r), tuple((k, int(c[k])) for k in CUTS if k in c), reps, i) for i in range(reps // CHUNK)]
    specs.sort(key=lambda s: -s[0])
    n_chunks = {}
    for s in specs:
        n_chunks[s[:3]] = n_chunks.get(s[:3], 0) + 1
    done: dict[tuple, list] = {}
    t0 = time.perf_counter()
    with ProcessPoolExecutor(max_workers=args.workers) as ex:
        futs = [ex.submit(job, s) for s in specs]
        for i, f in enumerate(as_completed(futs), 1):
            r = f.result()
            key = (r["N"], r["level"], r["key"])
            done.setdefault(key, []).append(r)
            if len(done[key]) < n_chunks[key]:
                continue
            row = combine(done[key])
            mask = (b.source == ("grid" if r["key"] == "grid" else "venue")) & (b.N == r["N"]) & (b.level == r["level"])
            if r["key"] != "grid":
                mask &= (b.venue + b.year.astype("Int64").astype(str)) == r["key"]
            assert mask.sum() == 1
            for k, v in row.items():
                b.loc[mask, k] = v
            print(f"[{i}/{len(specs)} {time.perf_counter() - t0:.0f}s] N={r['N']} {r['level']} {r['key']}: p2_best={row['p2_best']:.5f}"
                  f"+-{row['p2_best_se']:.5f} p2_accept={row.get('p2_accept', np.nan):.4f} ({row['reps_best']} reps)", flush=True)
            b.to_csv(PATH, index=False)  # checkpoint after every row
    print(f"updated {PATH}")


if __name__ == "__main__":
    main()
