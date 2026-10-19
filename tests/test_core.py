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
    # Committee 2's scores correlate with committee 1's at rho^2, so the rerun probabilities of a top-M set are
    # the true-rank integrals at correlation rho^2, and the true-rank ones those at rho; the same for
    # one paper and for the three of the paper (the share of them inside the top M).
    for n_best in (1, 3):
        row = simulate_best_paper(m, N, reps=6000, best_K=(1,), best_papers_cuts={"best": 3, "top10": 10, "accept_or_better": A},
                                  second_committee=True, n_best=n_best)
        for name, M in (("best", 3), ("top10", 10), ("accept_or_better", A)):
            exact = an.containment_fixed_K(N, n_best, M, rho2)
            assert abs(row[f"best_papers_in2_{name}"] - exact) < 4 * row[f"best_papers_in2_{name}_se"] + 1e-3
        exact = an.containment_fixed_K(N, n_best, 10, np.sqrt(rho2))
        assert abs(row["best_papers_in_top10"] - exact) < 4 * row["best_papers_in_top10_se"] + 1e-3
        assert row["best_papers_rank2_median"] > row["best_papers_rank_median"]


def test_tier_size_fit_recovers_power_law():
    import pandas as pd
    from peerreview.tiers import fit_tier_sizes, fitted_count
    N = np.array([1000, 2000, 5000, 10_000, 20_000], float)
    counts = pd.DataFrame(dict(venue="NeurIPS", year=np.arange(2014, 2019), N_used=N, acc_rate_used=0.25,
                               orals_used=0.3 * N**0.6, spotlights=0.5 * N**0.8,
                               awards_used=[3, 3, 3, 3, np.nan]))
    f = fit_tier_sizes(counts)
    a, o, s, w = (f[f.series == t].iloc[0] for t in ("accept_or_better", "oral_or_better", "spot", "best"))
    assert abs(a.gamma - 1.0) < 1e-9 and abs(a.a - 0.25) < 1e-9
    assert abs(o.gamma - 0.6) < 1e-9 and abs(o.a - 0.3) < 1e-9 and o.n_years == 5
    assert abs(s.gamma - 0.8) < 1e-9 and abs(s.a - 0.5) < 1e-9
    assert abs(w.gamma) < 1e-9 and abs(w.a - 3) < 1e-9 and w.n_years == 4  # a fixed number: gamma = 0
    assert fitted_count(f, "oral_or_better", 10_000) == round(0.3 * 10_000**0.6)


def test_tier_overlap_closed_form_matches_exact_from_30():
    # make_tier_scaling.py switches from the exact 2-D integral to the closed form at M = 30.
    r2 = 0.5038
    for N in (1000, 10_000):
        exact = an.precision_fixed_K(N, 30, r2)
        approx = an.precision_pct_finite(N, 30 / N, r2)
        assert abs(approx / exact - 1) < 2e-3


def test_tiers_are_separate():
    from peerreview.tiers import add_separate, bands, cuts
    c = cuts(3, 17, 48, 250)
    assert c == {"best": 3, "oral_or_better": 17, "spot_or_better": 65, "accept_or_better": 250}
    b = bands(c, 1000)
    assert b == {"best": (0, 3), "oral": (3, 17), "spot": (17, 65), "accept": (65, 250), "reject": (250, 1000)}
    assert "spot" not in bands(cuts(3, 45, float("nan"), 568), 2403)  # no Spotlight count, no Spotlight tier
    r = add_separate({"p2_best": 0.1, "p2_oral_or_better": 0.3, "p2_spot_or_better": 0.6, "p2_accept_or_better": 0.9}, "p2")
    assert np.isclose(r["p2_oral"], 0.2) and np.isclose(r["p2_spot"], 0.3) and np.isclose(r["p2_accept"], 0.3)
    assert np.isclose(r["p2_reject"], 0.1)
    assert np.isclose(sum(r[f"p2_{t}"] for t in ("best", "oral", "spot", "accept", "reject")), 1.0)


def test_placement_is_separate_and_matches_overlap():
    from peerreview.simulate import simulate_best_paper
    from peerreview.model import ReviewModel, MAIN_FORM
    from peerreview.tiers import add_separate, cuts
    m = ReviewModel(**MAIN_FORM, sigma_eps=2.0)
    cut_sizes = cuts(3, 17, 48, 250)
    r = simulate_best_paper(m, 1000, reps=100, best_K=(1,), seed=3, best_papers_cuts=cut_sizes, second_committee=True,
                            overlap_cuts=cut_sizes, place=True, n_best=3)
    for x in ("best", "oral", "spot", "accept"):
        assert r[f"place_{x}_in_{x}"] == r[f"overlap_{x}"]  # a paper keeps its own tier with the tier's overlap
        assert np.isclose(sum(r[f"place_{x}_in_{y}"] for y in ("best", "oral", "spot", "accept", "reject")), 1.0)  # one tier each
    add_separate(r, "best_papers_in2")
    for y in ("best", "oral", "spot", "accept", "reject"):  # the lean Best Papers path and the placement path agree
        assert abs(r[f"best_papers_in2_{y}"] - r[f"place_best_in_{y}"]) < 1e-12
    assert abs(r["overlap_best"] - r["best_papers_in2_best"]) < 1e-12


def test_award_step():
    import numpy as np
    from peerreview.model import ReviewModel, award_order
    from peerreview.simulate import simulate_best_paper
    rng = np.random.default_rng(1)
    s = rng.normal(5, 1.5, (4, 200))
    m0 = ReviewModel(R=4, scale="int10", sigma_eps=2.0)
    assert award_order(rng, s, m0, 50) is s and "sigma_award" not in m0.as_dict()  # no award noise: the score ordering
    m = m0.replace(sigma_award=0.6)
    t = award_order(rng, s, m, 50)
    for row_s, row_t in zip(s, t):
        acc, acc_t = set(np.argsort(-row_s)[:50]), set(np.argsort(-row_t)[:50])
        assert acc == acc_t  # acceptance is by the score
        rej = np.argsort(-row_s)[50:]
        assert list(np.argsort(-row_t)[50:]) == list(rej)  # rejected papers keep their score order
    # with sigma_award = 0 the simulator is unchanged (same seed, same numbers)
    cut_sizes = {"best": 3, "oral_or_better": 17, "spot_or_better": 65, "accept_or_better": 250}
    a = simulate_best_paper(m0, 1000, reps=50, best_K=(1,), seed=5, best_papers_cuts=cut_sizes, second_committee=True, overlap_cuts=cut_sizes)
    b = simulate_best_paper(m0, 1000, reps=50, best_K=(1,), seed=5, best_papers_cuts=cut_sizes, second_committee=True, overlap_cuts=cut_sizes, n_accepted=100)  # no award noise: the size does not matter
    assert a["overlap_spot"] == b["overlap_spot"] and a["best_papers_in2_best"] == b["best_papers_in2_best"]
    # award noise lowers the award overlaps and leaves the acceptance overlap
    c = simulate_best_paper(m0.replace(sigma_award=1.0), 1000, reps=200, best_K=(1,), seed=5, best_papers_cuts=cut_sizes, second_committee=True, overlap_cuts=cut_sizes)
    d = simulate_best_paper(m0, 1000, reps=200, best_K=(1,), seed=5, best_papers_cuts=cut_sizes, second_committee=True, overlap_cuts=cut_sizes)
    assert c["overlap_oral"] < d["overlap_oral"] and c["overlap_best"] < d["overlap_best"]
    assert abs(c["overlap_accept_or_better"] - d["overlap_accept_or_better"]) < 0.03
