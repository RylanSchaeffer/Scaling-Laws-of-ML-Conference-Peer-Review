"""Fit the chair-level award noise sigma_award on the NeurIPS 2021 pairs' real scores.

The model gives awards (orals and spotlights) to the top-K papers of the award ordering, the mean score
plus a chair noise eta ~ N(0, sigma_award^2), within the accepted set. On the real scores of the 301
public pairs (data/paired_reviews/neurips2021/copies.csv) the award ordering can be simulated directly:
each committee's accepted copies, its mean ratings, its own number of awards K. The statistic that
identifies sigma_award is how many of a committee's K awards lie inside its top-K by mean rating alone.
Observed: of the 53 award copies, 26 are inside their committee's score top-K (ties among equal means
broken at random, averaged). The fit is the sigma_award at which the simulated award set overlaps the
score top-K by the same number (bisection, common random numbers). The two statistics the model is
then tested on are held out: the number of award papers shared by the two committees (observed 3) and
the number rejected by the other committee (observed 25 of 53); the script reports both on the real
scores at the fitted value and at zero.

Uncertainty: the fit is repeated on bootstrap resamples of the pairs (90% range).

Writes results/award_noise.json and results/award_noise_fit.csv (the statistics on a sigma grid).
Usage: uv run python scripts/fit_award_noise.py [--reps 20000] [--boot 200]
"""
from __future__ import annotations

import argparse
import csv
import json
import os

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COPIES = os.path.join(ROOT, "data", "paired_reviews", "neurips2021", "copies.csv")
OUT_JSON = os.path.join(ROOT, "results", "award_noise.json")
OUT_CSV = os.path.join(ROOT, "results", "award_noise_fit.csv")


def tier(d: str) -> str:
    d = d.lower()
    return "oral" if "oral" in d else "spot" if "spotlight" in d else "poster" if ("poster" in d or d.startswith("accept")) else "reject"


def load_pairs() -> list[dict]:
    """One record per pair with both copies public: per side the mean rating, the tier and whether accepted."""
    rows = list(csv.DictReader(open(COPIES)))
    by = {}
    for r in rows:
        by.setdefault(r["pair_id"], {})[r["side"]] = dict(m=float(r["mean_rating_final"]), t=tier(r["own_decision"]))
    out = []
    for pid, d in sorted(by.items()):
        if "a" in d and "b" in d:
            out.append(dict(pair_id=pid, **{f"{s}_{k}": d[s][k] for s in "ab" for k in ("m", "t")}))
    return out


class Sides:
    """The two committees' accepted copies on a set of pairs, with common random numbers for the fit."""

    def __init__(self, pairs: list[dict], reps: int, rng: np.random.Generator):
        self.n = len(pairs)
        self.reps = reps
        self.side = {}
        for s in "ab":
            m = np.array([p[f"{s}_m"] for p in pairs])
            acc = np.array([p[f"{s}_t"] != "reject" for p in pairs])
            award = np.array([p[f"{s}_t"] in ("oral", "spot") for p in pairs])
            K = int(award.sum())
            # common random numbers: a tie-breaking jitter for the score ordering and standard normals for eta
            jit = 1e-6 * rng.random((reps, self.n))
            z = rng.standard_normal((reps, self.n))
            self.side[s] = dict(m=m, acc=acc, award=award, K=K, jit=jit, z=z)

    def topk(self, s: str, sigma: float) -> np.ndarray:
        """Boolean (reps, n): the K award papers of the award ordering at sigma within the accepted set."""
        d = self.side[s]
        t = d["m"][None, :] + d["jit"] + sigma * d["z"]
        t = np.where(d["acc"][None, :], t, -np.inf)
        K = d["K"]
        thr = np.partition(t, self.n - K, axis=1)[:, self.n - K][:, None]
        return t >= thr

    def stats(self, sigma: float) -> dict:
        """Expected counts at sigma: awards inside the score top-K, shared awards, awards rejected by the other side."""
        in_score = 0.0
        sets = {}
        for s in "ab":
            sets[s] = self.topk(s, sigma)
            score = self.topk(s, 0.0)
            in_score += (sets[s] & score).sum(1).mean()
        shared = (sets["a"] & sets["b"]).sum(1).mean()
        rej = (sets["a"] & ~self.side["b"]["acc"][None, :]).sum(1).mean() + (sets["b"] & ~self.side["a"]["acc"][None, :]).sum(1).mean()
        return dict(awards_in_score_topK=float(in_score), shared=float(shared), rejected_by_other=float(rej))

    def observed(self) -> dict:
        """The same three counts for the real awards (ties in the score top-K broken at random, averaged)."""
        in_score = 0.0
        for s in "ab":
            in_score += (self.topk(s, 0.0) & self.side[s]["award"][None, :]).sum(1).mean()
        a, b = self.side["a"], self.side["b"]
        return dict(awards_in_score_topK=float(in_score), shared=int((a["award"] & b["award"]).sum()),
                    rejected_by_other=int((a["award"] & ~b["acc"]).sum() + (b["award"] & ~a["acc"]).sum()),
                    K_a=a["K"], K_b=b["K"], awards=a["K"] + b["K"])

    def fit(self, lo: float = 0.0, hi: float = 4.0, tol: float = 1e-3) -> float:
        target = self.observed()["awards_in_score_topK"]
        f = lambda sig: self.stats(sig)["awards_in_score_topK"] - target  # decreasing in sigma
        if f(hi) > 0:
            return float("inf")
        while hi - lo > tol:
            mid = 0.5 * (lo + hi)
            if f(mid) > 0:
                lo = mid
            else:
                hi = mid
        return 0.5 * (lo + hi)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--reps", type=int, default=20_000)
    ap.add_argument("--boot", type=int, default=200)
    ap.add_argument("--seed", type=int, default=20261014)
    args = ap.parse_args()
    pairs = load_pairs()
    rng = np.random.default_rng(args.seed)
    S = Sides(pairs, args.reps, rng)
    obs = S.observed()
    sigma = S.fit()
    grid = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.25, 1.5, 2.0]
    with open(OUT_CSV, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["sigma_award", "awards_in_score_topK", "shared", "rejected_by_other"])
        for g in sorted(set(grid) | {round(sigma, 4)}):
            st = S.stats(g)
            w.writerow([g, round(st["awards_in_score_topK"], 3), round(st["shared"], 3), round(st["rejected_by_other"], 3)])
    boot = []
    brng = np.random.default_rng(args.seed + 1)
    for _ in range(args.boot):
        idx = brng.integers(0, len(pairs), len(pairs))
        Sb = Sides([pairs[i] for i in idx], 2000, brng)
        boot.append(Sb.fit())
    boot = np.array(boot)
    out = dict(
        sigma_award=round(sigma, 3), fit_statistic="awards inside the committee's own score top-K, summed over both committees",
        observed=obs, at_fit=S.stats(sigma), at_zero=S.stats(0.0),
        bootstrap=dict(n=args.boot, q05=float(np.quantile(boot, 0.05)), q50=float(np.median(boot)), q95=float(np.quantile(boot, 0.95)),
                       reps_per_fit=2000),
        n_pairs=len(pairs), fit_reps=args.reps, seed=args.seed, source=os.path.relpath(COPIES, ROOT),
        note="sigma_award on the 1-10 rating axis; awards = oral or spotlight by that committee; accepted = own decision not reject",
    )
    json.dump(out, open(OUT_JSON, "w"), indent=1)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
