"""§8.1: NeurIPS 2021 award consistency in the calibrated model (out of sample).

Observed (arXiv:2306.03262, Table 1): among the 764 decided duplicated papers (118 of
882 were withdrawn in both copies), the committees accepted 206 and 195; their Spotlight
or Better sets (Orals plus Spotlights; the experiment had no Best Papers tier) of 29 and 25
papers overlapped in 3 papers; the other committee rejected 13 of 29 and 13 of 25 Spotlight
or Better papers, and 13 of 25 and 13 of 23 Spotlights. Columns sob_*: Spotlight or Better. Every variant of §3.5 is calibrated to the accept-level disagreement only,
so these numbers are a test; the award step's noise is fitted on the pairs' scores (scripts/fit_award_noise.py), not on them.

Writes results/validation_neurips2021.csv.
Usage: uv run python scripts/run_validation_neurips2021.py [--workers 5]
"""

from __future__ import annotations

import argparse
import os
from concurrent.futures import ProcessPoolExecutor

import numpy as np
import pandas as pd

from peerreview.levels import LEVELS, ROOT, calibrated, main_model
from peerreview.model import MAIN_FORM
from peerreview.simulate import stable_seed
from peerreview.validation import replay_tiers

OBS = dict(n=764, accept_rate=(206 + 195) / 2 / 764, tiers1=(4, 25), tiers2=(2, 23), sob_overlap=3,
           spot1_rej2=13, spot2_rej1=13, sob1_rej2=13, sob2_rej1=13)  # sob: Spotlight or Better (Orals plus Spotlights)
# Every variant reviews on the main form (integer 1-10 scores, four reviews per paper), which is the 2021 form.
FORM = MAIN_FORM
VARIANTS = {  # the main model (with and without its award step) and the variants of the robustness section
    "gauss/gauss": main_model(),
    "gauss/gauss/noaward": main_model(sigma_award=0.0),
    "gauss/gauss+shared": main_model(sigma_u=0.5),
    "gauss/t3": main_model(noise="t3"),
    "beta/gauss": main_model(quality="beta"),
    "beta/t3": main_model(quality="beta", noise="t3"),
    "exp/gauss": main_model(quality="exp"),
    "lognormal/gauss": main_model(quality="lognormal"),
    "t3/gauss": main_model(quality="t3"),
    "careless1": main_model(careless=0.01, careless_kind="rave"),
    "careless5": main_model(careless=0.05, careless_kind="rave"),
    "random5": main_model(careless=0.05, careless_kind="random"),
}
CENTRAL_ONLY = ("lognormal/gauss", "t3/gauss", "careless1", "careless5", "random5")  # calibrated at the central level only
# Subsample: the decided-paper equivalent of the 9,122-paper conference (9,122 x 764 / 882).
DESIGNS = {"pool": dict(N_conf=None, reps=20_000), "subsample": dict(N_conf=7902, reps=4000)}


def job(name: str, level: str, design: str) -> dict:
    m = calibrated(VARIANTS[name], level)
    d = DESIGNS[design]
    seed = stable_seed(name, level, design, "neurips2021")
    st = replay_tiers(m, d["reps"], seed, n=OBS["n"], accept_rate=OBS["accept_rate"],
                      tiers1=OBS["tiers1"], tiers2=OBS["tiers2"], N_conf=d["N_conf"])
    ov = st["sob_overlap"]
    spot_share = (st["spot1_rej2"] + st["spot2_rej1"]) / (st["spot1"] + st["spot2"])
    obs_share = (OBS["spot1_rej2"] + OBS["spot2_rej1"]) / sum(t[1] for t in (OBS["tiers1"], OBS["tiers2"]))
    sob_rej = (st["sob1_rej2"] + st["sob2_rej1"]) / (st["sob1"] + st["sob2"])
    obs_sob_rej = (OBS["sob1_rej2"] + OBS["sob2_rej1"]) / sum(sum(t) for t in (OBS["tiers1"], OBS["tiers2"]))
    acc_dis = 1 - st["acc_overlap"] / st["acc1"]
    return dict(
        variant=name, level=level, design=design, sigma_eps=m.sigma_eps, sigma_award=m.sigma_award, R=m.R, reps=d["reps"], seed=seed,
        N_conf=d["N_conf"] or OBS["n"],
        sob_overlap_mean=ov.mean(), sob_overlap_sd=ov.std(), sob_overlap_q05=np.quantile(ov, 0.05), sob_overlap_q50=np.median(ov),
        sob_overlap_q95=np.quantile(ov, 0.95), p_sob_overlap_le_obs=(ov <= OBS["sob_overlap"]).mean(),
        p_sob_overlap_ge_obs=(ov >= OBS["sob_overlap"]).mean(),
        sob_overlap_share_mean=(ov / np.sqrt(st["sob1"] * st["sob2"])).mean(),
        spot_rej_share_mean=spot_share.mean(), spot_rej_share_q05=np.quantile(spot_share, 0.05),
        spot_rej_share_q95=np.quantile(spot_share, 0.95), obs_spot_rej_share=obs_share,
        p_spot_rej_ge_obs=(spot_share >= obs_share - 1e-12).mean(),
        p_spot_rej_le_obs=(spot_share <= obs_share + 1e-12).mean(),
        sob_rej_share_mean=sob_rej.mean(), sob_rej_share_q05=np.quantile(sob_rej, 0.05),
        sob_rej_share_q95=np.quantile(sob_rej, 0.95), obs_sob_rej_share=obs_sob_rej,
        p_sob_rej_ge_obs=(sob_rej >= obs_sob_rej - 1e-12).mean(), acc_dis_mean=acc_dis.mean(),
        sob1_mean=st["sob1"].mean(), sob2_mean=st["sob2"].mean(),
    )


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=5)
    ap.add_argument("--levels", default="", help="comma-separated levels to re-run; merged into the existing table")
    args = ap.parse_args()
    levels = tuple(x for x in args.levels.split(",") if x) or tuple(LEVELS)
    jobs = [(v, lev, d) for v in VARIANTS for lev in levels for d in DESIGNS if not (v in CENTRAL_ONLY and lev != "central")]
    with ProcessPoolExecutor(max_workers=args.workers) as ex:
        rows = list(ex.map(job, *zip(*jobs)))
    df = pd.DataFrame(rows)
    out = os.path.join(ROOT, "results", "validation_neurips2021.csv")
    if args.levels and os.path.exists(out):
        old = pd.read_csv(out)
        df = pd.concat([old[~old.level.isin(levels)], df], ignore_index=True)
    df.to_csv(out, index=False)
    cols = ["variant", "level", "design", "sob_overlap_mean", "sob_overlap_q05", "sob_overlap_q95", "p_sob_overlap_le_obs",
            "spot_rej_share_mean", "p_spot_rej_ge_obs", "sob_rej_share_mean", "p_sob_rej_ge_obs", "acc_dis_mean"]
    print(df[cols].round(3).to_string(index=False))


if __name__ == "__main__":
    main()
