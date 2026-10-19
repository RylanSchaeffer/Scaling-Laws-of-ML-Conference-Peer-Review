"""Does the number of Best Papers matter? Best Papers again for two, three and four Best Papers.

The paper holds the Best Papers at three, between NeurIPS's median (2.5) and mean (3.5) a year. This
script re-simulates Best Papers again (a second review also ranks a paper among the first review's Best
Papers among its own Best Papers) on the main form and with continuous scores at the central level, on the
submissions grid, for 2, 3 and 4 Best Papers. Every size is read off the same conferences, so the fitted
power-law exponents can be compared directly. On the main form those are the conferences of the central grid of
run_best_paper_hirep.py (its replays, chunks and seeds), so three Best Papers are read from results/best_paper.csv
rather than re-run (the same draws give the same values); continuous scores use one seed per N.

Writes results/best_paper_size.csv.
Usage: uv run python scripts/run_best_paper_size.py [--workers 2]
"""
from __future__ import annotations

import argparse
import os
import time
from concurrent.futures import ProcessPoolExecutor, as_completed

import numpy as np
import pandas as pd

from peerreview.levels import ROOT, calibrated, main_model
from peerreview.model import MAIN_FORM
from peerreview.simulate import simulate_best_paper, stable_seed
from run_best_paper import N_GRID  # the submissions grid of results/best_paper.csv
from run_best_paper_hirep import CHUNK, reps_for, reps_hirep

SIZES = (2, 3, 4)
SCALES = (MAIN_FORM["scale"], "continuous")  # the main form, and continuous scores (the power-law derivation's model)


def plan(N: int, scale: str) -> tuple[int, int]:
    """(replays, chunks): the main form follows the hirep central grid; continuous scores run in one chunk."""
    if scale == MAIN_FORM["scale"]:
        reps = reps_hirep(N, "central", "grid")
        return reps, reps // CHUNK
    return reps_for(N), 1


def job(spec: tuple) -> dict:
    N, k, scale, chunk = spec
    m = calibrated(main_model(scale=scale), "central")
    reps, n_chunks = plan(N, scale)
    if scale == MAIN_FORM["scale"]:  # the seeds of run_best_paper_hirep.py's central grid
        seed = stable_seed(m.as_dict(), N, reps, "best_paper_hirep", "central", "grid", chunk)
    else:
        seed = stable_seed(m.as_dict(), N, reps, "best_paper_size")  # one seed per N: every size sees the same conferences
    t0 = time.perf_counter()
    r = simulate_best_paper(m, N, reps // n_chunks, best_K=(1,), seed=seed, best_papers_cuts={"best": k}, second_committee=True,
                            n_best=k)
    return {"N": N, "n_best": k, "scale": scale, "chunk": chunk, "reps": reps, "seed": seed, "p2_best": r["best_papers_in2_best"],
            "p2_best_se": r["best_papers_in2_best_se"], "wall_s": time.perf_counter() - t0}


def exponent(d: pd.DataFrame) -> float:
    k, _ = np.polyfit(np.log(d.N.values), np.log(d.p2_best.values), 1)
    return -k


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=2)
    args = ap.parse_args()
    main3 = lambda k, sc: k == 3 and sc == MAIN_FORM["scale"]  # noqa: E731  (identical to the hirep central grid: read, not re-run)
    specs = sorted([(N, k, sc, c) for N in N_GRID for k in SIZES for sc in SCALES if not main3(k, sc) for c in range(plan(N, sc)[1])],
                   key=lambda s: -s[0])
    chunks, t0 = [], time.perf_counter()
    with ProcessPoolExecutor(max_workers=args.workers) as ex:
        futs = [ex.submit(job, s) for s in specs]
        for i, f in enumerate(as_completed(futs), 1):
            r = f.result()
            chunks.append(r)
            print(f"[{i}/{len(specs)} {time.perf_counter() - t0:.0f}s] N={r['N']} {r['scale']} Best Papers {r['n_best']} chunk {r['chunk']}: "
                  f"{r['p2_best']:.5f}+-{r['p2_best_se']:.5f} ({r['wall_s']:.0f}s)", flush=True)
    rows = []
    for (N, k, sc), g in pd.DataFrame(chunks).groupby(["N", "n_best", "scale"]):  # equal chunks: mean of means, SE from theirs
        rows.append({"N": N, "n_best": k, "scale": sc, "level": "central", "reps": int(g.reps.iloc[0]), "seed": int(g.seed.min()),
                     "p2_best": g.p2_best.mean(), "p2_best_se": float(np.sqrt((g.p2_best_se ** 2).sum()) / len(g)), "wall_s": g.wall_s.sum()})
    b = pd.read_csv(os.path.join(ROOT, "results", "best_paper.csv"))
    g = b[(b.source == "grid") & (b.level == "central") & b.N.isin(N_GRID)]
    rows += [{"N": int(r.N), "n_best": 3, "scale": MAIN_FORM["scale"], "level": "central", "reps": int(r.reps_best), "seed": int(r.seed_best),
              "p2_best": r.p2_best, "p2_best_se": r.p2_best_se, "wall_s": np.nan} for r in g.itertuples()]
    df = pd.DataFrame(rows).sort_values(["scale", "n_best", "N"])
    path = os.path.join(ROOT, "results", "best_paper_size.csv")
    df.to_csv(path, index=False)
    for (sc, k), d in df.groupby(["scale", "n_best"]):
        print(f"{sc} {k} Best Papers: {100 * d.p2_best.iloc[0]:.2f}% at 1,000, {100 * d.p2_best.iloc[-1]:.3f}% at 100,000; exponent {exponent(d):.2f}")
    print(f"wrote {path}")


if __name__ == "__main__":
    main()
