"""Generative model of conference peer review (handoff §3).

Paper i has true quality q_i and receives R reviews s_ij = q_i + u_i + eps_ij.
u_i is noise shared by everyone who handles the paper; eps_ij is a reviewer's own
error. Each review is optionally snapped to a score scale before averaging. The
paper's score is the mean of its R (snapped) reviews. Optionally, a share
`careless` of reviews ignore the paper: "rave" reviews give the top of the scale,
"random" reviews a uniformly random score.

Acceptance is by the score: the top A papers. Awards (the Best Papers, orals,
spotlights) are chosen within the accepted set by the award ordering a_i = score_i + eta_i,
where eta_i ~ N(0, sigma_award^2) is the chairs' own noise, redrawn by every committee
(`award_order`); the Best Papers are its first three. With sigma_award = 0 the award ordering is the score ordering.

Everything lives on a latent 1-to-10 axis.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass

import numpy as np
from scipy import special, stats

# Score scales on the latent 1-to-10 axis (handoff §3.2, data/review_forms.csv). "iclr4" is ICLR 2020.
SCALES: dict[str, np.ndarray | None] = {
    "continuous": None,
    "int10": np.arange(1.0, 11.0),
    "six": np.linspace(1.0, 10.0, 6),
    "iclr6": np.array([1.0, 3.0, 5.0, 6.0, 8.0, 10.0]),
    "five": np.linspace(1.0, 10.0, 5),
    "iclr4": np.array([1.0, 3.0, 6.0, 8.0]),
    "iclr2026": np.array([0.0, 2.0, 4.0, 6.0, 8.0, 10.0]),  # ICLR 2026 review form
}
# The review form of the main results: integer 1-to-10 overall scores, four reviews per paper. The scale
# NeurIPS used from 2014 to 2024 (also ICML 2023-2024 and ICLR 2017-2019 and 2021) and the form of the
# NeurIPS 2021 two-committee experiment that calibrates the model; NeurIPS and ICML assign four reviews.
# Other forms (data/review_forms.csv) are tested in the score-scale section (scripts/run_scale_impact.py).
MAIN_FORM: dict = {"R": 4, "scale": "int10"}
QUALITY_DISTS = ("gaussian", "beta", "exp", "t3", "lognormal")
NOISE_DISTS = ("gaussian", "t3")
CARELESS_KINDS = ("rave", "random")


@dataclass(frozen=True)
class ReviewModel:
    """Parameters of one review process. Hashable, so it can key caches and seeds."""

    R: int = 3
    sigma_eps: float = 1.5
    sigma_u: float = 0.0
    mu_q: float = 5.0
    sigma_q: float = 1.2
    quality: str = "gaussian"
    noise: str = "gaussian"
    scale: str = "continuous"
    # Custom scale points, used only when scale == "custom" (for the placement check).
    scale_points: tuple[float, ...] = ()
    # Share of reviews that ignore the paper, and what they say.
    careless: float = 0.0
    careless_kind: str = "rave"
    # Chair-level award noise: SD of eta in the award ordering score + eta within the accepted set.
    sigma_award: float = 0.0

    def __post_init__(self) -> None:
        if self.quality not in QUALITY_DISTS:
            raise ValueError(f"unknown quality distribution {self.quality!r}")
        if self.noise not in NOISE_DISTS:
            raise ValueError(f"unknown noise distribution {self.noise!r}")
        if self.scale != "custom" and self.scale not in SCALES:
            raise ValueError(f"unknown scale {self.scale!r}")
        if self.scale == "custom" and len(self.scale_points) < 2:
            raise ValueError("custom scale needs at least two points")
        if self.R < 1:
            raise ValueError("R must be at least 1")
        if not 0.0 <= self.careless < 1.0 or self.careless_kind not in CARELESS_KINDS:
            raise ValueError("careless must be in [0, 1) with kind 'rave' or 'random'")
        if self.sigma_award < 0:
            raise ValueError("sigma_award must be non-negative")

    def replace(self, **kw) -> "ReviewModel":
        d = asdict(self)
        d.update(kw)
        return ReviewModel(**d)

    @property
    def points(self) -> np.ndarray | None:
        if self.scale == "custom":
            return np.sort(np.asarray(self.scale_points, dtype=float))
        return SCALES[self.scale]

    @property
    def gaussian_shortcut(self) -> bool:
        """True when the mean score can be drawn in one step (handoff §9)."""
        return self.points is None and self.noise == "gaussian" and self.careless == 0

    @property
    def reliability(self) -> float:
        """rho^2 = corr(score, quality)^2 for continuous scores (any noise shape).

        Snapping changes the effective noise, so for a discrete scale this is the
        reliability of the latent (unsnapped) mean only.
        """
        var_noise = self.sigma_u**2 + self.sigma_eps**2 / self.R
        return self.sigma_q**2 / (self.sigma_q**2 + var_noise)

    @property
    def award_reliability(self) -> float:
        """corr(a1, a2) of two committees' award orderings, ignoring truncation to the accepted set:
        sigma_q^2 / (sigma_q^2 + sigma_u^2 + sigma_eps^2 / R + sigma_award^2) for continuous scores."""
        var_noise = self.sigma_u**2 + self.sigma_eps**2 / self.R + self.sigma_award**2
        return self.sigma_q**2 / (self.sigma_q**2 + var_noise)

    def as_dict(self) -> dict:
        d = asdict(self)
        d["scale_points"] = ",".join(f"{p:g}" for p in self.scale_points)
        if self.careless == 0:  # keep the seeds and CSV rows of every earlier model unchanged
            d.pop("careless")
            d.pop("careless_kind")
        if self.sigma_award == 0:
            d.pop("sigma_award")
        return d


# ---------------------------------------------------------------------------
# Quality distributions (handoff §3.3): all have mean mu_q and SD sigma_q.
# ---------------------------------------------------------------------------


def beta_shape(sigma_q: float) -> float:
    """a such that 9 * Beta(a, a) has SD sigma_q (SD of 9 Beta(a,a) is 4.5/sqrt(2a+1))."""
    a = ((4.5 / sigma_q) ** 2 - 1.0) / 2.0
    if a <= 0:
        raise ValueError("sigma_q too large for a Beta(a,a) on a width-9 interval")
    return a


def lognormal_params(mu_q: float, sigma_q: float) -> tuple[float, float]:
    s2 = np.log1p((sigma_q / mu_q) ** 2)
    return np.log(mu_q) - s2 / 2.0, np.sqrt(s2)


def sample_quality(rng: np.random.Generator, shape, m: ReviewModel) -> np.ndarray:
    mu, sd = m.mu_q, m.sigma_q
    if m.quality == "gaussian":
        return mu + sd * rng.standard_normal(shape)
    if m.quality == "beta":
        a = beta_shape(sd)
        return mu - 4.5 + 9.0 * rng.beta(a, a, size=shape)
    if m.quality == "exp":
        return mu - sd + sd * rng.standard_exponential(shape)
    if m.quality == "t3":
        return mu + sd * rng.standard_t(3, size=shape) / np.sqrt(3.0)
    if m.quality == "lognormal":
        lm, ls = lognormal_params(mu, sd)
        return np.exp(lm + ls * rng.standard_normal(shape))
    raise AssertionError(m.quality)


def quality_cdf(q: np.ndarray, m: ReviewModel) -> np.ndarray:
    """Population CDF F(q): the true percentile of quality q (used for 'mean true percentile')."""
    mu, sd = m.mu_q, m.sigma_q
    if m.quality == "gaussian":
        return special.ndtr((q - mu) / sd)
    if m.quality == "beta":
        a = beta_shape(sd)
        return special.betainc(a, a, np.clip((q - mu + 4.5) / 9.0, 0.0, 1.0))
    if m.quality == "exp":
        return -np.expm1(-np.maximum(q - mu + sd, 0.0) / sd)
    if m.quality == "t3":
        return stats.t.cdf((q - mu) * np.sqrt(3.0) / sd, 3)
    if m.quality == "lognormal":
        lm, ls = lognormal_params(mu, sd)
        return special.ndtr((np.log(q) - lm) / ls)
    raise AssertionError(m.quality)


# ---------------------------------------------------------------------------
# Scores
# ---------------------------------------------------------------------------


def snap(x: np.ndarray, points: np.ndarray) -> np.ndarray:
    """Snap each value to the nearest scale point (ties at midpoints go up)."""
    mids = (points[:-1] + points[1:]) / 2.0
    return points[np.searchsorted(mids, x, side="right")]


def _noise(rng: np.random.Generator, shape, m: ReviewModel) -> np.ndarray:
    if m.noise == "gaussian":
        return m.sigma_eps * rng.standard_normal(shape)
    return m.sigma_eps * rng.standard_t(3, size=shape) / np.sqrt(3.0)


def sample_scores(rng: np.random.Generator, q: np.ndarray, m: ReviewModel) -> np.ndarray:
    """One committee's mean scores for papers of quality q (any array shape).

    A second committee is a second call with the same q: it redraws u and eps.
    """
    if m.gaussian_shortcut:
        sd = np.sqrt(m.sigma_u**2 + m.sigma_eps**2 / m.R)
        return q + sd * rng.standard_normal(q.shape)
    base = q
    if m.sigma_u > 0:
        base = q + m.sigma_u * rng.standard_normal(q.shape)
    reviews = base[..., None] + _noise(rng, q.shape + (m.R,), m)
    pts = m.points
    if m.careless > 0:
        lo, hi = (1.0, 10.0) if pts is None else (float(pts[0]), float(pts[-1]))
        if m.careless_kind == "rave":
            junk = np.full(reviews.shape, hi)
        elif pts is None:
            junk = rng.uniform(lo, hi, size=reviews.shape)
        else:
            junk = rng.choice(pts, size=reviews.shape)
        reviews = np.where(rng.random(reviews.shape) < m.careless, junk, reviews)
    if pts is not None:
        reviews = snap(reviews, pts)
    return reviews.mean(axis=-1)


def jitter(rng: np.random.Generator, s: np.ndarray, m: ReviewModel) -> np.ndarray:
    """Add a negligible uniform jitter so ranking breaks ties uniformly at random.

    The jitter is far below the smallest possible gap between two distinct mean
    scores (min gap between scale points divided by R), so it only reorders ties.
    """
    pts = m.points
    width = 1e-9 if pts is None else 1e-6 * float(np.min(np.diff(pts))) / m.R
    return s + width * rng.random(s.shape)


def award_order(rng: np.random.Generator, s: np.ndarray, m: ReviewModel, n_accepted: int) -> np.ndarray:
    """The award ordering of one committee: the score plus the chairs' award noise within the accepted set.

    `s` holds the (jittered) scores, one row per conference; `n_accepted` is the number of accepted papers (Accepted or Better).
    Returns t with t = s + eta for the accepted papers (the top `n_accepted` by s) and t = s - 100 for the
    rest, so that the top-K of t for any K <= n_accepted is the top K chosen by s + eta among the
    accepted papers, the top `n_accepted` of t is the accepted set itself, and ranks beyond it follow s.
    With sigma_award = 0 the scores are returned unchanged and no random numbers are drawn.
    """
    if m.sigma_award == 0:
        return s
    N = s.shape[-1]
    A = int(n_accepted)
    if not 1 <= A <= N:
        raise ValueError(f"n_accepted must be in [1, N]; got {A} for N = {N}")
    thr = np.partition(s, N - A, axis=-1)[..., N - A][..., None]
    t = s + m.sigma_award * rng.standard_normal(s.shape)
    return np.where(s >= thr, t, s - 100.0)
