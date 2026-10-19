"""Vectorised Monte Carlo of whole conferences (handoff §4, §9).

A chunk of conferences is a (replicates x N) array. Top-K sets come from
argpartition; thresholds of the K-th largest value come from one np.partition
call with every needed K. Nothing is fully sorted except the top block of scores.

Metric names (per selection X of size K; every value is a per-conference mean):
  Top-of-ranking selections (fixed number "K{K}", fixed percentile "p{pct}pct"):
    prec_X    |Top_K(s1) & Top_K(q)| / K                         (headline metric)
    c2x_X     share of Top_K(s1) in the true top 2K   (NaN if 2K > N)
    c10x_X    share of Top_K(s1) in the true top 10K  (NaN if 10K > N)
    c1pct_X   share of Top_K(s1) in the true top round(0.01 N)
    c5pct_X   share of Top_K(s1) in the true top round(0.05 N)
    cA_X      share of Top_K(s1) in the true top round(alpha_ref N)
    pctl_X    mean population percentile F(q) of Top_K(s1)
    ovl_X     |Top_K(s1) & Top_K(s2)| / K               (two committees)
    rej2_X    share of Top_K(s1) that committee 2 rejects at alpha_ref
  Acceptance selections ("acc{alpha:.2f}", size A = round(alpha N)):
    prec_X    1 - swap fraction
    swap_X    share of accepted papers not in Top_A(q)
    ovl_X     P(accepted by 2 | accepted by 1)
    dis_X     P(rejected by 2 | accepted by 1) = 1 - ovl_X
    incons_X  share of all papers accepted by exactly one committee = 2A(1-ovl)/N
  Highest-quality paper (not the Best Papers; not in the paper): best_in_K{K} = P(the paper of highest
  true quality is in Top_K(s1)).
  winner_rank: true rank (1 = best) of the first paper of the award ordering; pooled quantiles
  (simulate_best_paper pools it over the n_best Best Papers).
  corr_qs = corr(q, s1); corr_s12 = corr(s1, s2) (computed before jitter).
"""

from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass, field

import numpy as np

from .tiers import OR_BETTER, bands
from .model import ReviewModel, award_order, jitter, quality_cdf, sample_quality, sample_scores

DEFAULT_ALPHAS = (0.10, 0.15, 0.20, 0.25, 0.30, 0.35, 0.40)


@dataclass(frozen=True)
class Selections:
    """Which selections to evaluate. Sizes are resolved against N by `sizes`."""

    fixed_K: tuple[int, ...] = (1, 5, 10, 30, 100)
    pct: tuple[float, ...] = (0.003, 0.005, 0.01, 0.05)
    alphas: tuple[float, ...] = DEFAULT_ALPHAS
    best_K: tuple[int, ...] = (1, 5, 10, 30)
    alpha_ref: float = 0.25  # acceptance rate for cA_ and rej2_

    def sizes(self, N: int) -> tuple[dict[str, int], dict[str, int]]:
        top = {f"K{K}": int(K) for K in self.fixed_K if 1 <= K <= N}
        for p in self.pct:
            K = int(round(p * N))
            if K >= 1:
                top[f"p{100 * p:g}pct"] = K
        acc = {}
        for a in self.alphas:
            A = int(round(a * N))
            if 1 <= A < N:
                acc[f"acc{a:.2f}"] = A
        return top, acc


def stable_seed(*parts) -> int:
    """A reproducible 32-bit seed from any JSON-serialisable description."""
    blob = json.dumps(parts, sort_keys=True, default=str).encode()
    return int.from_bytes(hashlib.sha256(blob).digest()[:4], "little")


