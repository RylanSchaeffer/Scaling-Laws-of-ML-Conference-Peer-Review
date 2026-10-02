"""Fast checks of the ICLR parser and analyses on tiny synthetic records (no network)."""

import json

import numpy as np
import pandas as pd
import pytest

from peerreview import iclr


def _records():
    # Shapes copied from the real dumps, plus label and separator variants.
    return [
        {"id": "a1", "track": "main", "status": "Oral", "rating": "6;8;8;10", "gs_citation": 12},
        {"id": "a2", "track": "main", "status": "Top-25%", "recommendation": "5;6;6;8", "gs_citation": 0},
        {"id": "a3", "track": "main", "status": "Poster", "rating": "6: Marginally above;5: below", "gs_citation": -1},
        {"id": "a4", "track": "main", "status": "Workshop", "rating": "", "gs_citation": None},
        {"id": "a5", "track": "Main", "status": "Withdraw", "rating": [3, "4", 5.5]},
        {"id": "a6", "track": "datasets", "status": "Desk Reject", "rating": "1|3"},
        {"id": "a7", "track": "main", "status": "ICLR 2026 ConditionalPoster", "rating": "2,4"},
        {"id": "a8", "track": "main", "status": "Active", "rating": 7},
        {"id": "a1", "track": "main", "status": "Oral", "rating": "6;8;8;10", "gs_citation": 12},  # repeat
        {"id": "a9", "track": "main", "status": "Talk", "rating": "8;6;6"},
        {"id": "b1", "track": "main", "status": "Top-5%", "recommendation": "", "rating": "3;3"},
    ]


def test_parse_scores_rules():
    assert iclr.parse_scores("4;5;6") == [4.0, 5.0, 6.0]
    assert iclr.parse_scores("") == [] and iclr.parse_scores(None) == []
    assert iclr.parse_scores("6: Marginally above acceptance threshold") == [6.0]
    assert iclr.parse_scores("8: Top 50% of accepted papers, clear accept") == [8.0]
    assert iclr.parse_scores("8: accept;3: reject") == [8.0, 3.0]
    assert iclr.parse_scores("1|3|10") == [1.0, 3.0, 10.0]
    assert iclr.parse_scores("1,3") == [1.0, 3.0]
    assert iclr.parse_scores([3, "4", 5.5, None, "n/a"]) == [3.0, 4.0, 5.5]
    assert iclr.parse_scores(7) == [7.0]
    assert iclr.parse_scores("abc;5") == [5.0]


@pytest.mark.parametrize(
    "raw, want",
    [
        ("Oral", "oral"),
        ("Talk", "oral"),
        ("Top-5%", "oral"),
        ("ICLR 2026 ConditionalOral", "oral"),
        ("Spotlight", "spotlight"),
        ("Top-25%", "spotlight"),
        ("Poster", "poster"),
        ("ICLR 2026 ConditionalPoster", "poster"),
        ("Reject", "reject"),
        ("Workshop", "reject"),
        ("Withdraw", "withdrawn"),
        ("Desk Reject", "desk_reject"),
        ("Active", "other"),
        ("", "other"),
        # OpenReview decision / venue strings (not in the current dumps).
        ("Accept (Oral)", "oral"),
        ("Accept (Talk)", "oral"),
        ("Accept (notable-top-5%)", "oral"),
        ("ICLR 2023 notable top 5%", "oral"),
        ("Accept (Spotlight)", "spotlight"),
        ("Accept (notable-top-25%)", "spotlight"),
        ("ICLR 2023 notable top 25%", "spotlight"),
        ("Accept (Poster)", "poster"),
        ("Accept: poster", "poster"),
        ("Accept", "poster"),
        ("Conditional Accept", "poster"),
        ("Invite to Workshop Track", "reject"),
        ("Rejected", "reject"),
        ("Withdrawn", "withdrawn"),
        ("ICLR 2018 Conference Withdrawn Submission", "withdrawn"),
        ("Desk Rejected", "desk_reject"),
        ("Desk Rejected Submission", "desk_reject"),
        ("Submitted to ICLR 2018", "other"),
    ],
)
def test_normalise_status(raw, want):
    assert iclr.normalise_status(raw) == want


