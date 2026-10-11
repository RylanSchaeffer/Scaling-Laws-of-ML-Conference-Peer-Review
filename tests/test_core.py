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


def test_second_committee_matches_closed_forms():
    from peerreview.simulate import simulate_best_paper
    m = ReviewModel(R=3, sigma_eps=2.0)
    rho2 = m.reliability
    N, A = 2000, 500
    row = simulate_best_paper(m, N, reps=6000, best_K=(1,), winner_tiers={"top10": 10, "accept": A}, second_committee=True)
    # Committee 2's scores correlate with committee 1's at rho^2, so the rerun tiers are the
    # true-rank integrals at correlation rho^2, and the true-rank tiers those at rho.
    for name, M, c in (("top10", 10, rho2), ("accept", A, rho2)):
        exact = an.containment_fixed_K(N, 1, M, c)
        assert abs(row[f"winner_in2_{name}"] - exact) < 4 * row[f"winner_in2_{name}_se"] + 1e-3
    exact = an.containment_fixed_K(N, 1, 10, np.sqrt(rho2))
    assert abs(row["winner_in_top10"] - exact) < 4 * row["winner_in_top10_se"] + 1e-3
    assert row["winner_rank2_median"] > row["winner_rank_median"]


def test_tier_size_fit_recovers_power_law():
    import pandas as pd
    from peerreview.tiers import fit_tier_sizes, tier_size
    N = np.array([1000, 2000, 5000, 10_000, 20_000], float)
    counts = pd.DataFrame(dict(venue="NeurIPS", year=np.arange(2014, 2019), N_used=N, acc_rate_used=0.25,
                               orals_used=0.3 * N**0.6, spotlights=0.5 * N**0.8, awards=[3, 3, 3, 3, np.nan]))
    f = fit_tier_sizes(counts)
    a, o, s, w = (f[f.tier == t].iloc[0] for t in ("accepted", "orals", "spotlights", "awards"))
    assert abs(a.gamma - 1.0) < 1e-9 and abs(a.a - 0.25) < 1e-9
    assert abs(o.gamma - 0.6) < 1e-9 and abs(o.a - 0.3) < 1e-9 and o.n_years == 5
    assert abs(s.gamma - 0.8) < 1e-9 and abs(s.a - 0.5) < 1e-9
    assert abs(w.gamma) < 1e-9 and abs(w.a - 3) < 1e-9 and w.n_years == 4  # a fixed number: gamma = 0
    assert tier_size(f, "orals", 10_000) == round(0.3 * 10_000**0.6)


def test_tier_overlap_closed_form_matches_exact_from_30():
    # make_tier_scaling.py switches from the exact 2-D integral to the closed form at M = 30.
    r2 = 0.5038
    for N in (1000, 10_000):
        exact = an.precision_fixed_K(N, 30, r2)
        approx = an.precision_pct_finite(N, 30 / N, r2)
        assert abs(approx / exact - 1) < 2e-3


def test_placement_matches_overlap_and_nests():
    from peerreview.simulate import simulate_best_paper
    from peerreview.model import ReviewModel, MAIN_FORM
    m = ReviewModel(**MAIN_FORM, sigma_eps=2.0)
    tiers = {"best": 1, "top10": 10, "oral": 17, "spot": 65, "accept": 250}
    r = simulate_best_paper(m, 1000, reps=100, best_K=(1,), seed=3, winner_tiers={"best": 1}, second_committee=True,
                            overlap_tiers=tiers, place_tiers={"oral": 17, "spot": 65, "accept": 250})
    for k in ("oral", "spot", "accept"):
        assert r[f"place_{k}_in_{k}"] == r[f"overlap_{k}"]  # a paper keeps its own tier with the tier's overlap
    # tiers nest, so the chance of a tier or higher grows with the tier
    assert r["place_oral_in_oral"] <= r["place_oral_in_spot"] <= r["place_oral_in_accept"] <= 1
    assert r["place_spot_in_spot"] <= r["place_spot_in_accept"]
