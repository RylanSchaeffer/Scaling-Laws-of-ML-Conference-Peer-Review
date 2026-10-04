"""Core checks: distributions, snapping, simulator against closed forms."""

import numpy as np
import pytest
from scipy import stats

from peerreview import analytic as an
from peerreview.model import QUALITY_DISTS, ReviewModel, quality_cdf, sample_quality, snap
from peerreview.simulate import Selections, simulate


@pytest.mark.parametrize("dist", QUALITY_DISTS)
def test_quality_moments_and_cdf(dist):
    m = ReviewModel(quality=dist)
    q = sample_quality(np.random.default_rng(1), 400_000, m)
    assert abs(q.mean() - 5.0) < 0.01
    assert abs(q.std() - 1.2) < (0.03 if dist == "t3" else 0.01)
    # CDF evaluated at the samples must be uniform.
    assert stats.kstest(quality_cdf(q[:20_000], m), "uniform").pvalue > 1e-3


def test_snap_nearest():
    pts = np.array([1.0, 3, 5, 6, 8, 10])
    x = np.array([-3.0, 1.9, 2.1, 5.4, 5.6, 6.9, 7.1, 9.2, 15.0])
    assert snap(x, pts).tolist() == [1, 1, 3, 5, 6, 6, 8, 10, 10]


def test_phi2_matches_scipy():
    rng = np.random.default_rng(0)
    for _ in range(50):
        h, k = rng.normal(0, 2, 2)
        r = rng.uniform(-0.95, 0.95)
        ref = stats.multivariate_normal([0, 0], [[1, r], [r, 1]]).cdf([h, k])
        assert abs(an.Phi2(h, k, r) - ref) < 1e-9


def test_simulator_matches_closed_forms():
    m = ReviewModel(R=3, sigma_eps=2.0)
    rho = np.sqrt(m.reliability)
    row = simulate(m, 5000, reps=2000, sel=Selections(fixed_K=(5,), pct=(0.01,)))
    for a in (0.1, 0.25, 0.4):
        assert abs(row[f"prec_acc{a:.2f}"] - an.precision_pct(a, rho)) < 4 * row[f"prec_acc{a:.2f}_se"] + 1e-3
        assert abs(row[f"dis_acc{a:.2f}"] - an.disagreement(a, rho**2)) < 4 * row[f"dis_acc{a:.2f}_se"] + 1e-3
    assert abs(row["corr_qs"] - rho) < 0.005
    assert abs(row["corr_s12"] - rho**2) < 0.005


def test_inversions_round_trip():
    for a in (0.1, 0.227, 0.4):
        for r in (0.2, 0.5, 0.8):
            assert abs(an.invert_disagreement(a, an.disagreement(a, r)) - r) < 1e-8
    se = an.sigma_eps_for_rho2(0.55, 3)
    assert abs(an.rho2(se, 3) - 0.55) < 1e-12


@pytest.mark.parametrize("kind, p10", [("rave", 0.05), ("random", 0.005)])
def test_careless_reviews(kind, p10):
    from peerreview.model import sample_scores
    m = ReviewModel(R=1, scale="int10", sigma_u=0.0, sigma_eps=0.01, careless=0.05, careless_kind=kind)
    s = sample_scores(np.random.default_rng(3), np.full(400_000, 5.0), m)
    # Careful reviews of a quality-5 paper give 5; a rave gives 10, a random review 1 to 10.
    assert abs((s == 10).mean() - p10) < 0.002
    assert abs((s != 5).mean() - (0.05 if kind == "rave" else 0.045)) < 0.002
    assert "careless" not in ReviewModel().as_dict() and m.as_dict()["careless"] == 0.05
    with pytest.raises(ValueError):
        ReviewModel(careless=0.05, careless_kind="sloppy")
