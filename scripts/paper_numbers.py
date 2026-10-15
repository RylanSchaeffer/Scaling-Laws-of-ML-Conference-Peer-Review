"""Print every simulated number the paper quotes, from results/*.csv, in the order of the paper.

Usage: uv run python scripts/paper_numbers.py
"""
from __future__ import annotations

import json
import os

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES = os.path.join(ROOT, "results")
LEV = ("pessimistic", "central", "optimistic")


def load(name):
    return pd.read_csv(os.path.join(RES, f"{name}.csv"), keep_default_na=False, na_values=[""])


def pct(x, d=1):
    return f"{100 * x:.{d}f}%"


def at(df, N, col):
    """Log-N interpolation of a column of a frame sorted by N."""
    d = df.sort_values("N")
    return float(np.interp(np.log(N), np.log(d.N.values), d[col].values))


def exponent(df, col, lo=1e3, hi=1e5):
    d = df[(df.N >= lo) & (df.N <= hi)].sort_values("N")
    k, _ = np.polyfit(np.log(d.N.values), np.log(d[col].values), 1)
    return -k


def section(title):
    print(f"\n== {title}")


def main():
    b = load("best_paper")
    ven = b[b.source == "venue"]
    grid = b[b.source == "grid"]

    section("Fig 1c / Section results / sec:best: NeurIPS Best Paper under a second review (best_paper.csv venue rows)")
    for yr in (2014, 2021, 2026):
        for lev in LEV:
            r = ven[(ven.venue == "NeurIPS") & (ven.year == yr) & (ven.level == lev)]
            if r.empty:
                continue
            r = r.iloc[0]
            print(f"NeurIPS {yr} {lev:11s} N={int(r.N):6d} orals={int(r.orals)} spot={r.spotlights}: first {pct(r.p2_best, 2)} top10 {pct(r.p2_top10)} "
                  f"oral {pct(r.p2_oral)} spot {pct(r.p2_spot)} accept {pct(r.p2_accept)} merely {pct(r.p2_accept - r.p2_spot)} "
                  f"reject {pct(r.p2_reject)} median rank {r.winner_rank2_median:.0f} reps={int(r.reps)} reps_best={r.reps_best}")
    for v in ("ICML", "ICLR"):
        r = ven[(ven.venue == v) & (ven.year == 2026) & (ven.level == "central")]
        if not r.empty:
            r = r.iloc[0]
            print(f"{v} 2026 central N={int(r.N)} orals={int(r.orals)} spot={r.spotlights}: first {pct(r.p2_best, 2)} top10 {pct(r.p2_top10)} "
                  f"oral {pct(r.p2_oral)} spot {pct(r.p2_spot)} accept {pct(r.p2_accept)} reject {pct(r.p2_reject)}")

    section("Fig 2a / sec:best / sec:between: grid, central (best_paper.csv grid rows)")
    g = grid[grid.level == "central"]
    for N in (1000, 100000):
        print(f"N={N}: first {pct(at(g, N, 'p2_best'), 2)} top10 {pct(at(g, N, 'p2_top10'))} oral {pct(at(g, N, 'p2_oral'))} "
              f"spot {pct(at(g, N, 'p2_spot'))} accept {pct(at(g, N, 'p2_accept'))} reject {pct(at(g, N, 'p2_reject'))} "
              f"overlap_top10 {pct(at(g, N, 'overlap_top10'))} overlap_top1pct {pct(at(g, N, 'overlap_top1pct'))} "
              f"z2_winner {at(g, N, 'z2_winner'):.2f} z2_tenth {at(g, N, 'z2_tenth'):.2f}")
    print(f"exponents over 1e3..1e5: p2_best {exponent(g, 'p2_best'):.2f}  p2_top10 {exponent(g, 'p2_top10'):.2f}")
    for lev in LEV:
        gg = grid[grid.level == lev]
        if not gg.empty:
            print(f"  {lev}: overlap_top10 at 1e3 {pct(at(gg, 1000, 'overlap_top10'))}, at 1e5 {pct(at(gg, 100000, 'overlap_top10'))}; "
                  f"first at 1e5 {pct(at(gg, 100000, 'p2_best'), 2)}")

    section("Fig 4c / sec:best / implications: reviews needed (R_needed.csv)")
    r = load("R_needed")
    r = r[r.metric == "overlap"]
    for su in (0.0, 0.5):
        d = r[np.isclose(r.sigma_u, su)].sort_values("N")
        if not d.empty:
            print(f"sigma_u={su}: " + ", ".join(f"N={int(x.N)}: R={x.R_needed:.1f}" for x in d.itertuples()))

    section("Fig 4c / sec:best / implications: reviews per paper to hold each tier's 1K overlap (R_needed_tiers_summary.csv)")
    rt = load("R_needed_tiers_summary")
    for tier in ("accept", "spot", "oral", "top10"):
        d = rt[rt.tier == tier].sort_values("N")
        print(f"{tier:7s} target {d.target.iloc[0]:.3f}: " + ", ".join(f"N={int(x.N)}: {x.R_needed:.1f}" for x in d.itertuples()))

    section("Fig 2b-d / sec:between / sec:accept: placement, central (placement.csv)")
    p = load("placement")
    p = p[p.level == "central"]
    for N in (1000, 100000):
        print(f"N={N}: oral->oral {pct(at(p, N, 'overlap_oral'))} spot->spot {pct(at(p, N, 'overlap_spot'))} accept->accept {pct(at(p, N, 'overlap_accept'))} "
              f"oral->spot+ {pct(at(p, N, 'place_oral_in_spot'))} oral->accept {pct(at(p, N, 'place_oral_in_accept'))} spot->accept {pct(at(p, N, 'place_spot_in_accept'))} "
              f"orals {at(p, N, 'orals'):.0f} spot tier {at(p, N, 'orals') + at(p, N, 'spotlights'):.0f}")
    print(f"at N=9122 (Fig 2 caption, 2021 markers): spot->spot {pct(at(p, 9122, 'overlap_spot'))} spot->accept {pct(at(p, 9122, 'place_spot_in_accept'))} "
          f"oral->accept {pct(at(p, 9122, 'place_oral_in_accept'))}")

    section("Fig 5 / sec:sure: variants at NeurIPS 2014 and 2026 size (best_paper_robustness.csv)")
    rb = load("best_paper_robustness")
    for n in dict.fromkeys(rb.variant):
        parts = []
        for yr in (2014, 2026):
            x = rb[(rb.variant == n) & (rb.year == yr)]
            if x.empty:
                continue
            x = x.iloc[0]
            parts.append(f"{yr}: first {pct(x.p2_best, 2)} oral {pct(x.p2_oral)} merely {pct(x.p2_accept - x.p2_spot)} reject {pct(x.p2_reject, 2)}")
        print(f"{n:28s} " + " | ".join(parts))

    section("Fig 6 / sec:scales: forms at NeurIPS 2014 and 2026 size (scale_impact.csv)")
    sc = load("scale_impact")
    conf = sc[sc.part == "conference"]
    for f in dict.fromkeys(conf.form):
        parts = []
        for yr in (2014, 2026):
            x = conf[(conf.form == f) & (conf.year == yr)]
            if x.empty:
                continue
            x = x.iloc[0]
            parts.append(f"{yr}: first {pct(x.p2_best, 2)} top10 {pct(x.p2_top10)} oral {pct(x.p2_oral)} reject {pct(x.p2_reject)}")
        print(f"{f:28s} " + " | ".join(parts))

    section("Fig 3 / sec:award / sec:sure: NeurIPS 2021 replay, central, subsample (validation_neurips2021.csv)")
    v = load("validation_neurips2021")
    v = v[(v.design == "subsample") & (v.level == "central")]
    for x in v.itertuples():
        print(f"{x.variant:22s} shared {x.overlap_mean:.1f} ({x.overlap_q05:.0f}-{x.overlap_q95:.0f}) P(<=3)={x.p_overlap_le_obs:.3f}  "
              f"rejected {pct(x.top_rej_share_mean, 0)} ({pct(x.top_rej_share_q05, 0)}-{pct(x.top_rej_share_q95, 0)}) P(>=obs)={x.p_top_rej_ge_obs:.3f}")

    section("Chair noise (award_noise.json)")
    a = json.load(open(os.path.join(RES, "award_noise.json")))
    print(f"sigma_award {a['sigma_award']}  bootstrap 90% {a['bootstrap']['q05']:.2f}-{a['bootstrap']['q95']:.2f}  "
          f"observed {a['observed']}  at_fit {a['at_fit']}  at_zero {a['at_zero']}")


if __name__ == "__main__":
    main()
