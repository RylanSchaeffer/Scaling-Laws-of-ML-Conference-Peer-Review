"""Why did NeurIPS 2021 committees reject 54% of each other's spotlights, against 31% in the model?

At NeurIPS 2021 each committee rejected the other's spotlights (26 of 48, 54%) about as
often as its posters (177 of 347, 51%), and none of the 6 orals. Three analyses test the
candidate causes.

A  NeurIPS 2021 replay (validation.replay_tiers, the paper's 764-paper subsample of a
   7,902-paper conference, Gaussian quality and noise, R = 4):
     score_only  tiers by score at a grid of reliabilities rho^2 (lower reliability);
     own         tiers among accepted papers by score + own * sd(s) * e, e drawn afresh
                 per committee (a judgement the two committees do not share); own = inf
                 picks the tiers at random among accepted papers;
     shared      tiers by score + shared * sd(s) * h, h common to both committees (a
                 property both see, such as broad interest);
     both        shared and own together;
     own_spot    as own, but the orals follow the score and only the spotlights use the
                 committee's own judgement (all 6 orals were accepted by the other committee);
     shared_spot as shared, with the orals following the score;
     both_spot   shared and own together, with the orals following the score.
   score_share is the share of the tier index's variance among accepted papers that the
   score explains.
B  ICLR (main track, decided papers): how closely real orals and spotlights follow the mean
   rating, against acceptance. A paper's committee score is its mean rating plus AC noise
   sig_a, fitted to the precision of acceptance by mean rating; then own is fitted to the
   precision of the top tier by mean rating among accepted papers. Ties in the mean rating
   count as noise, so own is if anything too large. 2026 scores are pre-discussion
   (see iclr.py) and 2017 to 2019 have orals only.
C  ICLR split halves: decided main-track papers (as in the paper's other split-half test
   and the NeurIPS 2021 decided set) with at least 4 reviews, 4 of them drawn at random, split
   2 and 2. Half A takes its top 3.5% (the NeurIPS 2021 oral-plus-spotlight share) and
   accepts 26.2%; half B accepts its own 26.2%. The share of A's top tier and of A's other
   accepts that B rejects is compared with an ordinal Gaussian null: Gaussian quality and
   noise, cut to that year's rating values at their observed frequencies, with the same
   ties and tie-breaks, and the per-review reliability fitted to the observed accept-level
   disagreement.

Writes results/highlight_process_neurips2021.csv, results/iclr_highlight_scores.csv and
results/iclr_splithalf_top.csv.
Usage: uv run python scripts/run_highlight_process.py [--workers 5]
"""

from __future__ import annotations

import argparse
import os
from concurrent.futures import ProcessPoolExecutor

import numpy as np
import pandas as pd
from scipy.optimize import brentq
from scipy.stats import norm, rankdata

from peerreview import analytic as an
from peerreview import iclr
from peerreview.levels import LEVELS, ROOT
from peerreview.model import ReviewModel
from peerreview.simulate import stable_seed
from peerreview.validation import replay_tiers

# As in run_validation_neurips2021.py (arXiv:2306.03262, Table 1).
OBS = dict(n=764, accept_rate=(206 + 195) / 2 / 764, tiers1=(4, 25), tiers2=(2, 23), N_conf=7902, reps=4000,
           overlap=3, spot_rej=26 / 48, post_rej=177 / 347, oral_rej=0 / 6, acc_dis=(107 + 96) / (206 + 195))
RHO2_GRID = (0.15, 0.20, 0.25, 0.30, 0.35, 0.40)
OWN_GRID = (0.0, 0.25, 0.5, 0.75, 1.0, 1.5, 2.0, 3.0, np.inf)
SHARED_GRID = (0.5, 1.0, 2.0, 4.0)
BOTH_GRID = ((1.0, 1.0), (2.0, 2.0))

ICLR_TOP, ICLR_ALPHA, SPLITS = 0.035, 0.262, 60


# ---------------------------------------------------------------------------
# A  NeurIPS 2021 replay
# ---------------------------------------------------------------------------