def test_score_field_choice():
    assert iclr.score_field({"rating": "1;2"}) == "rating"
    assert iclr.score_field({"recommendation": "3;5"}) == "recommendation"
    assert iclr.score_field({"recommendation": "", "rating": "3;3"}) == "rating"


def test_parse_records_columns_and_flags():
    df = iclr.parse_records(_records(), 2099)
    assert list(df.columns) == list(iclr.COLUMNS)
    assert len(df) == 10  # the repeated a1 is dropped
    r = df.set_index("paper_id")
    assert r.loc["a1", "status"] == "oral" and r.loc["a1", "accepted"] and r.loc["a1", "decided"]
    assert r.loc["a1", "ratings"] == "6;8;8;10" and r.loc["a1", "n_reviews"] == 4
    assert r.loc["a1", "mean_rating"] == pytest.approx(8.0)
    assert r.loc["a1", "citations"] == 12.0
    assert r.loc["a2", "status"] == "spotlight" and r.loc["a2", "ratings"] == "5;6;6;8"
    assert r.loc["a3", "ratings"] == "6;5" and np.isnan(r.loc["a3", "citations"])
    assert r.loc["a4", "status"] == "reject" and r.loc["a4", "decided"] and not r.loc["a4", "accepted"]
    assert r.loc["a4", "ratings"] == "" and r.loc["a4", "n_reviews"] == 0 and np.isnan(r.loc["a4", "mean_rating"])
    assert r.loc["a5", "status"] == "withdrawn" and not r.loc["a5", "decided"]
    assert r.loc["a5", "ratings"] == "3;4;5.5" and r.loc["a5", "main_track"]
    assert r.loc["a6", "status"] == "desk_reject" and not r.loc["a6", "main_track"]
    assert r.loc["a7", "status"] == "poster" and r.loc["a7", "ratings"] == "2;4"
    assert r.loc["a8", "status"] == "other" and not r.loc["a8", "decided"] and r.loc["a8", "ratings"] == "7"
    assert r.loc["a9", "status"] == "oral" and r.loc["a9", "ratings"] == "8;6;6"
    assert r.loc["b1", "status"] == "oral" and r.loc["b1", "ratings"] == "3;3"
    assert r.loc["a1", "status_raw"] == "Oral" and r.loc["b1", "status_raw"] == "Top-5%"


def test_parse_year_and_cache_round_trip(tmp_path):
    raw = tmp_path / "raw"
    raw.mkdir()
    (raw / "iclr2099.json").write_text(json.dumps(_records()))
    df = iclr.parse_year(2099, raw_dir=raw, fetch=False)
    path = tmp_path / "papers.csv.gz"
    iclr.write_cache(df, path)
    back = iclr.read_cache(path)
    pd.testing.assert_frame_equal(back, df, check_dtype=False)
    assert back["ratings"].tolist() == df["ratings"].tolist()  # '' survives the round trip
    assert back["decided"].dtype == bool


def test_download_skips_existing_file(tmp_path):
    p = tmp_path / "iclr2099.json"
    p.write_text("[]")
    assert iclr.download(2099, raw_dir=tmp_path) == p  # no network call: the file is real


def test_anova_icc_balanced_closed_form():
    groups = [np.array([1.0, 3.0]), np.array([4.0, 6.0]), np.array([7.0, 9.0])]
    a = iclr.anova_icc(groups)
    # MSW = 2 (each pair differs by 2); MSB = 2 * var([2, 5, 8], ddof=1) = 18; n0 = 2.
    assert a["var_within"] == pytest.approx(2.0)
    assert a["var_between"] == pytest.approx((18 - 2) / 2)
    assert a["icc1"] == pytest.approx(8 / 10)
    # Groups with one value are ignored.
    assert iclr.anova_icc(groups + [np.array([100.0])])["icc1"] == pytest.approx(0.8)


