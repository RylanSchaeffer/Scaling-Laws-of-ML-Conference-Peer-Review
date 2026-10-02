"""§8.2 model side: the ICLR split-half replay in the model, year by year.

For each year with an observed split-half replay (results/iclr_splithalf_observed.csv):
two committees of R = 2 reviews on that year's score scale, random tie-breaking,
N = the number of kept papers, acceptance at the kept set's observed rate, and
sigma_eps chosen by bisection so that the model's correlation between the two
committees' mean scores equals the observed correlation of the two half means.
The model's accept-level precision, inconsistency share and top-10 / top-30
overlaps are then compared with the observed values (not used in the fit).

Quality placement: mean and between-paper SD of the year's individual scores
(results/iclr_variance.csv); a second run uses the default mu_q = 5, sigma_q = 1.2.

Writes results/validation_iclr.csv.
Usage: uv run python scripts/run_validation_iclr.py [--workers 5]
"""

from __future__ import annotations

import argparse
import os
from concurrent.futures import ProcessPoolExecutor

import pandas as pd

from peerreview.calibrate import calibrate_sigma_eps
from peerreview.levels import ROOT
from peerreview.model import ReviewModel
from peerreview.simulate import Selections, simulate, stable_seed

SCALE_POINTS = {
    "1-10": ("int10", ()),
    "1/3/5/6/8/10": ("iclr6", ()),
    "1/3/6/8": ("iclr4", ()),
    "0/2/4/6/8/10": ("custom", (0.0, 2.0, 4.0, 6.0, 8.0, 10.0)),
}


def job(row: dict, placement: str) -> dict:
    scale, pts = SCALE_POINTS[row["scale"]]
    if placement == "observed":
        mu, sd = row["mean_score"], row["sd_between"]
    else:
        mu, sd = 5.0, 1.2
    m = ReviewModel(R=2, scale=scale, scale_points=pts, mu_q=float(mu), sigma_q=float(sd))
    N = int(row["n_kept"])
    alpha = int(row["A"]) / N
    seed = stable_seed(int(row["year"]), placement, "iclr-calibration")
    cal = calibrate_sigma_eps(m, float(row["corr_halves_mean"]), alpha=alpha, metric="corr_s12", N=N, reps=2000,
                              seed=seed, lo=0.02, hi=12.0, tol=5e-4)
    m = m.replace(sigma_eps=cal["sigma_eps"])
    sel = Selections(fixed_K=(10, 30), pct=(), alphas=(alpha,), best_K=(1,), alpha_ref=alpha)
    sim = simulate(m, N, reps=4000, sel=sel, salt=f"iclr-{row['year']}-{placement}")
    a = f"acc{alpha:.2f}"
    return dict(
        year=int(row["year"]), scale=row["scale"], in_main=bool(row["in_main"]), placement=placement,
        mu_q=m.mu_q, sigma_q=m.sigma_q, N=N, A=int(row["A"]), alpha=alpha, sigma_eps=m.sigma_eps,
        cal_converged=cal["converged"], seed=sim["seed"], reps=sim["reps"],
        obs_corr=row["corr_halves_mean"], model_corr=sim["corr_s12"],
        obs_incons=row["inconsistent_mean"], model_incons=sim[f"incons_{a}"], model_incons_se=sim[f"incons_{a}_se"],
        obs_precision=row["precision_mean"], model_precision=sim[f"ovl_{a}"], model_precision_se=sim[f"ovl_{a}_se"],
        obs_top10=row["ovl_top10_mean"], obs_top10_sd=row["ovl_top10_sd"],
        model_top10=sim["ovl_K10"], model_top10_se=sim["ovl_K10_se"],
        obs_top30=row["ovl_top30_mean"], obs_top30_sd=row["ovl_top30_sd"],
        model_top30=sim["ovl_K30"], model_top30_se=sim["ovl_K30_se"],
        model_rho2=sim["corr_qs"] ** 2, model_prec_true_acc=sim[f"prec_{a}"], model_prec_true_K10=sim["prec_K10"],
    )


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=5)
    args = ap.parse_args()
    obs = pd.read_csv(os.path.join(ROOT, "results", "iclr_splithalf_observed.csv"))
    var = pd.read_csv(os.path.join(ROOT, "results", "iclr_variance.csv"))[["year", "mean_score", "sd_between"]]
    obs = obs.merge(var, on="year")
    jobs = [(r, p) for r in obs.to_dict("records") for p in ("observed", "default")]
    with ProcessPoolExecutor(max_workers=args.workers) as ex:
        rows = list(ex.map(job, *zip(*jobs)))
    df = pd.DataFrame(rows).sort_values(["placement", "year"])
    df.to_csv(os.path.join(ROOT, "results", "validation_iclr.csv"), index=False)
    cols = ["year", "placement", "sigma_eps", "obs_corr", "model_corr", "obs_incons", "model_incons", "obs_precision",
            "model_precision", "obs_top10", "model_top10", "obs_top30", "model_top30"]
    print(df[cols].round(3).to_string(index=False))


if __name__ == "__main__":
    main()
