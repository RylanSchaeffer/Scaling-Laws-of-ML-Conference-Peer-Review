"""Calibration of reviewer noise to field data (handoff §7).

§7.1 Two-committee experiments -> committee correlation r12 = rho2 (analytic inverse).
§7.2 Inter-review correlation -> rho2 by Spearman-Brown (reviewer-level only).
§7.3 Any variant (discrete scale, non-Gaussian shapes, shared noise) -> sigma_eps by
     bisection on simulated two-committee disagreement, with common random numbers.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from . import analytic as an
from .model import ReviewModel
from .simulate import disagreement as sim_disagreement


@dataclass(frozen=True)
class ExperimentTarget:
    name: str
    alpha: float  # acceptance rate at which the disagreement was measured
    incons: float  # share of all papers with inconsistent decisions
    n_papers: int
    note: str

    @property
    def dis(self) -> float:
        """P(rejected by 2 | accepted by 1) = incons / (2 alpha) when both accept alpha N."""
        return self.incons / (2.0 * self.alpha)

    @property
    def rho2(self) -> float:
        return float(an.invert_inconsistent(self.alpha, self.incons))

    def rho2_ci(self, z: float = 1.96) -> tuple[float, float]:
        """rho2 at the binomial 95% interval of the inconsistency share (low rho2 first)."""
        se = np.sqrt(self.incons * (1 - self.incons) / self.n_papers)
        return (
            float(an.invert_inconsistent(self.alpha, self.incons + z * se)),
            float(an.invert_inconsistent(self.alpha, self.incons - z * se)),
        )


# §10.1. NeurIPS 2014 table: 22 both, 22 A only, 21 B only, 101 neither (166 papers).
NEURIPS2014_RAW = ExperimentTarget(
    "NeurIPS 2014 (raw table)", alpha=(44 + 43) / 2 / 166, incons=43 / 166, n_papers=166,
    note="committees' own acceptance rate, 43.5/166",
)
NEURIPS2014_QUOTED = ExperimentTarget(
    "NeurIPS 2014 (quoted)", alpha=0.225, incons=43 / 166, n_papers=166,
    note="25.9% inconsistency applied to the conference-wide 22.5% rate",
)
# NeurIPS 2021 Table 1 (arXiv:2306.03262): of 882 duplicated papers, 118 were withdrawn in
# both copies and never decided. Among the 764 decided papers the original committee
# accepted 206 and the copy 195; 203 papers got inconsistent decisions.
NEURIPS2021 = ExperimentTarget(
    "NeurIPS 2021 (decided papers)", alpha=(206 + 195) / 2 / 764, incons=203 / 764, n_papers=764,
    note="203 of 764 decided papers inconsistent at 26.2% average acceptance (withdrawn excluded)",
)
NEURIPS2021_ALL = ExperimentTarget(
    "NeurIPS 2021 (all 882, as quoted)", alpha=(206 + 195) / 2 / 882, incons=203 / 882, n_papers=882,
    note="23.0% at 22.7%: counts the 118 withdrawn papers as consistent rejects",
)
EXPERIMENTS = (NEURIPS2014_RAW, NEURIPS2014_QUOTED, NEURIPS2021, NEURIPS2021_ALL)

# Correlations between the two committees' mean scores: r12 = rho2 directly.
NEURIPS2014_SCORE_CORR = (0.55, 0.065)  # calibrated scores, Cortes & Lawrence 2021
NEURIPS2021_SCORE_CORR = {"initial": 0.575, "final": 0.586}  # arXiv:2306.03262, Fig. 1

# §7.2 inputs.
ICLR_REVIEW_CORR = 0.40  # berenslab ICLR dataset, 2017-2024
ICLR_REVIEWS_PER_PAPER = 3.7
NEURIPS2014_VARCOMP = {"paper": 1.28, "offset": 0.24, "subjective": 1.27}

# The base-model target used for every per-variant recalibration (§7.3).
CENTRAL_TARGET = NEURIPS2021


def reliability_table() -> list[dict]:
    """Every rho2 estimate of §7.1 and §7.2, with what it includes."""
    rows = []
    for e in EXPERIMENTS:
        lo, hi = e.rho2_ci()
        rows.append(dict(source=e.name, method="two-committee inconsistency", alpha=e.alpha,
                         incons=e.incons, dis=e.dis, rho2=e.rho2, rho2_lo=lo, rho2_hi=hi,
                         includes="reviewers + AC + everything that differs between committees",
                         note=e.note))
    c, se = NEURIPS2014_SCORE_CORR
    rows.append(dict(source="NeurIPS 2014 (score correlation)", method="corr of committee mean scores",
                     rho2=c, rho2_lo=c - 1.96 * se, rho2_hi=c + 1.96 * se,
                     includes="reviewers + calibration; no AC decision", note="0.55 +/- 0.065"))
    for stage, c in NEURIPS2021_SCORE_CORR.items():
        rows.append(dict(source=f"NeurIPS 2021 (score correlation, {stage})", method="corr of committee mean scores",
                         rho2=c, includes="reviewers (+ discussion for final); no AC decision",
                         note="arXiv:2306.03262 Fig. 1; the handoff listed this as not reported"))
    for R in (3.0, ICLR_REVIEWS_PER_PAPER, 4.0):
        rows.append(dict(source=f"ICLR 2017-2024, R={R:g}", method="Spearman-Brown on r=0.40",
                         rho2=float(an.spearman_brown(ICLR_REVIEW_CORR, R)),
                         includes="reviewer-level disagreement only (no AC, no shared noise)",
                         note="upper bound on rho2 if any shared component exists"))
    v = NEURIPS2014_VARCOMP
    r1 = v["paper"] / sum(v.values())
    r1c = v["paper"] / (v["paper"] + v["subjective"])
    for R in (3.0, 4.0):
        rows.append(dict(source=f"NeurIPS 2014 variance components, R={R:g}",
                         method="Spearman-Brown, offsets as noise",
                         rho2=float(an.spearman_brown(r1, R)), includes="reviewer level only",
                         note=f"single-review reliability {r1:.3f}"))
        rows.append(dict(source=f"NeurIPS 2014 variance components, R={R:g}",
                         method="Spearman-Brown, offsets removed",
                         rho2=float(an.spearman_brown(r1c, R)), includes="reviewer level only",
                         note=f"single-review reliability {r1c:.3f}"))
    return rows


def calibrate_sigma_eps(
    m: ReviewModel,
    target: float,
    alpha: float = CENTRAL_TARGET.alpha,
    metric: str = "dis",
    N: int = 5000,
    reps: int = 2000,
    seed: int = 20261002,
    lo: float = 0.02,
    hi: float = 12.0,
    tol: float = 5e-4,
    max_iter: int = 40,
) -> dict:
    """Bisection on sigma_eps so the simulated `metric` equals `target`.

    metric "dis": P(rejected by 2 | accepted by 1) at acceptance rate alpha (§7.3).
    metric "corr_s12": correlation of the two committees' mean scores (§8.2).
    Both are monotone in sigma_eps: dis increases, corr_s12 decreases.
    The same seed is used at every step (common random numbers).
    """
    sign = 1.0 if metric == "dis" else -1.0

    def f(se: float) -> tuple[float, dict]:
        out = sim_disagreement(m.replace(sigma_eps=float(se)), N, alpha, reps, seed)
        return sign * (out[metric] - target), out

    flo, _ = f(lo)
    fhi, _ = f(hi)
    branch_lo = lo
    if flo > 0 and fhi > 0 and metric == "dis":
        # On a coarse scale, disagreement is not monotone in sigma_eps: near-zero
        # reviewer noise makes many exact ties, and random tie-breaking dominates.
        # Restrict the search to the rising branch, right of the minimum.
        grid = np.geomspace(lo, hi, 41)
        vals = [f(g)[0] for g in grid]
        i = int(np.argmin(vals))
        lo, flo = float(grid[i]), vals[i]
        branch_lo = lo
    if flo > 0 or fhi < 0:
        return dict(sigma_eps=np.nan, achieved=np.nan, converged=False, iters=0,
                    note=f"target not bracketed in [{lo}, {hi}]")
    out = {}
    for it in range(1, max_iter + 1):
        mid = 0.5 * (lo + hi)
        fm, out = f(mid)
        if fm > 0:
            hi = mid
        else:
            lo = mid
        if abs(fm) < tol and hi - lo < 1e-3:
            break
    se = 0.5 * (lo + hi)
    fm, out = f(se)
    return dict(sigma_eps=se, achieved=out[metric], achieved_se=out[f"{metric}_se"],
                corr_s12=out["corr_s12"], dis=out["dis"], converged=abs(fm) < 2 * tol,
                iters=it, N=N, reps=reps, alpha=alpha, target=target, metric=metric, seed=seed,
                branch_lo=branch_lo)
