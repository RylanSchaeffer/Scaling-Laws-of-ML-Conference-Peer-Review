"""ICLR public-review pipeline (handoff §8.2 steps 1 to 3, §8.3, §10.2, §10.3).

Run from the repo root:  uv run python scripts/iclr_data.py [--use-cache] [--splits 200]

Steps
  1. Download every year's paperlists dump (2017 to 2025; 2026 if available) and
     parse them into data/processed/iclr_papers.csv.gz (re-parsed unless --use-cache).
  2. Sanity checks, printed and written:
       results/iclr_pooled_pairs.csv  pooled 2017 to 2024 review-pair correlation (§10.2)
       results/iclr_score_values.csv  individual score counts per year and value,
                                      against handoff §10.3
       results/iclr_counts.csv        records per year and status, against §10.4
  3. results/iclr_variance.csv        §8.3 variance decomposition, decided main track
  4. results/iclr_splithalf_observed.csv  §8.2 split-half replay
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from peerreview import iclr  # noqa: E402
from peerreview.analytic import spearman_brown  # noqa: E402
from peerreview.simulate import stable_seed  # noqa: E402

RESULTS = ROOT / "results"

# Handoff §10.3: individual score counts in the dumps (all records).
HANDOFF_SCORE_COUNTS = {
    2021: dict(zip(range(1, 11), (14, 167, 905, 2289, 2685, 2832, 1999, 495, 112, 10))),
    2022: dict(zip((1, 3, 5, 6, 8, 10), (310, 3223, 3771, 3714, 2089, 54))),
    2023: dict(zip((1, 3, 5, 6, 8, 10), (465, 4711, 5126, 5326, 2846, 101))),
}
# Handoff §10.3: score value sets (2020 four-point; 2024 to 2025 from the reviewer guide).
HANDOFF_SCALE = {2020: (1, 3, 6, 8), 2024: (1, 3, 5, 6, 8, 10), 2025: (1, 3, 5, 6, 8, 10)}

# Handoff §10.4, ICLR rows: submissions N, acceptance rate, orals.
HANDOFF_VENUE = {
    2017: (507, 0.391, 15),
    2018: (981, 0.320, 23),
    2019: (1591, 0.314, 24),
    2020: (2594, 0.265, 48),
    2021: (2997, 0.287, 53),
    2022: (3328, 0.329, 54),
    2023: (4938, 0.318, 91),
    2024: (7262, 0.311, 86),
    2025: (11603, 0.319, 213),
    2026: (19525, 0.274, 224),
}
# 2026 extra counts (§10.4): desk-rejected, withdrawn, decided, accepted.
HANDOFF_2026 = {"desk_reject": 779, "withdrawn": 5042, "decided": 13763, "accepted": 5355}

# Handoff §10.2: own decomposition of the dumps.
HANDOFF_ICC = {2017: 0.58, 2018: 0.41, 2019: 0.46, 2020: 0.39}

MIN_SPLITHALF_PAPERS = 500  # years with fewer kept papers are skipped (2017 to 2020)
# Rows for 2026 are written with in_main=False (see the peerreview.iclr docstring).


def _print(df: pd.DataFrame, title: str, floatfmt: str = "{:.3f}") -> None:
    print(f"\n== {title} ==")
    with pd.option_context("display.width", 250, "display.max_columns", 60, "display.max_rows", 200):
        print(df.to_string(index=False, float_format=lambda x: floatfmt.format(x)))


def check_avg_field(papers: pd.DataFrame) -> pd.DataFrame:
    """Compare parsed means with the dumps' own *_avg field."""
    rows = []
    for y in sorted(papers["year"].unique()):
        recs = iclr.read_records(int(y))
        ref = {}
        for r in recs:
            f = iclr.score_field(r)
            v = r.get(f"{f}_avg")
            v = v[0] if isinstance(v, list) else v
            ref[str(r["id"])] = float(v) if v is not None else np.nan
        sub = papers[(papers["year"] == y) & (papers["n_reviews"] > 0)]
        d = np.abs(sub["mean_rating"].to_numpy() - sub["paper_id"].map(ref).to_numpy())
        rows.append({"year": y, "papers_with_reviews": len(sub), "max_abs_diff_vs_avg_field": float(np.nanmax(d))})
    return pd.DataFrame(rows)


