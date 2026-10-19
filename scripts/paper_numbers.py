"""Print every simulated number the paper quotes, from results/*.csv, in the order of the paper.

Tiers are separate (peerreview.tiers): Best Papers, Oral, Spotlight, Accepted (no award), Rejected.
A union is always printed as "X or Better".

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
    section("sec:tiers / Table bestpapers: NeurIPS Best Papers by year (data/neurips_best_papers.csv) and their power-law fit")
    bp = pd.read_csv(os.path.join(ROOT, "data", "neurips_best_papers.csv"))
    for c in ("main_track", "all_tracks"):
        print(f"{c}: {bp[c].min()} to {bp[c].max()} a year, {bp.year.min()}-{bp.year.max()}; median {np.median(bp[c]):g}, mean {bp[c].mean():.2f}; "
              f"years with one: {list(bp.year[bp[c] == 1])}")
    v = pd.read_csv(os.path.join(ROOT, "data", "venues.csv"))
    v = v[(v.venue == "NeurIPS") & (v.denominator != "decided") & v.awards_used.notna()]
    (k, _), cov = np.polyfit(np.log10(v.N_used.astype(float)), np.log10(v.awards_used.astype(float)), 1, cov=True)
    print(f"main-track count ~ N^{k:.2f} +- {np.sqrt(cov[0, 0]):.2f} (SE), {int(v.year.min())}-{int(v.year.max())}, {len(v)} years")

    section("sec:tiers / Fig 1b: NeurIPS count fits, count = a N^gamma (tier_sizes.csv); oral is the Oral tier alone, oral_or_better NeurIPS's Oral count")
    for r in load("tier_sizes").itertuples():
        print(f"{r.series:17s} {r.a:.2f} N^{r.gamma:.2f} ({r.year_min}-{r.year_max}, {r.n_years} years)")

    sz = os.path.join(RES, "best_paper_size.csv")
    if os.path.exists(sz):
        section("sec:robust (two or four Best Papers): Best Papers again for 2, 3 and 4 Best Papers, central (best_paper_size.csv)")
        d = pd.read_csv(sz)
        for (sc, k), g in d.groupby(["scale", "n_best"] if "scale" in d else ["n_best", "n_best"]):
            g = g.sort_values("N")
            e = -np.polyfit(np.log(g.N.values), np.log(g.p2_best.values), 1)[0]
            print(f"{sc} {k} Best Papers: {pct(g.p2_best.iloc[0], 2)} at {int(g.N.iloc[0])}, {pct(g.p2_best.iloc[-1], 3)} at {int(g.N.iloc[-1])}; exponent {e:.2f}")

    b = load("best_paper")
    ven = b[b.source == "venue"]
    grid = b[b.source == "grid"]

    section("Fig 1c / sec:bestpaper: NeurIPS Best Papers (the top three) under a second review (best_paper.csv venue rows)")
    for yr in (2014, 2021, 2026):
        for lev in LEV:
            r = ven[(ven.venue == "NeurIPS") & (ven.year == yr) & (ven.level == lev)]
            if r.empty:
                continue
            r = r.iloc[0]
            print(f"NeurIPS {yr} {lev:11s} N={int(r.N):6d} Oral or Better count={int(r.n_oral_or_better)} Spotlights={r.spotlights}: Best Papers {pct(r.p2_best, 2)} "
                  f"Oral {pct(r.p2_oral)} Spotlight {pct(r.p2_spot)} Accepted {pct(r.p2_accept)} Rejected {pct(r.p2_reject)} | "
                  f"Oral or Better {pct(r.p2_oral_or_better)} Spotlight or Better {pct(r.p2_spot_or_better)} Accepted or Better {pct(r.p2_accept_or_better)} "
                  f"| median rank {r.best_papers_rank2_median:.0f} reps={int(r.reps)} reps_best={r.reps_best}")
    for v in ("ICML", "ICLR"):
        r = ven[(ven.venue == v) & (ven.year == 2026) & (ven.level == "central")]
        if not r.empty:
            r = r.iloc[0]
            print(f"{v} 2026 central N={int(r.N)} Oral or Better count={int(r.n_oral_or_better)} Spotlights={r.spotlights}: Best Papers {pct(r.p2_best, 2)} "
                  f"Oral {pct(r.p2_oral)} Spotlight {pct(r.p2_spot)} Accepted {pct(r.p2_accept)} Rejected {pct(r.p2_reject)} | "
                  f"Oral or Better {pct(r.p2_oral_or_better)} Spotlight or Better {pct(r.p2_spot_or_better)} Accepted or Better {pct(r.p2_accept_or_better)}")

    section("Fig 2a / sec:best / sec:between: grid, central (best_paper.csv grid rows)")
    g = grid[grid.level == "central"]
    for N in (1000, 100000):
        print(f"N={N}: Best Papers {pct(at(g, N, 'p2_best'), 2)} Oral {pct(at(g, N, 'p2_oral'))} "
              f"Spotlight {pct(at(g, N, 'p2_spot'))} Accepted {pct(at(g, N, 'p2_accept'))} Rejected {pct(at(g, N, 'p2_reject'))} "
              f"overlap Accepted or Better {pct(at(g, N, 'overlap_accept_or_better'))} "
              f"overlap_top0p3pct {pct(at(g, N, 'overlap_top0p3pct'))} median rank {at(g, N, 'best_papers_rank2_median'):.0f} "
              f"z2_best_papers {at(g, N, 'z2_best_papers'):.2f} z2_cut {at(g, N, 'z2_cut'):.2f}")
    print(f"exponent over 1e3..1e5: p2_best {exponent(g, 'p2_best'):.2f}")
    for lev in LEV:
        gg = grid[grid.level == lev]
        if not gg.empty:
            print(f"  {lev}: Best Papers again at 1e3 {pct(at(gg, 1000, 'p2_best'), 2)}, at 1e5 {pct(at(gg, 100000, 'p2_best'), 2)}; "
                  f"exponent {exponent(gg, 'p2_best'):.2f}")

    section("Fig 4a / sec:best: the ceiling, overlap with infinitely many reviewers (R_needed_tiers_curve.csv limit_overlap)")
    rc = load("R_needed_tiers_curve")
    for tier in ("accept", "spot", "oral", "best"):
        c = rc[rc.group == tier].sort_values("N")
        lim_at = lambda N: float(np.interp(np.log(N), np.log(c.N.values), c.limit_overlap.values))
        print(f"{tier:7s} " + ", ".join(f"N={N}: {pct(lim_at(N))}" for N in (1000, 10000, 100000)))
    cc = os.path.join(RES, "chair_calls.csv")
    if os.path.exists(cc):
        section("Two levers at the top (chair_calls.csv): Best Papers overlap by reviews per paper R and independent chair calls k")
        d = pd.read_csv(cc)
        print(d.pivot_table(index=["N", "R"], columns="k", values="overlap_best").round(4).to_string())
        print(d.pivot_table(index=["N", "R"], columns="k", values="overlap_best_se").round(4).to_string())

    section("Fig 4b / sec:best / implications: reviews per paper to hold each tier's 1K overlap (R_needed_tiers_curve.csv, the drawn curve)")
    rt = load("R_needed_tiers_summary")
    rc = load("R_needed_tiers_curve")
    for tier in ("accept", "spot", "oral", "best"):
        d = rt[rt.group == tier].sort_values("N")
        c = rc[rc.group == tier].sort_values("N")
        r_at = lambda N: float(np.interp(np.log(N), np.log(c.N.values), c.R_needed.values))
        lim_at = lambda N: float(np.interp(np.log(N), np.log(c.N.values), c.limit_overlap.values))
        ns = float(c.N_star.iloc[0])
        print(f"{tier:7s} target {d.target.iloc[0]:.4f}: " + ", ".join(f"N={N}: {r_at(N):.1f}" for N in (1000, 10000, 21544, 31623, 46416, 100000))
              + (f"; N* = {ns:,.0f}" if np.isfinite(ns) else "; no N* up to 100,000"))
        print(f"        R = inf overlap: " + ", ".join(f"N={N}: {lim_at(N):.4f}" for N in (1000, 10000, 46416, 100000)))

    section("Fig 1e-g / sec:between / sec:accept: placement, central (placement.csv): first-review group -> second-review tier")
    p = load("placement")
    p = p[p.level == "central"]
    seps = ("best", "oral", "spot", "accept", "reject")
    for N in (1000, 9122, 30709, 100000):
        print(f"N={N}: Oral tier {at(p, N, 'n_oral_or_better') - 3:.0f} papers, Spotlight tier {at(p, N, 'spotlights'):.0f}, "
              f"Accepted tier {0.25 * N - at(p, N, 'n_oral_or_better') - at(p, N, 'spotlights'):.0f}")
        for first in ("best", "oral", "spot", "accept", "accept_or_better"):
            print(f"   {first:16s} -> " + " ".join(f"{y} {pct(at(p, N, f'place_{first}_in_{y}'))}" for y in seps)
                  + (f" | accepted again (Accepted or Better) {pct(1 - at(p, N, f'place_{first}_in_reject'))}"))
        print(f"   overlap Oral or Better {pct(at(p, N, 'overlap_oral_or_better'))} Spotlight or Better {pct(at(p, N, 'overlap_spot_or_better'))} "
              f"Accepted or Better {pct(at(p, N, 'overlap_accept_or_better'))}")

    section("Fig 5 / sec:sure: variants at NeurIPS 2014 and 2026 size (best_paper_robustness.csv)")
    rb = load("best_paper_robustness")
    for n in dict.fromkeys(rb.variant):
        parts = []
        for yr in (2014, 2026):
            x = rb[(rb.variant == n) & (rb.year == yr)]
            if x.empty:
                continue
            x = x.iloc[0]
            parts.append(f"{yr}: Best Papers {pct(x.p2_best, 2)} Oral {pct(x.p2_oral)} Spotlight {pct(x.p2_spot)} Accepted {pct(x.p2_accept)} Rejected {pct(x.p2_reject, 2)}")
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
            parts.append(f"{yr}: Best Papers {pct(x.p2_best, 2)} Oral {pct(x.p2_oral)} Spotlight {pct(x.p2_spot)} Accepted {pct(x.p2_accept)} Rejected {pct(x.p2_reject)}")
        print(f"{f:28s} " + " | ".join(parts))
    gr = sc[sc.part == "grid"]
    for f in dict.fromkeys(gr.form):
        g = gr[gr.form == f].sort_values("N")
        e = -np.polyfit(np.log(g.N.values), np.log(g.p2_best.values), 1)[0]
        print(f"grid {f:28s} Best Papers again {pct(g.p2_best.iloc[0], 2)} at {int(g.N.iloc[0])}, {pct(g.p2_best.iloc[-1], 3)} at {int(g.N.iloc[-1])}; exponent {e:.2f}")

    section("Fig 3 / sec:award / sec:sure: NeurIPS 2021 replay, central, subsample (validation_neurips2021.csv)")
    v = load("validation_neurips2021")
    v = v[(v.design == "subsample") & (v.level == "central")]
    for x in v.itertuples():
        print(f"{x.variant:22s} Spotlight or Better shared {x.sob_overlap_mean:.1f} ({x.sob_overlap_q05:.0f}-{x.sob_overlap_q95:.0f}) P(<=3)={x.p_sob_overlap_le_obs:.3f}  "
              f"rejected {pct(x.sob_rej_share_mean, 0)} ({pct(x.sob_rej_share_q05, 0)}-{pct(x.sob_rej_share_q95, 0)}) P(>=obs)={x.p_sob_rej_ge_obs:.3f}")

    section("Chair noise (award_noise.json)")
    a = json.load(open(os.path.join(RES, "award_noise.json")))
    print(f"sigma_award {a['sigma_award']}  bootstrap 90% {a['bootstrap']['q05']:.2f}-{a['bootstrap']['q95']:.2f}  "
          f"observed {a['observed']}  at_fit {a['at_fit']}  at_zero {a['at_zero']}")


if __name__ == "__main__":
    main()
