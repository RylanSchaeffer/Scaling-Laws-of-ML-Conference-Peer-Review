"""Where a second review would place the Best Papers under each model variant, at the NeurIPS 2014
and 2026 conferences (their submissions, acceptance rates, oral and spotlight counts), on the main
review form (integer 1-10 scores, four reviews per paper; other forms: scripts/run_scale_impact.py).

The model's Best Papers are the first three papers of the award ordering (score plus chair noise within the accepted set).
For each variant the script simulates whole conferences, each reviewed twice, and records where the second
review gives the first review's Best Papers each separate tier (p2_best, p2_oral, p2_spot, p2_accept, p2_reject)
and each "or Better" set (p2_*_or_better), and the same for their true rank (p_*).

Variants change one thing about the Gaussian model: the quality distribution (bounded, exponential,
lognormal, t3), the reviewer noise (t3), shared paper-level noise, or a share of careless reviews
("rave" = the top score, "random" = a random point).
Every variant is recalibrated at the central level (results/calibration_variants.csv).

Each variant also replays the NeurIPS 2021 award decisions (validation.replay_tiers, the 764-paper decided
set within a 7,902-paper conference): sob_overlap2021_* is the overlap of the two committees' Spotlight or Better sets.

Writes results/best_paper_robustness.csv.
Usage: uv run python scripts/run_best_paper_robustness.py [--workers 2]
"""

from __future__ import annotations

import argparse
import os
from concurrent.futures import ProcessPoolExecutor

import pandas as pd

from peerreview.levels import ROOT, calibrated, main_model
from peerreview.model import ReviewModel
from peerreview.simulate import simulate_best_paper, stable_seed
from peerreview.tiers import CUTS, add_separate, cuts
from peerreview.validation import replay_tiers
from run_best_paper import N_BEST

VARIANTS = {  # name: (group, changes to the year's real review form)
    "Gaussian": ("main", {}),
    "bounded quality": ("quality", dict(quality="beta")),
    "exponential quality": ("quality", dict(quality="exp")),
    "lognormal quality": ("quality", dict(quality="lognormal")),
    "$t_3$ quality": ("quality", dict(quality="t3")),
    "$t_3$ noise": ("noise", dict(noise="t3")),
    "shared noise": ("noise", dict(sigma_u=0.5)),
    "1% rave reviews": ("careless", dict(careless=0.01, careless_kind="rave")),
    "5% rave reviews": ("careless", dict(careless=0.05, careless_kind="rave")),
    "5% random reviews": ("careless", dict(careless=0.05, careless_kind="random")),
}


def form_model(year: int, changes: dict) -> ReviewModel:
    """The main model (integer 1-10 scores, four reviews per paper, the fitted award step) with the variant's changes."""
    return main_model(**changes)


REPS = {2014: 200_000, 2026: 40_000}
OVERLAP_REPS, OBS_OVERLAP = 4000, 3


def job(name: str, year: int) -> dict:
    group, changes = VARIANTS[name]
    m = calibrated(form_model(year, changes), "central")
    v = pd.read_csv(os.path.join(ROOT, "data", "venues.csv"))
    x = v[(v.venue == "NeurIPS") & (v.year == year) & (v.denominator != "decided")].iloc[0]
    N, A, n_oral_or_better = int(x.N_used), int(round(x.N_used * x.acc_rate_used)), int(x.orals_used)
    sp = pd.read_csv(os.path.join(ROOT, "data", "spotlights.csv"))
    spotlights = int(sp[(sp.venue == "NeurIPS") & (sp.year == year)].spotlights.iloc[0])
    cut_sizes = cuts(N_BEST, n_oral_or_better, spotlights, A)
    r = simulate_best_paper(m, N, REPS[year], best_K=(1,), best_papers_cuts=cut_sizes, second_committee=True,
                            salt=f"best-paper-robustness-{name}", n_best=N_BEST)
    out = {"variant": name, "group": group, "year": year, "N": N, "accepted": A, "n_oral_or_better": n_oral_or_better,
           "spotlights": spotlights, "level": "central",
           "R": m.R, "scale": m.scale, "sigma_eps": m.sigma_eps, "reps": r["reps"], "seed": r["seed"],
           "best_papers_rank_median": r["best_papers_rank_median"], "best_papers_rank2_median": r["best_papers_rank2_median"], "wall_s": r["wall_s"]}
    for c in CUTS:  # "or Better" probabilities; the Best Papers are their own
        out[f"p_{c}"], out[f"p_{c}_se"] = r[f"best_papers_in_{c}"], r[f"best_papers_in_{c}_se"]
        out[f"p2_{c}"], out[f"p2_{c}_se"] = r[f"best_papers_in2_{c}"], r[f"best_papers_in2_{c}_se"]
    add_separate(out, "p")  # the separate tiers
    add_separate(out, "p2")
    return out

def overlap_job(name: str) -> dict:
    m = calibrated(form_model(2021, VARIANTS[name][1]), "central")  # the replay is of NeurIPS 2021, on its form
    seed = stable_seed(name, "best-paper-robustness-overlap2021")
    st = replay_tiers(m, OVERLAP_REPS, seed, n=764, accept_rate=(206 + 195) / 2 / 764, counts1=(4, 25),
                      counts2=(2, 23), N_conf=7902)
    ov = st["sob_overlap"]  # the two committees' Spotlight or Better sets
    return {"variant": name, "sob_overlap2021_mean": ov.mean(), "sob_overlap2021_q05": float(pd.Series(ov).quantile(0.05)),
            "sob_overlap2021_q95": float(pd.Series(ov).quantile(0.95)), "p_sob_overlap2021_le_obs": (ov <= OBS_OVERLAP).mean(),
            "sob_overlap2021_reps": OVERLAP_REPS, "sob_overlap2021_seed": seed}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=2)
    args = ap.parse_args()
    jobs = [(n, y) for n in VARIANTS for y in REPS]
    with ProcessPoolExecutor(max_workers=args.workers) as ex:
        ov = ex.map(overlap_job, list(VARIANTS))
        df = pd.DataFrame(list(ex.map(job, *zip(*jobs))))
        df = df.merge(pd.DataFrame(list(ov)), on="variant")
    out = os.path.join(ROOT, "results", "best_paper_robustness.csv")
    df.to_csv(out, index=False)
    print(df[["variant", "year", "p2_best", "p2_oral", "p2_spot", "p2_accept", "p2_reject", "p2_reject_se", "best_papers_rank2_median",
              "p_best", "p_reject", "sob_overlap2021_mean", "p_sob_overlap2021_le_obs"]]
          .round(4).to_string(index=False))


if __name__ == "__main__":
    main()