def replay_job(kind: str, level: str, rho2: float, shared: float, own: float) -> dict:
    orals_by_score = kind.endswith("_spot")
    m = ReviewModel(R=4, sigma_eps=float(an.sigma_eps_for_rho2(rho2, 4, 1.2, 0.0)))
    seed = stable_seed(kind, level, round(rho2, 6), shared, str(own), "highlight-process")
    st = replay_tiers(m, OBS["reps"], seed, n=OBS["n"], accept_rate=OBS["accept_rate"], tiers1=OBS["tiers1"],
                      tiers2=OBS["tiers2"], N_conf=OBS["N_conf"], shared=shared, own=own,
                      orals_by_score=orals_by_score)
    with np.errstate(invalid="ignore", divide="ignore"):
        spot = (st["spot1_rej2"] + st["spot2_rej1"]) / (st["spot1"] + st["spot2"])
    ov = st["overlap"]
    oral_n, oral_rej = st["oral1"] + st["oral2"], st["oral1_rej2"] + st["oral2_rej1"]
    post_n, post_rej = st["post1"] + st["post2"], st["post1_rej2"] + st["post2_rej1"]
    hi_spot = spot >= OBS["spot_rej"] - 1e-12
    lo_ov = ov <= OBS["overlap"]
    return dict(
        kind=kind, level=level, rho2=rho2, shared=shared, own=own, reps=OBS["reps"], seed=seed,
        sigma_eps=m.sigma_eps, score_share=st["score_share"].mean(),
        overlap_mean=ov.mean(), overlap_q05=np.quantile(ov, 0.05), overlap_q95=np.quantile(ov, 0.95),
        p_overlap_le_obs=lo_ov.mean(),
        spot_rej_mean=np.nanmean(spot), spot_rej_q05=np.nanquantile(spot, 0.05), spot_rej_q95=np.nanquantile(spot, 0.95),
        p_spot_rej_ge_obs=hi_spot.mean(), p_joint=(hi_spot & lo_ov).mean(),
        post_rej_mean=post_rej.sum() / post_n.sum(), oral_rej_mean=oral_rej.sum() / oral_n.sum(),
        p_no_oral_rejected=(oral_rej[oral_n == 6] == 0).mean(),  # observed: 0 of exactly 6
        acc_dis_mean=(1 - st["acc_overlap"] / st["acc1"]).mean(),
        obs_overlap=OBS["overlap"], obs_spot_rej=OBS["spot_rej"], obs_post_rej=OBS["post_rej"],
        obs_oral_rej=OBS["oral_rej"], obs_acc_dis=OBS["acc_dis"],
    )


def replay_jobs() -> list[tuple]:
    jobs = [("score_only", "", r2, 0.0, 0.0) for r2 in RHO2_GRID]
    for level, r2 in LEVELS.items():
        jobs += [("own", level, r2, 0.0, o) for o in OWN_GRID]
    c = LEVELS["central"]
    jobs += [("shared", "central", c, s, 0.0) for s in SHARED_GRID]
    jobs += [("both", "central", c, s, o) for s, o in BOTH_GRID]
    for level in ("pessimistic", "central"):
        jobs += [("own_spot", level, LEVELS[level], 0.0, o) for o in OWN_GRID if o > 0]
    jobs += [("shared_spot", "central", c, s, 0.0) for s in SHARED_GRID]
    jobs += [("both_spot", "central", c, s, o) for s, o in BOTH_GRID]
    return jobs


# ---------------------------------------------------------------------------
# B  ICLR: highlights against the mean rating
# ---------------------------------------------------------------------------


def expected_precision(score: np.ndarray, label: np.ndarray, k: int) -> float:
    """Expected share of labelled items among the k highest scores, ties broken at random."""
    order = np.argsort(-score, kind="stable")
    thr = score[order[k - 1]]
    above = score > thr
    tied = score == thr
    return (label[above].sum() + (k - above.sum()) * label[tied].mean()) / k


def auc(score: np.ndarray, label: np.ndarray) -> float:
    rk = rankdata(score)
    n1, n0 = label.sum(), (~label).sum()
    return float((rk[label].sum() - n1 * (n1 + 1) / 2) / (n1 * n0))


