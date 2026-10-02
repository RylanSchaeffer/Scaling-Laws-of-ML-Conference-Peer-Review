"""§8.1: NeurIPS 2021 top-tier consistency in the calibrated model (out of sample).

Observed (arXiv:2306.03262, Table 1): among the 764 decided duplicated papers (118 of
882 were withdrawn in both copies), the committees accepted 206 and 195; their top
tiers (oral + spotlight) of 29 and 25 papers overlapped in 3 papers; the other
committee rejected 13 of 29 and 13 of 25 top-tier papers, and 13 of 25 and 13 of 23
spotlights. Every variant of §3.5 is calibrated to the accept-level disagreement only,
so these numbers are a test.

Writes results/validation_neurips2021.csv.
Usage: uv run python scripts/run_validation_neurips2021.py [--workers 5]
"""

from __future__ import annotations

import argparse
import os
from concurrent.futures import ProcessPoolExecutor

import numpy as np
import pandas as pd

from peerreview.levels import LEVELS, ROOT, calibrated
from peerreview.model import ReviewModel
from peerreview.simulate import stable_seed
from peerreview.validation import replay_tiers

OBS = dict(n=764, accept_rate=(206 + 195) / 2 / 764, tiers1=(4, 25), tiers2=(2, 23), overlap=3,
           spot1_rej2=13, spot2_rej1=13, top1_rej2=13, top2_rej1=13)
VARIANTS = {
    "gauss/gauss": ReviewModel(R=4),
    "gauss/gauss+shared": ReviewModel(R=4, sigma_u=0.5),
    "gauss/t3": ReviewModel(R=4, noise="t3"),
    "beta/gauss": ReviewModel(R=4, quality="beta"),
    "beta/t3": ReviewModel(R=4, quality="beta", noise="t3"),
    "exp/gauss": ReviewModel(R=4, quality="exp"),
}
# Subsample: the decided-paper equivalent of the 9,122-paper conference (9,122 x 764 / 882).
DESIGNS = {"pool": dict(N_conf=None, reps=20_000), "subsample": dict(N_conf=7902, reps=4000)}


def job(name: str, level: str, design: str) -> dict:
    m = calibrated(VARIANTS[name], level)
    d = DESIGNS[design]
    seed = stable_seed(name, level, design, "neurips2021")
    st = replay_tiers(m, d["reps"], seed, n=OBS["n"], accept_rate=OBS["accept_rate"],
                      tiers1=OBS["tiers1"], tiers2=OBS["tiers2"], N_conf=d["N_conf"])
    ov = st["overlap"]
    spot_share = (st["spot1_rej2"] + st["spot2_rej1"]) / (st["spot1"] + st["spot2"])
    obs_share = (OBS["spot1_rej2"] + OBS["spot2_rej1"]) / sum(t[1] for t in (OBS["tiers1"], OBS["tiers2"]))
    top_rej = (st["top1_rej2"] + st["top2_rej1"]) / (st["top1"] + st["top2"])
    obs_top_rej = (OBS["top1_rej2"] + OBS["top2_rej1"]) / sum(sum(t) for t in (OBS["tiers1"], OBS["tiers2"]))
    acc_dis = 1 - st["acc_overlap"] / st["acc1"]
    return dict(
        variant=name, level=level, design=design, sigma_eps=m.sigma_eps, R=m.R, reps=d["reps"], seed=seed,
        N_conf=d["N_conf"] or OBS["n"],
        overlap_mean=ov.mean(), overlap_sd=ov.std(), overlap_q05=np.quantile(ov, 0.05), overlap_q50=np.median(ov),
        overlap_q95=np.quantile(ov, 0.95), p_overlap_le_obs=(ov <= OBS["overlap"]).mean(),
        p_overlap_ge_obs=(ov >= OBS["overlap"]).mean(),
        overlap_share_mean=(ov / np.sqrt(st["top1"] * st["top2"])).mean(),
        spot_rej_share_mean=spot_share.mean(), spot_rej_share_q05=np.quantile(spot_share, 0.05),
        spot_rej_share_q95=np.quantile(spot_share, 0.95), obs_spot_rej_share=obs_share,
        p_spot_rej_ge_obs=(spot_share >= obs_share - 1e-12).mean(),
        p_spot_rej_le_obs=(spot_share <= obs_share + 1e-12).mean(),
        top_rej_share_mean=top_rej.mean(), top_rej_share_q05=np.quantile(top_rej, 0.05),
        top_rej_share_q95=np.quantile(top_rej, 0.95), obs_top_rej_share=obs_top_rej,
        p_top_rej_ge_obs=(top_rej >= obs_top_rej - 1e-12).mean(), acc_dis_mean=acc_dis.mean(),
        top1_mean=st["top1"].mean(), top2_mean=st["top2"].mean(),
    )


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=5)
    args = ap.parse_args()
    jobs = [(v, lev, d) for v in VARIANTS for lev in LEVELS for d in DESIGNS]
    with ProcessPoolExecutor(max_workers=args.workers) as ex:
        rows = list(ex.map(job, *zip(*jobs)))
    df = pd.DataFrame(rows)
    out = os.path.join(ROOT, "results", "validation_neurips2021.csv")
    df.to_csv(out, index=False)
    cols = ["variant", "level", "design", "overlap_mean", "overlap_q05", "overlap_q95", "p_overlap_le_obs",
            "spot_rej_share_mean", "p_spot_rej_ge_obs", "top_rej_share_mean", "p_top_rej_ge_obs", "acc_dis_mean"]
    print(df[cols].round(3).to_string(index=False))


if __name__ == "__main__":
    main()
