"""Generative model of conference peer review (handoff §3).

Paper i has true quality q_i and receives R reviews s_ij = q_i + u_i + eps_ij.
u_i is noise shared by everyone who handles the paper; eps_ij is a reviewer's own
error. Each review is optionally snapped to a score scale before averaging. The
paper's score is the mean of its R (snapped) reviews.

Everything lives on a latent 1-to-10 axis.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass

import numpy as np
from scipy import special, stats

# Score scales on the latent 1-to-10 axis (handoff §3.2). "iclr4" is ICLR 2020.
SCALES: dict[str, np.ndarray | None] = {
    "continuous": None,
    "int10": np.arange(1.0, 11.0),
    "six": np.linspace(1.0, 10.0, 6),
    "iclr6": np.array([1.0, 3.0, 5.0, 6.0, 8.0, 10.0]),
    "five": np.linspace(1.0, 10.0, 5),
    "iclr4": np.array([1.0, 3.0, 6.0, 8.0]),
}
QUALITY_DISTS = ("gaussian", "beta", "exp", "t3", "lognormal")
NOISE_DISTS = ("gaussian", "t3")


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
        return self.points is None and self.noise == "gaussian"

    @property
    def reliability(self) -> float:
        """rho^2 = corr(score, quality)^2 for continuous scores (any noise shape).

        Snapping changes the effective noise, so for a discrete scale this is the
        reliability of the latent (unsnapped) mean only.
        """
        var_noise = self.sigma_u**2 + self.sigma_eps**2 / self.R
        return self.sigma_q**2 / (self.sigma_q**2 + var_noise)

    def as_dict(self) -> dict:
        d = asdict(self)
        d["scale_points"] = ",".join(f"{p:g}" for p in self.scale_points)
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