def model_precision(sig_a: float, own: float, alpha: float, top_frac: float, seed: int,
                    n: int = 20_000, reps: int = 20) -> tuple[float, float, float]:
    """m = mean rating (continuous), s = m + sig_a * a, accept the top alpha by s, tiers among
    accepts by s + own * sd(s) * e. Returns the precision of acceptance by m, the precision of
    the tier by m among accepts, and the score share of the tier index among accepts.
    Common random numbers (fixed seed) keep the fits smooth."""
    rng = np.random.default_rng(seed)
    pa, pt, sh = [], [], []
    A = int(round(alpha * n))
    T = max(1, int(round(top_frac * A)))
    for _ in range(reps):
        m = rng.standard_normal(n)
        s = m + sig_a * rng.standard_normal(n)
        e = rng.standard_normal(A)
        acc = np.zeros(n, bool)
        acc[np.argsort(-s)[:A]] = True
        pa.append(acc[np.argsort(-m)[:A]].mean())
        sa, ma = s[acc], m[acc]
        t = sa + own * s.std() * e
        top = np.zeros(A, bool)
        top[np.argsort(-t)[:T]] = True
        pt.append(top[np.argsort(-ma)[:T]].mean())
        sh.append(np.var(sa) / np.var(t))
    return float(np.mean(pa)), float(np.mean(pt)), float(np.mean(sh))


def _ratings(df: pd.DataFrame) -> pd.Series:
    return df.ratings.fillna("").astype(str).apply(lambda s: [float(x) for x in s.split(";") if x != ""])


def iclr_highlight_job(year: int, m: np.ndarray, acc: np.ndarray, top: np.ndarray) -> dict:
    A, T = int(acc.sum()), int(top.sum())
    alpha, top_frac = A / len(m), T / A
    acc_prec = expected_precision(m, acc, A)
    top_prec = expected_precision(m[acc], top[acc], T)
    seed = stable_seed(year, "iclr-highlight-fit")

    def f_a(sa):
        return model_precision(sa, 0.0, alpha, top_frac, seed, reps=8)[0] - acc_prec
    sig_a = brentq(f_a, 0.0, 4.0, xtol=1e-3) if f_a(0.0) > 0 else 0.0
    _, top_prec_score_only, _ = model_precision(sig_a, 0.0, alpha, top_frac, seed)

    def f_t(o):
        return model_precision(sig_a, o, alpha, top_frac, seed, reps=8)[1] - top_prec
    at_bound = f_t(0.0) <= 0
    own = 0.0 if at_bound else brentq(f_t, 0.0, 20.0, xtol=1e-3)
    _, _, share = model_precision(sig_a, own, alpha, top_frac, seed)
    return dict(year=year, n=len(m), A=A, T=T, alpha=alpha, top_frac=top_frac,
                top_tiers="oral" if year <= 2019 or year == 2026 else "oral+spotlight",
                scores="pre-discussion" if year == 2026 else "final",
                acc_prec=acc_prec, top_prec=top_prec, top_prec_chance=top_frac,
                auc_acc=auc(m, acc), auc_top=auc(m[acc], top[acc]),
                sig_a=sig_a, top_prec_if_score_only=top_prec_score_only, own_fit=own, own_at_zero=at_bound,
                score_share=share)


def iclr_highlights() -> pd.DataFrame:
    d = iclr.read_cache()
    d = d[d.main_track.astype(bool) & d.status.isin(["oral", "spotlight", "poster", "reject"])].copy()
    d["r"] = _ratings(d)
    d = d[d.r.apply(len) > 0]
    rows = []
    for year, g in d.groupby("year"):
        m = g.r.apply(np.mean).to_numpy()
        acc = g.status.isin(["oral", "spotlight", "poster"]).to_numpy()
        top = g.status.isin(["oral", "spotlight"]).to_numpy()
        rows.append(iclr_highlight_job(int(year), m, acc, top))
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# C  ICLR split halves: does a score-based top tier survive other reviewers?
# ---------------------------------------------------------------------------


def _top_mask(rng: np.random.Generator, x: np.ndarray, frac: float) -> np.ndarray:
    k = int(round(frac * x.shape[1]))
    order = np.lexsort((rng.random(x.shape), -x), axis=1)[:, :k]
    mask = np.zeros(x.shape, bool)
    np.put_along_axis(mask, order, True, axis=1)
    return mask


