"""The three reliability levels carried through every result (handoff §7.4), and the
store of per-variant calibrated reviewer noise (handoff §7.3).

pessimistic  lowest two-committee estimate: NeurIPS 2014 "quoted" (25.9% inconsistency
             at the conference-wide 22.5% acceptance rate)
central      NeurIPS 2021, the largest experiment: 203 of its 764 decided papers got
             inconsistent decisions at a 26.2% average acceptance rate (the 118 papers
             withdrawn in both copies are excluded; including them, as the quoted
             "23.0% at 22.7%" does, gives rho^2 = 0.557). NeurIPS 2014's raw table
             (0.527) and both experiments' score correlations (0.55, 0.59) are close.
optimistic   ICLR inter-review correlation 0.40 at 3.7 reviews per paper (Spearman-Brown);
             reviewer-level agreement only, so an upper bound

Every variant is recalibrated so that its simulated two-committee disagreement at the
NeurIPS 2021 decided-set acceptance rate (26.2%) equals the Gaussian model's disagreement at the
level's rho^2. At the central level that target is NeurIPS 2021's own disagreement.
"""

from __future__ import annotations

import os

import numpy as np
import pandas as pd

from . import analytic as an
from .calibrate import ICLR_REVIEW_CORR, ICLR_REVIEWS_PER_PAPER, NEURIPS2014_QUOTED, NEURIPS2021
from .model import ReviewModel

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CALIB_CSV = os.path.join(ROOT, "results", "calibration_variants.csv")

CAL_ALPHA = NEURIPS2021.alpha
LEVELS: dict[str, float] = {
    "pessimistic": NEURIPS2014_QUOTED.rho2,
    "central": NEURIPS2021.rho2,
    "optimistic": float(an.spearman_brown(ICLR_REVIEW_CORR, ICLR_REVIEWS_PER_PAPER)),
}


def target_dis(level: str) -> float:
    """Two-committee disagreement at CAL_ALPHA that every variant must reproduce."""
    return float(an.disagreement(CAL_ALPHA, LEVELS[level]))


VARIANT_FIELDS = ("R", "scale", "quality", "noise", "sigma_u", "mu_q", "scale_points", "careless", "careless_kind")
FIELD_DEFAULTS = {"careless": 0.0, "careless_kind": "rave"}


def variant_key(m: ReviewModel) -> tuple:
    d = {**FIELD_DEFAULTS, **m.as_dict()}
    return tuple(d[f] for f in VARIANT_FIELDS)


def _store() -> pd.DataFrame:
    df = pd.read_csv(CALIB_CSV, keep_default_na=False, na_values=[""])
    df["scale_points"] = df["scale_points"].fillna("").astype(str)
    for f, v in FIELD_DEFAULTS.items():
        df[f] = df[f].fillna(v) if f in df else v
    return df


def calibrated(m: ReviewModel, level: str = "central") -> ReviewModel:
    """Return m with sigma_eps replaced by its calibrated value at the given level.

    Gaussian continuous models use the exact analytic inverse; every other variant
    must already be in results/calibration_variants.csv.
    """
    if m.gaussian_shortcut and m.quality == "gaussian":
        se = float(an.sigma_eps_for_rho2(LEVELS[level], m.R, m.sigma_q, m.sigma_u))
        return m.replace(sigma_eps=se)
    df = _store()
    key = variant_key(m)
    mask = np.ones(len(df), bool)
    for f, v in zip(VARIANT_FIELDS, key):
        col = df[f]
        mask &= (np.isclose(col.astype(float), float(v)) if f in ("R", "sigma_u", "mu_q", "careless")
                 else (col.astype(str) == str(v)))
    mask &= df["level"] == level
    hit = df[mask]
    if len(hit) != 1:
        raise KeyError(f"no unique calibration for {key} at level {level!r} ({len(hit)} rows)")
    return m.replace(sigma_eps=float(hit["sigma_eps"].iloc[0]))
