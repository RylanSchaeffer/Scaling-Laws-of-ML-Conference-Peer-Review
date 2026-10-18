"""Out-of-sample tests (handoff §8.1): replay the NeurIPS 2021 consistency experiment's
award decisions in the calibrated model.

Each committee ranks the same papers by its own mean score, accepts its top A, and
puts the top `oral` papers of its award ordering (score plus chair noise within the
accepted set, model.award_order) in its Oral tier and the next `spot` in its Spotlight tier.
The tiers are separate (peerreview.tiers); the experiment had no Best Papers tier, so its Spotlight
or Better set is Orals plus Spotlights (sob). The statistics are the ones the experiment reported:
the overlap of the two Spotlight or Better sets, and the share of one committee's Spotlights (and of
its Spotlight or Better papers) that the other committee rejected.

Two designs:
  pool       a stand-alone pool of n papers with exactly the observed tier sizes;
  subsample  the experiment as a random n-paper subsample of an N-paper conference
             whose tiers and acceptance are set conference-wide at the observed rates
             (so tier sizes inside the subsample vary from run to run).
"""

from __future__ import annotations

import numpy as np

from .model import ReviewModel, award_order, jitter, sample_quality, sample_scores


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
) -> dict[str, np.ndarray]:
    """Per-conference statistics of the top-tier replay.

    tiers = (orals, spotlights) for each committee, counted in a pool of n papers.
    With N_conf set, the tiers and acceptance are fractions of an N_conf-paper
    conference and the statistics are counted inside its first n papers.
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
    out: dict[str, list] = {k: [] for k in ("sob_overlap", "sob1", "sob2", "spot1", "spot2", "spot1_rej2", "spot2_rej1",
                                             "sob1_rej2", "sob2_rej1", "acc_overlap", "acc1")}  # sob: Spotlight or Better
    done = 0
    while done < reps:
        r = min(chunk, reps - done)
        q = sample_quality(rng, (r, N), m)
        s1 = jitter(rng, sample_scores(rng, q, m), m)
        s2 = jitter(rng, sample_scores(rng, q, m), m)
        a1 = s1 >= _kth_largest(s1, sizes["acc"])
        a2 = s2 >= _kth_largest(s2, sizes["acc"])
        t1 = award_order(rng, s1, m, sizes["acc"])
        t2 = award_order(rng, s2, m, sizes["acc"])
        sob1 = t1 >= _kth_largest(t1, sizes["t1"])  # Spotlight or Better: Orals plus Spotlights
        sob2 = t2 >= _kth_largest(t2, sizes["t2"])
        spot1 = sob1 & ~(t1 >= _kth_largest(t1, sizes["o1"]))  # Spotlight: Spotlight or Better minus the Orals
        spot2 = sob2 & ~(t2 >= _kth_largest(t2, sizes["o2"]))
        sub = slice(0, n)
        a1, a2, sob1, sob2, spot1, spot2 = (x[:, sub] for x in (a1, a2, sob1, sob2, spot1, spot2))
        with np.errstate(invalid="ignore", divide="ignore"):
            out["sob_overlap"].append((sob1 & sob2).sum(1))
            out["sob1"].append(sob1.sum(1))
            out["sob2"].append(sob2.sum(1))
            out["spot1"].append(spot1.sum(1))
            out["spot2"].append(spot2.sum(1))
            out["spot1_rej2"].append((spot1 & ~a2).sum(1))
            out["spot2_rej1"].append((spot2 & ~a1).sum(1))
            out["sob1_rej2"].append((sob1 & ~a2).sum(1))
            out["sob2_rej1"].append((sob2 & ~a1).sum(1))
            out["acc_overlap"].append((a1 & a2).sum(1))
            out["acc1"].append(a1.sum(1))
        done += r
    return {k: np.concatenate(v) for k, v in out.items()}