def score_value_table(papers: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for y, g in papers.groupby("year"):
        all_v = np.concatenate([x for x in iclr.scores_list(g) if len(x)])
        dm = g[g["decided"] & g["main_track"]]
        dec_v = np.concatenate([x for x in iclr.scores_list(dm) if len(x)])
        vals, cnt = np.unique(all_v, return_counts=True)
        dvals, dcnt = np.unique(dec_v, return_counts=True)
        dmap = dict(zip(dvals, dcnt))
        ref = HANDOFF_SCORE_COUNTS.get(int(y), {})
        for v, c in zip(vals, cnt):
            h = ref.get(int(v), np.nan) if ref else np.nan
            rows.append(
                {
                    "year": int(y),
                    "value": float(v),
                    "count_all": int(c),
                    "count_decided_main": int(dmap.get(v, 0)),
                    "handoff_count": h,
                    "match": (bool(int(c) == h) if ref else None),
                }
            )
    return pd.DataFrame(rows)


def counts_table(papers: pd.DataFrame, raw_counts: dict[int, int], raw_fields: dict[int, str]) -> pd.DataFrame:
    rows = []
    for y, g in papers.groupby("year"):
        y = int(y)
        st = g["status"].value_counts()
        N_h, rate_h, orals_h = HANDOFF_VENUE.get(y, (np.nan, np.nan, np.nan))
        acc = int(g["accepted"].sum())
        dec = int(g["decided"].sum())
        row = {
            "year": y,
            "scale": iclr.scale_label(y),
            "in_main": y in iclr.YEARS_MAIN,
            "score_field": raw_fields[y],
            "records_raw": raw_counts[y],
            "records": len(g),
            "duplicates_dropped": raw_counts[y] - len(g),
            **{s: int(st.get(s, 0)) for s in iclr.STATUSES},
            "workshop_raw": int((g["status_raw"] == "Workshop").sum()),
            "conditional_raw": int(g["status_raw"].str.contains("Conditional").sum()),
            "main_track": int(g["main_track"].sum()),
            "no_reviews": int((g["n_reviews"] == 0).sum()),
            "decided": dec,
            "accepted": acc,
            "accept_rate_decided": acc / dec,
            "decided_with_ge4": int((g["decided"] & (g["n_reviews"] >= 4)).sum()),
            "handoff_N": N_h,
            "handoff_rate": rate_h,
            "accepted_over_handoff_N": acc / N_h,
            "handoff_orals": orals_h,
            "orals_minus_handoff": int(st.get("oral", 0)) - orals_h,
        }
        rows.append(row)
    return pd.DataFrame(rows)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--use-cache", action="store_true", help="read data/processed/iclr_papers.csv.gz if present")
    ap.add_argument("--splits", type=int, default=200)
    ap.add_argument("--boot", type=int, default=200, help="bootstrap resamples for the ICC(1) SE")
    args = ap.parse_args()
    t0 = time.time()
    RESULTS.mkdir(exist_ok=True)

    # 1. Download and parse.
    years = list(iclr.YEARS_MAIN) + list(iclr.YEARS_EXTRA)
    for y in years:
        p = iclr.download(y)
        print(f"raw {y}: {p.relative_to(ROOT)} ({p.stat().st_size / 1e6:.1f} MB)")
    papers = iclr.load_papers(refresh=not args.use_cache)
    print(f"processed: {iclr.CACHE_PATH.relative_to(ROOT)}  rows={len(papers)}  years={sorted(papers.year.unique())}")
    raw_counts, raw_fields = {}, {}
    for y in sorted(papers["year"].unique()):
        recs = iclr.read_records(int(y))
        raw_counts[int(y)] = len(recs)
        fields = pd.Series([iclr.score_field(r) for r in recs if r.get(iclr.score_field(r))]).value_counts()
        raw_fields[int(y)] = ";".join(f"{k}:{v}" for k, v in fields.items())

    # Round trip of the cache.
    back = iclr.read_cache()
    assert back.shape == papers.shape and (back["ratings"] == papers["ratings"]).all(), "cache round trip failed"

    # 2. Sanity checks.
    _print(check_avg_field(papers), "parsed mean vs the dump's own *_avg field", "{:.2e}")

    sv = score_value_table(papers)
    sv.to_csv(RESULTS / "iclr_score_values.csv", index=False)
    wide = sv.pivot(index="year", columns="value", values="count_all").fillna(0).astype(int)
    wide.columns = [f"{c:g}" for c in wide.columns]
    _print(wide.reset_index(), "individual score counts, all records (handoff §10.3)")
    for y, ref in HANDOFF_SCORE_COUNTS.items():
        s = sv[sv.year == y]
        same_set = set(s["value"].astype(int)) == set(ref)
        print(f"  {y}: value set matches handoff: {same_set}; every count matches: {bool(s['match'].all())}")
    for y, pts in HANDOFF_SCALE.items():
        got = tuple(int(v) for v in sv[sv.year == y]["value"])
        print(f"  {y}: values {got}; handoff scale {pts}; match: {got == pts}")
    for y in sorted(papers.year.unique()):
        got = tuple(sv[sv.year == y]["value"])
        print(f"  {y}: observed values within SCALES[{y}]: {set(got) <= set(iclr.SCALES[int(y)])}")

    ct = counts_table(papers, raw_counts, raw_fields)
    ct.to_csv(RESULTS / "iclr_counts.csv", index=False)
    _print(ct.drop(columns=["score_field"]), "records per year and status vs handoff §10.4")
    print("  score field used (records with scores): " + ", ".join(f"{y} {f}" for y, f in raw_fields.items()))
    g26 = papers[papers.year == 2026]
    if len(g26):
        st = g26["status"].value_counts()
        print(
            "  2026 vs handoff: desk_reject {} vs {}; withdrawn {} vs {}; decided {} vs {}; accepted {} vs {}".format(
                int(st.get("desk_reject", 0)),
                HANDOFF_2026["desk_reject"],
                int(st.get("withdrawn", 0)),
                HANDOFF_2026["withdrawn"],
                int(g26["decided"].sum()),
                HANDOFF_2026["decided"],
                int(g26["accepted"].sum()),
                HANDOFF_2026["accepted"],
            )
        )

    # 3. Variance decomposition, decided main-track papers.
    vrows = []
    for y, g in papers.groupby("year"):
        y = int(y)
        dm = g[g["decided"] & g["main_track"]]
        seed = stable_seed("iclr_icc_boot", y)
        row = {"year": y, "scale": iclr.scale_label(y), "in_main": y in iclr.YEARS_MAIN, "boot_seed": seed}
        row.update(iclr.variance_decomposition(dm, n_boot=args.boot, seed=seed))
        row["sb_rel_mean_reviews"] = float(spearman_brown(row["icc1"], row["mean_reviews"]))
        # All reviewed main-track records (any status), the subset the handoff's ICC used.
        allr = g[g["main_track"] & (g["n_reviews"] >= 1)]
        a = iclr.anova_icc(iclr.scores_list(allr))
        row.update(
            n_papers_all_reviewed=len(allr),
            icc1_all_reviewed=float(a["icc1"]),
            sd_between_all_reviewed=float(np.sqrt(max(a["var_between"], 0))),
            sd_within_all_reviewed=float(np.sqrt(a["var_within"])),
            mean_paper_avg_all_reviewed=float(allr["mean_rating"].mean()),
            sd_paper_avg_all_reviewed=float(allr["mean_rating"].std(ddof=1)),
            handoff_icc1=HANDOFF_ICC.get(y, np.nan),
        )
        vrows.append(row)
    var = pd.DataFrame(vrows)
    var.to_csv(RESULTS / "iclr_variance.csv", index=False)
    _print(
        var[
            [
                "year",
                "scale",
                "n_papers",
                "mean_reviews",
                "share_ge4_reviews",
                "sd_between",
                "sd_within",
                "icc1",
                "icc1_se",
                "pair_corr",
                "pair_corr_pooled",
                "icc1_all_reviewed",
                "handoff_icc1",
            ]
        ],
        "variance decomposition, decided main track (§8.3)",
    )
    _print(
        var[
            [
                "year",
                "accept_rate",
                "mean_paper_avg",
                "sd_paper_avg",
                "mean_paper_avg_all_reviewed",
                "sd_paper_avg_all_reviewed",
                "mean_avg_accepted",
                "sd_avg_accepted",
                "mean_avg_rejected",
                "sd_avg_rejected",
                "mean_avg_poster",
                "mean_avg_spotlight",
                "mean_avg_oral",
            ]
        ],
        "paper-average scores, decided main track",
    )
    _print(
        var[
            [
                "year",
                "threshold_logit",
                "threshold_logit_se",
                "logit_slope",
                "threshold_binned",
                "cutoff_topA",
                "mean_rule_precision",
                "sb_rel_mean_reviews",
            ]
        ],
        "decision threshold in mean score",
    )

    # Pooled 2017 to 2024 pair correlation, against the berenslab figure (§10.2:
    # r = 0.40 over 244,226 review pairs, 3.7 reviews per paper).
    prow = []
    for label, sel in (("all_reviewed", papers["n_reviews"] >= 2), ("decided", (papers["n_reviews"] >= 2) & papers["decided"])):
        g = papers[sel & papers["main_track"] & papers["year"].between(2017, 2024)]
        groups = iclr.scores_list(g)
        n = np.array([len(x) for x in groups])
        prow.append(
            {
                "subset": label,
                "years": "2017-2024",
                "papers": len(g),
                "ordered_pairs": int((n * (n - 1)).sum()),
                "mean_reviews": float(n.mean()),
                "pair_corr_pooled": iclr.pair_correlation(groups, "pair"),
                "pair_corr_paper_weighted": iclr.pair_correlation(groups, "paper"),
                "handoff_r": 0.40,
                "handoff_pairs": 244226,
            }
        )
    pooled = pd.DataFrame(prow)
    pooled.to_csv(RESULTS / "iclr_pooled_pairs.csv", index=False)
    _print(pooled, "pooled 2017-2024 review-pair correlation vs berenslab (§10.2)")

    # 4. Split-half replay.
    srows = []
    for y, g in papers.groupby("year"):
        y = int(y)
        dm = g[g["decided"] & g["main_track"]]
        n_kept = int((dm["n_reviews"] >= 4).sum())
        if n_kept < MIN_SPLITHALF_PAPERS:
            print(f"split-half {y}: skipped, {n_kept} decided main-track papers with >= 4 reviews")
            continue
        seed = stable_seed("iclr_splithalf", y)
        row = {"year": y, "scale": iclr.scale_label(y), "in_main": y in iclr.YEARS_MAIN, "seed": seed}
        row.update(iclr.split_half(dm, n_splits=args.splits, seed=seed))
        srows.append(row)
    sh = pd.DataFrame(srows)
    sh.to_csv(RESULTS / "iclr_splithalf_observed.csv", index=False)
    main_m = [m for m in iclr.SPLIT_METRICS if not m.startswith("n_ge")]
    cols = ["year", "scale", "n_kept", "A", "accept_rate_kept"]
    cols += [f"{m}_{s}" for m in main_m for s in ("mean", "sd")] + ["sb_pred_corr_halves"]
    _print(sh[cols], "split-half replay, decided main track with >= 4 reviews (§8.2)")
    tie = ["year", "A", "n_ge_cut_A_mean", "n_ge_cut_top10_mean", "n_ge_cut_top30_mean", "n_ge_cut_top3_mean"]
    _print(sh[tie], "papers at or above each half-1 cut (tie blocks)", "{:.1f}")
    print(f"\nwrote results/iclr_score_values.csv, iclr_counts.csv, iclr_pooled_pairs.csv, iclr_variance.csv, iclr_splithalf_observed.csv "
          f"({time.time() - t0:.0f} s)")


if __name__ == "__main__":
    main()
