"""How sure are the Best Paper probabilities? The same tiers as make_best_paper.py, under every
variant that fits the acceptance data equally well (each refitted to the central NeurIPS 2021
disagreement), at NeurIPS 2014 and 2026 size.

The model's Best Paper is the top-scored paper (ties broken at random). For each variant the
script simulates whole conferences, each reviewed by two independent reviews, and records
two things about the first review's Best Paper. The rerun framing the paper reports (p2_*): the
probability that the second review ranks it in its top M, for M = 1 (the Best Paper again), 10, the oral
count and the accepted count; one minus the last is the probability that a second review
rejects it. The true-rank framing (p_*): the probability that it is truly in the top M.

Variants: Gaussian (the main model); quality bounded, exponential, lognormal or heavy-tailed
(t3), R = 3; reviews on a 1-10 or ICLR scale, R = 4; heavy-tailed (t3) reviewer noise on a
1-10 scale; and 1% or 5% "rave" reviews (always 10) or 5% random reviews on a 1-10 scale.

Each variant also replays the NeurIPS 2021 top tier (validation.replay_tiers, the 764-paper
subsample design of run_validation_neurips2021.py): the overlap of the two committees'
oral-plus-spotlight tiers, observed 3. This is the one data set that reaches the top of the
ranking, so it tests the quality tails that acceptance data cannot see.

Writes results/best_paper_robustness.csv.
Usage: uv run python scripts/run_best_paper_robustness.py [--workers 5]
"""

from __future__ import annotations

import argparse
import os
from concurrent.futures import ProcessPoolExecutor

import pandas as pd

from peerreview.levels import ROOT, calibrated
from peerreview.model import ReviewModel
from peerreview.simulate import simulate_best_paper, stable_seed
from peerreview.validation import replay_tiers

VARIANTS = {  # name: (group, model)
    "Gaussian": ("main", ReviewModel(R=4)),
    "bounded quality": ("quality", ReviewModel(R=3, quality="beta")),
    "exponential quality": ("quality", ReviewModel(R=3, quality="exp")),
    "lognormal quality": ("quality", ReviewModel(R=3, quality="lognormal")),
    "$t_3$ quality": ("quality", ReviewModel(R=3, quality="t3")),
    "1-10 scale": ("scale", ReviewModel(R=4, scale="int10")),
    "ICLR scale": ("scale", ReviewModel(R=4, scale="iclr6")),
    "$t_3$ noise, 1-10": ("noise", ReviewModel(R=4, noise="t3", scale="int10")),
    "1% rave reviews": ("careless", ReviewModel(R=4, scale="int10", careless=0.01, careless_kind="rave")),
    "5% rave reviews": ("careless", ReviewModel(R=4, scale="int10", careless=0.05, careless_kind="rave")),
    "5% random reviews": ("careless", ReviewModel(R=4, scale="int10", careless=0.05, careless_kind="random")),
}
REPS = {2014: 200_000, 2026: 40_000}
OVERLAP_REPS, OBS_OVERLAP = 4000, 3


def job(name: str, year: int) -> dict:
    group, m0 = VARIANTS[name]
    m = calibrated(m0, "central")
    v = pd.read_csv(os.path.join(ROOT, "data", "venues.csv"))
    x = v[(v.venue == "NeurIPS") & (v.year == year) & (v.denominator != "decided")].iloc[0]
    N, A, orals = int(x.N_used), int(round(x.N_used * x.acc_rate_used)), int(x.orals_used)
    sp = pd.read_csv(os.path.join(ROOT, "data", "spotlights.csv"))
    spotlights = int(sp[(sp.venue == "NeurIPS") & (sp.year == year)].spotlights.iloc[0])
    tiers = {"best": 1, "top10": 10, "oral": orals, "spot": orals + spotlights, "accept": A}  # nested tiers
    r = simulate_best_paper(m, N, REPS[year], best_K=(1,), winner_tiers=tiers, second_committee=True,
                            salt=f"best-paper-robustness-{name}")
    return {"variant": name, "group": group, "year": year, "N": N, "accepted": A, "orals": orals,
            "spotlights": spotlights, "level": "central",
            "R": m.R, "sigma_eps": m.sigma_eps, "reps": r["reps"], "seed": r["seed"],
            "p_best": r["winner_in_best"], "p_top10": r["winner_in_top10"], "p_oral": r["winner_in_oral"],
            "p_spot": r["winner_in_spot"],
            "p_accept": r["winner_in_accept"], "p_reject": 1 - r["winner_in_accept"],
            "p_reject_se": r["winner_in_accept_se"], "p_best_se": r["winner_in_best_se"],
            "winner_rank_median": r["winner_rank_median"],
            "p2_best": r["winner_in2_best"], "p2_top10": r["winner_in2_top10"], "p2_oral": r["winner_in2_oral"],
            "p2_spot": r["winner_in2_spot"],
            "p2_accept": r["winner_in2_accept"], "p2_reject": 1 - r["winner_in2_accept"],
            "p2_reject_se": r["winner_in2_accept_se"], "p2_best_se": r["winner_in2_best_se"],
            "winner_rank2_median": r["winner_rank2_median"], "wall_s": r["wall_s"]}


def overlap_job(name: str) -> dict:
    m = calibrated(VARIANTS[name][1], "central")
    seed = stable_seed(name, "best-paper-robustness-overlap2021")
    st = replay_tiers(m, OVERLAP_REPS, seed, n=764, accept_rate=(206 + 195) / 2 / 764, tiers1=(4, 25),
                      tiers2=(2, 23), N_conf=7902)
    ov = st["overlap"]
    return {"variant": name, "overlap2021_mean": ov.mean(), "overlap2021_q05": float(pd.Series(ov).quantile(0.05)),
            "overlap2021_q95": float(pd.Series(ov).quantile(0.95)), "p_overlap2021_le_obs": (ov <= OBS_OVERLAP).mean(),
            "overlap2021_reps": OVERLAP_REPS, "overlap2021_seed": seed}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=5)
    args = ap.parse_args()
    jobs = [(n, y) for n in VARIANTS for y in REPS]
    with ProcessPoolExecutor(max_workers=args.workers) as ex:
        ov = ex.map(overlap_job, list(VARIANTS))
        df = pd.DataFrame(list(ex.map(job, *zip(*jobs))))
        df = df.merge(pd.DataFrame(list(ov)), on="variant")
    out = os.path.join(ROOT, "results", "best_paper_robustness.csv")
    df.to_csv(out, index=False)
    print(df[["variant", "year", "p2_best", "p2_top10", "p2_oral", "p2_spot", "p2_reject", "p2_reject_se", "winner_rank2_median",
              "p_best", "p_reject", "overlap2021_mean", "p_overlap2021_le_obs"]]
          .round(4).to_string(index=False))


if __name__ == "__main__":
    main()