def default_reps(N: int, budget: float = 2e8, rmin: int = 200, rmax: int = 10_000) -> int:
    """Replicates under a fixed budget of paper draws (handoff §9)."""
    return int(np.clip(budget // N, rmin, rmax))


def _thresholds(x: np.ndarray, Ks) -> dict[int, np.ndarray]:
    """Row-wise value of the K-th largest entry, for every K in Ks."""
    N = x.shape[1]
    Ks = sorted({int(K) for K in Ks if 1 <= K <= N})
    if not Ks:
        return {}
    part = np.partition(x, [N - K for K in Ks], axis=1)
    return {K: part[:, N - K] for K in Ks}


def _rowcorr(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    a = a - a.mean(axis=1, keepdims=True)
    b = b - b.mean(axis=1, keepdims=True)
    return (a * b).sum(1) / np.sqrt((a * a).sum(1) * (b * b).sum(1))


@dataclass
class _Acc:
    """Accumulates per-conference metric values across chunks."""

    vals: dict[str, list] = field(default_factory=dict)

    def add(self, name: str, v) -> None:
        self.vals.setdefault(name, []).append(np.asarray(v, dtype=float))

    def summary(self) -> dict[str, float]:
        out = {}
        for k, chunks in self.vals.items():
            v = np.concatenate(chunks)
            if k in ("winner_rank", "winner_rank2", "best_papers_rank", "best_papers_rank2"):
                # Pooled over all conferences, never averaged over chunks (§9). winner_*: the first paper of the award
                # ordering (simulate_chunk); best_papers_*: each of the three Best Papers, pooled (simulate_best_paper).
                for qn in (0.1, 0.25, 0.5, 0.75, 0.9):
                    out[f"{k}_q{int(100 * qn)}"] = float(np.quantile(v, qn))
                out[f"{k}_median"] = float(np.median(v))
                out["winner_logrank_mean" if k == "winner_rank" else f"{k}_logrank_mean"] = float(np.mean(np.log(v)))
                continue
            ok = np.isfinite(v)
            n = int(ok.sum())
            out[k] = float(v[ok].mean()) if n else np.nan
            out[f"{k}_se"] = float(v[ok].std(ddof=1) / np.sqrt(n)) if n > 1 else np.nan
            if k.startswith("z2_"):  # score positions also report their spread across conferences
                out[f"{k}_sd"] = float(v[ok].std(ddof=1)) if n > 1 else np.nan
        return out


def simulate_chunk(
    rng: np.random.Generator,
    m: ReviewModel,
    N: int,
    reps: int,
    sel: Selections,
    two_committees: bool = True,
    acc: _Acc | None = None,
) -> _Acc:
    acc = acc or _Acc()
    rows = np.arange(reps)[:, None]
    q = sample_quality(rng, (reps, N), m)
    s1 = sample_scores(rng, q, m)
    s2 = sample_scores(rng, q, m) if two_committees else None

    acc.add("corr_qs", _rowcorr(q, s1))
    if two_committees:
        acc.add("corr_s12", _rowcorr(s1, s2))

    s1 = jitter(rng, s1, m)
    if two_committees:
        s2 = jitter(rng, s2, m)

    top, accsel = sel.sizes(N)
    A_ref = int(round(sel.alpha_ref * N))
    M1, M5 = max(1, int(round(0.01 * N))), max(1, int(round(0.05 * N)))
    # Award ordering (model.award_order): the top-of-ranking selections, the first paper of the award
    # ordering (winner_rank) and the highest-quality paper's rank (best_in_K) are by score + chair noise within the accepted set (A_ref); acceptance stays by the score.
    t1 = award_order(rng, s1, m, A_ref)
    t2 = award_order(rng, s2, m, A_ref) if two_committees else None

    # Thresholds (K-th largest values) for every size that is needed.
    q_need = {M1, M5, A_ref} | set(accsel.values())
    for K in top.values():
        q_need |= {K, 2 * K, 10 * K}
    Tq = _thresholds(q, q_need)
    T1 = _thresholds(s1, accsel.values())
    T2 = _thresholds(s2, set(accsel.values()) | {A_ref}) if two_committees else {}
    T2t = _thresholds(t2, set(top.values())) if two_committees else {}

    # --- top-of-ranking selections: sort only the top Kt of the award ordering -------------
    if top:
        Kt = max(top.values())
        if Kt < N:
            idx = np.argpartition(-t1, Kt - 1, axis=1)[:, :Kt]
        else:
            idx = np.broadcast_to(np.arange(N), (reps, N)).copy()
        order = np.argsort(-t1[rows, idx], axis=1)
        idx = np.take_along_axis(idx, order, axis=1)
        q_top = q[rows, idx]
        cs1 = np.cumsum(q_top >= Tq[M1][:, None], axis=1)
        cs5 = np.cumsum(q_top >= Tq[M5][:, None], axis=1)
        csA = np.cumsum(q_top >= Tq[A_ref][:, None], axis=1)
        csF = np.cumsum(quality_cdf(q_top, m), axis=1)
        if two_committees:
            s2_top = s2[rows, idx]
            t2_top = t2[rows, idx]
            csR = np.cumsum(s2_top < T2[A_ref][:, None], axis=1)
        for name, K in top.items():
            qk = q_top[:, :K]
            acc.add(f"prec_{name}", (qk >= Tq[K][:, None]).sum(1) / K)
            for mult in (2, 10):
                M = mult * K
                v = (qk >= Tq[M][:, None]).sum(1) / K if M <= N else np.full(reps, np.nan)
                acc.add(f"c{mult}x_{name}", v)
            acc.add(f"c1pct_{name}", cs1[:, K - 1] / K)
            acc.add(f"c5pct_{name}", cs5[:, K - 1] / K)
            acc.add(f"cA_{name}", csA[:, K - 1] / K)
            acc.add(f"pctl_{name}", csF[:, K - 1] / K)
            if two_committees:
                acc.add(f"ovl_{name}", (t2_top[:, :K] >= T2t[K][:, None]).sum(1) / K)
                acc.add(f"rej2_{name}", csR[:, K - 1] / K)

    # --- acceptance selections: boolean masks over all N --------------------
    for name, A in accsel.items():
        m1 = s1 >= T1[A][:, None]
        prec = (m1 & (q >= Tq[A][:, None])).sum(1) / A
        acc.add(f"prec_{name}", prec)
        acc.add(f"swap_{name}", 1.0 - prec)
        if two_committees:
            ovl = (m1 & (s2 >= T2[A][:, None])).sum(1) / A
            acc.add(f"ovl_{name}", ovl)
            acc.add(f"dis_{name}", 1.0 - ovl)
            acc.add(f"incons_{name}", 2.0 * A * (1.0 - ovl) / N)

    # --- highest-quality paper (best_in_K) and first of the award ordering (winner_rank) ----------------------------------------------
    b = np.argmax(q, axis=1)
    srank_best = (t1 > t1[rows[:, 0], b][:, None]).sum(1)  # 0-based rank in the award ordering
    for K in sel.best_K:
        if K <= N:
            acc.add(f"best_in_K{K}", srank_best < K)
    w = np.argmax(t1, axis=1)
    acc.add("winner_rank", (q > q[rows[:, 0], w][:, None]).sum(1) + 1)
    return acc


def simulate(
    m: ReviewModel,
    N: int,
    reps: int | None = None,
    sel: Selections = Selections(),
    two_committees: bool = True,
    seed: int | None = None,
    chunk_elems: float = 4e6,
    salt: str = "",
) -> dict:
    """Simulate `reps` conferences of N papers. Returns one flat result row."""
    reps = default_reps(N) if reps is None else int(reps)
    if seed is None:
        seed = stable_seed(m.as_dict(), N, reps, two_committees, salt)
    rng = np.random.default_rng(seed)
    per_paper = m.R if not m.gaussian_shortcut else 1
    chunk = max(1, int(chunk_elems // (N * per_paper)))
    t0 = time.perf_counter()
    acc = _Acc()
    done = 0
    while done < reps:
        r = min(chunk, reps - done)
        simulate_chunk(rng, m, N, r, sel, two_committees, acc)
        done += r
    row = {**m.as_dict(), "N": N, "reps": reps, "seed": seed, "two_committees": two_committees}
    row["rho2"] = m.reliability
    row.update(acc.summary())
    row["wall_s"] = time.perf_counter() - t0
    return row


# ---------------------------------------------------------------------------
# Fast special-purpose simulators
# ---------------------------------------------------------------------------


def simulate_best_paper(
    m: ReviewModel,
    N: int,
    reps: int,
    best_K=(1, 5, 10, 30),
    seed: int | None = None,
    chunk_elems: float = 4e6,
    salt: str = "",
    best_papers_cuts: dict[str, int] | None = None,
    second_committee: bool = False,
    overlap_cuts: dict[str, int] | None = None,
    place: bool = False,
    n_accepted: int | None = None,
    n_best: int = 1,
) -> dict:
    """High-replication tier probabilities and ranks of the Best Papers, the first n_best papers of the award ordering; O(N) per conference.

    Every rank is in the award ordering (model.award_order): the score plus the chairs' award noise
    within the accepted set (Accepted or Better), whose size is `n_accepted`, else the "accept_or_better" entry of best_papers_cuts or
    overlap_cuts, else 25% of N. The Best Papers are the first n_best papers of that ordering
    (the paper uses n_best = 3). With sigma_award = 0 the award ordering is the score ordering.

    Tiers are separate (peerreview.tiers): a paper is in exactly one of best, oral, spot, accept, reject.
    The cutoff dicts below are keyed by tiers.CUTS: "best" (n_best), then the size of each "or Better" set,
    "oral_or_better", "spot_or_better", "accept_or_better"; any other key is a plain top-M set.

    best_papers_cuts {cut: M} adds best_papers_in_{cut}, the proportion of the Best Papers in the true top M,
    averaged over conferences. second_committee re-reviews every paper with fresh noise (u, eps and eta
    redrawn) and adds best_papers_rank2, the rank of each of the Best Papers by the second review's award
    ordering (pooled over the three), and best_papers_in2_{cut}, the proportion of the Best Papers that the
    second review ranks within M. These are "or Better" probabilities; tiers.add_separate turns them into
    the separate tiers'. best_papers_in2_best is the share of the Best Papers that the second review keeps.
    With second_committee, overlap_cuts {cut: K} adds overlap_{cut}, the proportion of the first review's
    top K that the second review also ranks in its top K (overlap_best, overlap_oral_or_better, ...), and
    overlap_{tier} for each separate tier between two known cuts (overlap_oral, overlap_spot,
    overlap_accept): the proportion of the first review's tier that the second review puts in the same
    tier. It also adds z2_best_papers and z2_cut, the second review's score for the first review's Best Papers
    (their mean) and its own n_best-th best score in its award ordering, both in units of the second
    review's score SD about its mean.
    With overlap_cuts, place adds place_{x}_in_{y}: the proportion of the first review's group x that the
    second review puts in the separate tier y (best, oral, spot, accept, reject). x is a separate tier
    (best, oral, spot, accept) or an "or Better" set (oral_or_better, spot_or_better, accept_or_better).
    Each x's five placements sum to 1, and place_x_in_x equals overlap_x for a separate tier x.
    """
    if seed is None:
        seed = stable_seed(m.as_dict(), N, reps, "best", salt)
    if n_accepted is None:
        n_accepted = (best_papers_cuts or {}).get("accept_or_better") or (overlap_cuts or {}).get("accept_or_better") or int(round(0.25 * N))
    rng = np.random.default_rng(seed)
    per_paper = m.R if not m.gaussian_shortcut else 1
    chunk = max(1, int(chunk_elems // (N * per_paper)))
    t0 = time.perf_counter()
    acc = _Acc()
    done = 0
    while done < reps:
        r = min(chunk, reps - done)
        rows = np.arange(r)
        q = sample_quality(rng, (r, N), m)
        s = jitter(rng, sample_scores(rng, q, m), m)
        t = award_order(rng, s, m, n_accepted)
        b = np.argmax(q, axis=1)
        srank = (t > t[rows, b][:, None]).sum(1)
        for K in best_K:
            acc.add(f"best_in_K{K}", srank < K)
        if n_best == 1:
            W = np.argmax(t, axis=1)[:, None]
        else:  # the first n_best papers of the award ordering, in any order
            W = np.argpartition(-t, n_best - 1, axis=1)[:, :n_best]
        rank = np.stack([(q > q[rows, W[:, k]][:, None]).sum(1) + 1 for k in range(n_best)], axis=1)
        acc.add("best_papers_rank", rank.ravel())
        for name, M in (best_papers_cuts or {}).items():
            acc.add(f"best_papers_in_{name}", (rank <= M).mean(1))
        if second_committee:
            s2 = jitter(rng, sample_scores(rng, q, m), m)
            t2 = award_order(rng, s2, m, n_accepted)
            rank2 = np.stack([(t2 > t2[rows, W[:, k]][:, None]).sum(1) + 1 for k in range(n_best)], axis=1)
            acc.add("best_papers_rank2", rank2.ravel())
            for name, M in (best_papers_cuts or {}).items():
                acc.add(f"best_papers_in2_{name}", (rank2 <= M).mean(1))
            if overlap_cuts:
                order1 = np.argsort(-t, axis=1)
                order2 = np.argsort(-t2, axis=1)
                rank2_all = np.empty_like(order2)
                rank2_all[rows[:, None], order2] = np.arange(N)[None, :]  # 0-based rank by the second review
                r2 = rank2_all[rows[:, None], order1]  # the second review's rank of the first review's k-th paper
                for name, K in overlap_cuts.items():  # "or Better" sets (and the Best Papers): top K in both
                    K = int(K)
                    acc.add(f"overlap_{name}", (r2[:, :K] < K).sum(1) / K)
                bd = bands(overlap_cuts, N)
                for x, (lo, hi) in bd.items():  # separate tiers: the same tier in both reviews
                    if x not in ("best", "reject") and hi > lo:
                        acc.add(f"overlap_{x}", ((r2[:, lo:hi] >= lo) & (r2[:, lo:hi] < hi)).sum(1) / (hi - lo))
                if place:  # first-review groups: each separate tier, and each "or Better" set (its top K)
                    groups = {x: (lo, hi) for x, (lo, hi) in bd.items() if x != "reject" and hi > lo}
                    groups.update({c: (0, int(overlap_cuts[c])) for c in OR_BETTER if c in overlap_cuts})
                    for x, (lo, hi) in groups.items():
                        rx = r2[:, lo:hi]
                        for y, (ylo, yhi) in bd.items():
                            acc.add(f"place_{x}_in_{y}", ((rx >= ylo) & (rx < yhi)).sum(1) / (hi - lo))
                mu2, sd2 = s2.mean(axis=1), s2.std(axis=1)
                acc.add("z2_best_papers", ((s2[rows[:, None], W] - mu2[:, None]) / sd2[:, None]).mean(1))
                acc.add("z2_cut", (s2[rows, order2[:, n_best - 1]] - mu2) / sd2)
        done += r
    row = {**m.as_dict(), "N": N, "reps": reps, "seed": seed, "rho2": m.reliability, "accepted": int(n_accepted)}
    row.update(acc.summary())
    row["wall_s"] = time.perf_counter() - t0
    return row


def disagreement(
    m: ReviewModel,
    N: int,
    alpha: float,
    reps: int,
    seed: int,
    chunk_elems: float = 4e6,
) -> dict:
    """Two-committee accept-level statistics only (for calibration by bisection).

    With a fixed seed the same random numbers are reused for every sigma_eps
    (common random numbers), so the result is a smooth, monotone function of
    sigma_eps for continuous scores.
    """
    rng = np.random.default_rng(seed)
    per_paper = m.R if not m.gaussian_shortcut else 1
    chunk = max(1, int(chunk_elems // (N * per_paper)))
    A = int(round(alpha * N))
    dis, incons, prec, c12 = [], [], [], []
    done = 0
    while done < reps:
        r = min(chunk, reps - done)
        q = sample_quality(rng, (r, N), m)
        s1 = sample_scores(rng, q, m)
        s2 = sample_scores(rng, q, m)
        c12.append(_rowcorr(s1, s2))
        s1, s2 = jitter(rng, s1, m), jitter(rng, s2, m)
        T = _thresholds(np.concatenate([s1, s2, q]), [A])[A]
        t1, t2, tq = T[:r, None], T[r : 2 * r, None], T[2 * r :, None]
        a1 = s1 >= t1
        ovl = (a1 & (s2 >= t2)).sum(1) / A
        dis.append(1 - ovl)
        incons.append(2 * A * (1 - ovl) / N)
        prec.append((a1 & (q >= tq)).sum(1) / A)
        done += r
    dis, incons, prec, c12 = map(np.concatenate, (dis, incons, prec, c12))
    se = lambda v: float(v.std(ddof=1) / np.sqrt(len(v)))
    return {
        "dis": float(dis.mean()),
        "dis_se": se(dis),
        "incons": float(incons.mean()),
        "prec": float(prec.mean()),
        "corr_s12": float(c12.mean()),
        "corr_s12_se": se(c12),
    }
