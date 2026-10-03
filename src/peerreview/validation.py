"""Out-of-sample tests (handoff §8.1): replay the NeurIPS 2021 consistency experiment's
top tier in the calibrated model.

Each committee ranks the same papers by its own mean score, accepts its top A, and
puts its top `oral` papers in an oral tier and the next `spot` papers in a spotlight
tier. The statistics are the ones the experiment reported: the overlap of the two
top tiers (oral + spotlight) and the share of one committee's spotlights that the
other committee rejected.

Highlights beyond scores (optional): each committee may pick its tiers among its accepted
papers by an index  s + sd(s) * (shared * h + own * e),  where h ~ N(0, 1) is a paper
property both committees see (such as broad interest), e ~ N(0, 1) is drawn afresh for each
committee, and sd(s) is the SD of the scores across papers. own = inf picks the tiers at
random among accepted papers. With orals_by_score, the orals still follow the score and
only the spotlights use the index. With shared = own = 0 the tiers follow the score alone
and the random draws are unchanged.

Two designs:
  pool       a stand-alone pool of n papers with exactly the observed tier sizes;
  subsample  the experiment as a random n-paper subsample of an N-paper conference
             whose tiers and acceptance are set conference-wide at the observed rates
             (so tier sizes inside the subsample vary from run to run).
"""

from __future__ import annotations

import numpy as np

from .model import ReviewModel, jitter, sample_quality, sample_scores


def _kth_largest(x: np.ndarray, K: int) -> np.ndarray:
    N = x.shape[1]
    return np.partition(x, N - K, axis=1)[:, N - K][:, None]


def replay_tiers(
    m: ReviewModel,
    reps: int,
    seed: int,
    n: int = 882,
    accept_rate: float = 0.227,
    tiers1: tuple[int, int] = (4, 25),
    tiers2: tuple[int, int] = (2, 23),
    N_conf: int | None = None,
    chunk_elems: float = 4e6,
    shared: float = 0.0,
    own: float = 0.0,
    orals_by_score: bool = False,
) -> dict[str, np.ndarray]:
    """Per-conference statistics of the top-tier replay.

    tiers = (orals, spotlights) for each committee, counted in a pool of n papers.
    With N_conf set, the tiers and acceptance are fractions of an N_conf-paper
    conference and the statistics are counted inside its first n papers.
    shared, own, orals_by_score: the non-score terms of the tier index (module docstring).
    """
    rng = np.random.default_rng(seed)
    N = n if N_conf is None else N_conf
    scale = N / n
    o1, p1 = tiers1
    o2, p2 = tiers2
    sizes = {
        "acc": int(round(accept_rate * N)),
        "o1": max(1, int(round(o1 * scale))), "t1": int(round((o1 + p1) * scale)),
        "o2": max(1, int(round(o2 * scale))), "t2": int(round((o2 + p2) * scale)),
    }
    per = 1 if m.gaussian_shortcut else m.R
    chunk = max(1, int(chunk_elems // (N * per)))
    out: dict[str, list] = {k: [] for k in ("overlap", "top1", "top2", "spot1", "spot2", "spot1_rej2", "spot2_rej1",
                                             "top1_rej2", "top2_rej1", "acc_overlap", "acc1", "oral1", "oral2",
                                             "oral1_rej2", "oral2_rej1", "post1", "post2", "post1_rej2", "post2_rej1",
                                             "score_share")}
    beyond = shared != 0 or own != 0
    done = 0
    while done < reps:
        r = min(chunk, reps - done)
        q = sample_quality(rng, (r, N), m)
        s1 = jitter(rng, sample_scores(rng, q, m), m)
        s2 = jitter(rng, sample_scores(rng, q, m), m)
        a1 = s1 >= _kth_largest(s1, sizes["acc"])
        a2 = s2 >= _kth_largest(s2, sizes["acc"])
        if beyond:
            h = rng.standard_normal(s1.shape) if shared else 0.0
            idx = []
            for s, a in ((s1, a1), (s2, a2)):
                e = rng.standard_normal(s.shape)
                if np.isinf(own):
                    t = e
                else:
                    t = s + s.std(axis=1, keepdims=True) * (shared * h + own * e)
                idx.append(np.where(a, t, -np.inf))
            i1, i2 = idx
            if np.isinf(own):
                out["score_share"].append(np.zeros(r))
            else:
                # The non-score terms are independent of s, so var(s) / var(index) among accepts.
                share = [np.array([np.var(s[k][a[k]]) / np.var(i[k][a[k]]) for k in range(len(s))])
                         for s, a, i in ((s1, a1, i1), (s2, a2, i2))]
                out["score_share"].append(0.5 * (share[0] + share[1]))
        else:
            i1, i2 = s1, s2
            out["score_share"].append(np.ones(r))
        if beyond and orals_by_score:
            oral1 = s1 >= _kth_largest(s1, sizes["o1"])
            oral2 = s2 >= _kth_largest(s2, sizes["o2"])
            j1, j2 = np.where(oral1, -np.inf, i1), np.where(oral2, -np.inf, i2)
            spot1 = j1 >= _kth_largest(j1, sizes["t1"] - sizes["o1"])
            spot2 = j2 >= _kth_largest(j2, sizes["t2"] - sizes["o2"])
            top1, top2 = oral1 | spot1, oral2 | spot2
        else:
            top1 = i1 >= _kth_largest(i1, sizes["t1"])
            top2 = i2 >= _kth_largest(i2, sizes["t2"])
            oral1 = i1 >= _kth_largest(i1, sizes["o1"])
            oral2 = i2 >= _kth_largest(i2, sizes["o2"])
            spot1 = top1 & ~oral1
            spot2 = top2 & ~oral2
        sub = slice(0, n)
        a1, a2, top1, top2, spot1, spot2, oral1, oral2 = (
            x[:, sub] for x in (a1, a2, top1, top2, spot1, spot2, oral1, oral2))
        post1, post2 = a1 & ~top1, a2 & ~top2
        with np.errstate(invalid="ignore", divide="ignore"):
            out["overlap"].append((top1 & top2).sum(1))
            out["top1"].append(top1.sum(1))
            out["top2"].append(top2.sum(1))
            out["spot1"].append(spot1.sum(1))
            out["spot2"].append(spot2.sum(1))
            out["spot1_rej2"].append((spot1 & ~a2).sum(1))
            out["spot2_rej1"].append((spot2 & ~a1).sum(1))
            out["top1_rej2"].append((top1 & ~a2).sum(1))
            out["top2_rej1"].append((top2 & ~a1).sum(1))
            out["acc_overlap"].append((a1 & a2).sum(1))
            out["acc1"].append(a1.sum(1))
            out["oral1"].append(oral1.sum(1))
            out["oral2"].append(oral2.sum(1))
            out["oral1_rej2"].append((oral1 & ~a2).sum(1))
            out["oral2_rej1"].append((oral2 & ~a1).sum(1))
            out["post1"].append(post1.sum(1))
            out["post2"].append(post2.sum(1))
            out["post1_rej2"].append((post1 & ~a2).sum(1))
            out["post2_rej1"].append((post2 & ~a1).sum(1))
        done += r
    return {k: np.concatenate(v) for k, v in out.items()}