def test_icc_and_pair_corr_recover_simulated_value():
    rng = np.random.default_rng(3)
    k, sb, sw = 4000, 1.0, 1.2
    m = rng.normal(5, sb, k)
    groups = [m[i] + rng.normal(0, sw, rng.integers(2, 6)) for i in range(k)]
    true = sb**2 / (sb**2 + sw**2)
    assert iclr.anova_icc(groups)["icc1"] == pytest.approx(true, abs=0.03)
    assert iclr.pair_correlation(groups, "paper") == pytest.approx(true, abs=0.03)
    assert iclr.pair_correlation(groups, "pair") == pytest.approx(true, abs=0.03)
    assert iclr.bootstrap_icc(groups, n_boot=20, seed=1).std() < 0.03


def test_decision_thresholds():
    rng = np.random.default_rng(0)
    x = rng.uniform(2, 9, 20_000)
    acc = rng.random(x.size) < 1 / (1 + np.exp(-3.0 * (x - 5.8)))
    lt = iclr.decision_threshold_logistic(x, acc)
    assert lt["threshold"] == pytest.approx(5.8, abs=4 * lt["threshold_se"] + 0.01)
    assert lt["slope"] == pytest.approx(3.0, rel=0.1)
    assert iclr.decision_threshold_binned(x, acc) == pytest.approx(5.8, abs=0.1)


def test_mean_rule_exact_tie_expectation():
    x = np.array([9.0, 8.0, 8.0, 8.0, 1.0])
    acc = np.array([True, True, False, False, False])  # A = 2
    r = iclr.mean_rule(x, acc)
    # Paper 0 is in; one of three tied papers fills the second slot, accepted with prob 1/3.
    assert r["cutoff"] == 8.0 and r["precision"] == pytest.approx((1 + 1 / 3) / 2)


def test_split_half_identical_reviews_agree():
    # Every paper's four reviews are equal and distinct across papers: both halves agree.
    scores = np.repeat(np.arange(40, dtype=float)[:, None], 4, axis=1)
    acc = np.zeros(40, bool)
    acc[-10:] = True
    d = iclr.split_half_draws(scores, acc, n_splits=7, seed=1, Ks=(5,))
    assert np.allclose(d["precision"], 1) and np.allclose(d["inconsistent"], 0)
    assert np.allclose(d["ovl_top5"], 1) and np.allclose(d["corr_halves"], 1)
    assert np.allclose(d["prec_vs_actual"], 1) and np.allclose(d["n_ge_cut_A"], 10)


def test_split_half_uses_two_plus_two_and_is_seeded():
    rng = np.random.default_rng(5)
    scores = rng.integers(1, 11, (300, 6)).astype(float)
    scores[::3, 4:] = np.nan  # some papers have exactly four reviews
    acc = rng.random(300) < 0.3
    d1 = iclr.split_half_draws(scores, acc, n_splits=30, seed=9)
    d2 = iclr.split_half_draws(scores, acc, n_splits=30, seed=9)
    for k in d1:
        np.testing.assert_array_equal(d1[k], d2[k])
    A = int(acc.sum())
    # Both halves accept exactly A, so inconsistent share = 2 A (1 - precision) / n.
    np.testing.assert_allclose(d1["inconsistent"], 2 * A * (1 - d1["precision"]) / 300)
    with pytest.raises(ValueError):
        iclr.split_half_draws(np.array([[1.0, 2, 3, np.nan]] * 5), np.array([1, 0, 0, 0, 0], bool))


def test_split_half_summary_on_frame():
    rng = np.random.default_rng(2)
    q = rng.normal(5, 1, 400)
    rows = []
    for i, qi in enumerate(q):
        n = 3 if i % 4 == 0 else 4
        s = np.clip(np.rint(qi + rng.normal(0, 1, n)), 1, 10).astype(int)
        rows.append({"id": f"p{i}", "track": "main", "status": "Poster" if qi > 5.5 else "Reject",
                     "rating": ";".join(map(str, s))})
    df = iclr.parse_records(rows, 2099)
    out = iclr.split_half(df, n_splits=20, seed=0)
    assert out["n_kept"] == 300 and out["A"] == int(df.loc[df.n_reviews >= 4, "accepted"].sum())
    assert 0 < out["precision_mean"] < 1 and out["precision_sd"] > 0
    assert out["corr_halves_mean"] == pytest.approx(out["sb_pred_corr_halves"], abs=0.08)