def split_stats(rng: np.random.Generator, R: np.ndarray, splits: int) -> np.ndarray:
    """R: (papers, 4) ratings. Mean over splits and both directions of the shares of A's
    accepts, A's top tier and A's other accepts that B rejects."""
    perm = np.argsort(rng.random((splits,) + R.shape), axis=2)
    X = np.take_along_axis(np.broadcast_to(R, (splits,) + R.shape), perm, axis=2)
    out = []
    for a, b in ((X[..., :2], X[..., 2:]), (X[..., 2:], X[..., :2])):
        mA, mB = a.mean(-1), b.mean(-1)
        accA, topA, accB = _top_mask(rng, mA, ICLR_ALPHA), _top_mask(rng, mA, ICLR_TOP), _top_mask(rng, mB, ICLR_ALPHA)
        rej = ~accB
        post = accA & ~topA
        out.append([(rej & accA).sum(1) / accA.sum(1), (rej & topA).sum(1) / topA.sum(1),
                    (rej & post).sum(1) / post.sum(1)])
    return np.asarray(out).mean(axis=(0, 2))


def ordinal_null(R: np.ndarray, rho1: float, seed: int, reps: int, splits: int = 10) -> np.ndarray:
    vals, counts = np.unique(R, return_counts=True)
    cut = norm.ppf(np.cumsum(counts)[:-1] / counts.sum())
    rng = np.random.default_rng(seed)
    out = []
    for _ in range(reps):
        q = rng.standard_normal((len(R), 1))
        z = np.sqrt(rho1) * q + np.sqrt(1 - rho1) * rng.standard_normal((len(R), 4))
        out.append(split_stats(rng, vals[np.searchsorted(cut, z)], splits))
    return np.mean(out, axis=0)


def splithalf_job(year: int, ratings: list) -> dict:
    rng = np.random.default_rng(stable_seed(year, "iclr-splithalf-top"))
    R = np.array([rng.choice(r, 4, replace=False) for r in ratings])
    obs = split_stats(rng, R, SPLITS)
    seed = stable_seed(year, "iclr-splithalf-top-null")
    rho1 = brentq(lambda p: ordinal_null(R, p, seed, reps=2)[0] - obs[0], 0.02, 0.95, xtol=1e-3)
    null = ordinal_null(R, rho1, seed + 1, reps=8)
    return dict(year=year, n=len(R), scores="pre-discussion" if year == 2026 else "final", rho1=rho1,
                acc_rej=obs[0], acc_rej_null=null[0], top_rej=obs[1], top_rej_null=null[1],
                post_rej=obs[2], post_rej_null=null[2])


def iclr_splithalf(workers: int) -> pd.DataFrame:
    d = iclr.read_cache()
    d = d[d.main_track.astype(bool) & d.status.isin(["oral", "spotlight", "poster", "reject"])].copy()
    d["r"] = _ratings(d)
    d = d[d.r.apply(len) >= 4]
    years = sorted(int(y) for y in d.year.unique())
    with ProcessPoolExecutor(max_workers=workers) as ex:
        rows = list(ex.map(splithalf_job, years, [list(d[d.year == y].r) for y in years]))
    df = pd.DataFrame(rows)
    pool = df[df.year.between(2021, 2025)]
    w = pool.n / pool.n.sum()
    cols = ["rho1", "acc_rej", "acc_rej_null", "top_rej", "top_rej_null", "post_rej", "post_rej_null"]
    pooled = {"year": "2021-2025", "n": int(pool.n.sum()), "scores": "final", **{c: float((pool[c] * w).sum()) for c in cols}}
    return pd.concat([df, pd.DataFrame([pooled])], ignore_index=True)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=5)
    args = ap.parse_args()
    res = os.path.join(ROOT, "results")

    jobs = replay_jobs()
    with ProcessPoolExecutor(max_workers=args.workers) as ex:
        a = pd.DataFrame(list(ex.map(replay_job, *zip(*jobs))))
    a.to_csv(os.path.join(res, "highlight_process_neurips2021.csv"), index=False)
    print(a[["kind", "level", "rho2", "shared", "own", "score_share", "overlap_mean", "spot_rej_mean",
             "p_spot_rej_ge_obs", "p_joint", "post_rej_mean", "oral_rej_mean", "acc_dis_mean"]].round(3).to_string(index=False))

    b = iclr_highlights()
    b.to_csv(os.path.join(res, "iclr_highlight_scores.csv"), index=False)
    print(b.round(3).to_string(index=False))

    c = iclr_splithalf(args.workers)
    c.to_csv(os.path.join(res, "iclr_splithalf_top.csv"), index=False)
    print(c.round(3).to_string(index=False))


if __name__ == "__main__":
    main()
