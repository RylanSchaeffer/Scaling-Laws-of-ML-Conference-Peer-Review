"""Every figure of the paper, from results/*.csv.

Simulation results come from the sweep and robustness CSVs; analytic curves come from
results/analytic_curves.csv, results/analytic_R_needed.csv, results/best_paper.csv and
results/tier_scaling.csv, so every plotted number traces to a CSV row. Figures go to
figures/fig{n}_{name}.pdf and .png, numbered as in the paper.

Usage: uv run python scripts/make_figures.py [names...]
"""

from __future__ import annotations

import argparse
import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.lines import Line2D
from matplotlib.ticker import FixedLocator, NullLocator

from peerreview import plotting as P
from peerreview.levels import LEVELS, ROOT

RES = os.path.join(ROOT, "results")
FIG = os.path.join(ROOT, "figures")
LEV = ("pessimistic", "central", "optimistic")
NEURIPS = {2014: 1678, 2026: 30709}
ROW_H = 1.69  # height of one row of panels, inches


def load(name: str) -> pd.DataFrame:
    return pd.read_csv(os.path.join(RES, f"{name}.csv"), keep_default_na=False, na_values=[""])


_AC = None


def A(quantity: str, level: str, K=None, p=None) -> pd.DataFrame:
    """Rows of results/analytic_curves.csv for one curve, sorted by N."""
    global _AC
    if _AC is None:
        _AC = load("analytic_curves")
    d = _AC[(_AC.quantity == quantity) & (_AC.level == level)]
    if K is not None:
        d = d[np.isclose(d.K.astype(float), K)]
    if p is not None:
        d = d[np.isclose(d.p.astype(float), p)]
    return d.sort_values("N")


def Aband(ax, quantity, color, K=None, label=None, lw=1.6, band=True):
    """Analytic central line, optionally with the pessimistic-optimistic band."""
    c, lo, hi = (A(quantity, lev, K=K) for lev in ("central", "pessimistic", "optimistic"))
    if band:
        ax.fill_between(c.N, lo.value, hi.value, color=color, alpha=0.14, lw=0)
    ax.plot(c.N, c.value, color=color, lw=lw, label=label)


def sim_points(ax, df, col, color, level="central", marker="o", ms=3.6, zorder=4):
    d = df[df.level == level].sort_values("N")
    ax.plot(d.N, d[col], ls="none", marker=marker, ms=ms, color=color, mec=P.SURFACE, mew=0.7, zorder=zorder)


def mark_venues(ax, label=False, y=0.97):
    for yr, n in NEURIPS.items():
        ax.axvline(n, color=P.MUTED, lw=0.6, ls=(0, (2, 2)), zorder=0)
        if label:
            # The second label drops "NeurIPS" so the two labels do not touch in narrow panels.
            text = f"NeurIPS\n{yr}" if yr == min(NEURIPS) else f"\n{yr}"
            ax.text(n * 1.1, y, text, color=P.INK2, va="top", ha="left",
                    transform=ax.get_xaxis_transform())


def sim_legend_handles():
    return [Line2D([], [], color=P.INK2, lw=1.6, label="Theory"),
            Line2D([], [], color=P.INK2, ls="none", marker="o", ms=3.6, mec=P.SURFACE, label="Simulation")]


# ---------------------------------------------------------------------------
# Figure 1: growth, NeurIPS tier shares, and (vs N) where the Best Paper lands again and how much of each tier is reproduced
# ---------------------------------------------------------------------------

VENUES = (("NeurIPS", P.BLUE[450], "o"), ("ICML", P.CAT[1], "s"), ("ICLR", P.CAT[2], "^"))
TIERS = (  # (label, colour): where a second, independent committee ranks the Best Paper, best to worst
    ("Top 10", P.BLUE[700]),  # in the second committee's top 10
    ("Oral", P.BLUE[450]),  # within its oral count, outside its top 10
    ("Accept", P.BLUE[250]),  # accepted by it, below its oral count
    ("Reject", P.ORANGE[450]),  # rejected by it
)


def tier_shares(r) -> list[float]:
    """Split the Best Paper's rank under a second committee into the four TIERS (one best_paper.csv row)."""
    return [r.p2_top10, r.p2_oral - r.p2_top10, r.p2_accept - r.p2_oral, 1 - r.p2_accept]


def venue_rows(level: str = "central") -> pd.DataFrame:
    b = load("best_paper")
    return b[(b.source == "venue") & (b.level == level)]


def venue_counts() -> pd.DataFrame:
    """Submissions, acceptance rate, spotlights and orals per venue-year: data/venues.csv
    (`*_used` columns) and data/spotlights.csv (main-track spotlight counts, blank where the
    venue had no spotlight tier or no source gives one)."""
    v = pd.read_csv(os.path.join(ROOT, "data", "venues.csv"))
    v = v[v.denominator != "decided"]
    sp = pd.read_csv(os.path.join(ROOT, "data", "spotlights.csv"))
    return v.merge(sp[["venue", "year", "spotlights"]], on=["venue", "year"], how="left").sort_values(["venue", "year"])


def _neurips_2026(ax, y, ms):
    """NeurIPS 2026 is reported by secondary aggregators only (docs/claims.md): open marker."""
    ax.plot([2026], [y], ls="none", marker="o", ms=ms, mfc=P.SURFACE, mec=P.BLUE[450], mew=1.0, zorder=5)


def submissions_panel(ax):
    """Papers submitted per year at NeurIPS, ICML and ICLR (data/venues.csv, N_used)."""
    v = venue_counts()
    for venue, c, mk in VENUES:
        s = v[v.venue == venue]
        ax.plot(s.year, s.N_used, color=c, lw=1.6, marker=mk, ms=3.0, mew=0, label=venue)
    _neurips_2026(ax, v[(v.venue == "NeurIPS") & (v.year == 2026)].N_used.iloc[0], 3.4)
    ax.set_yscale("log")
    ax.set_ylim(400, 1e5)
    ax.yaxis.set_major_locator(FixedLocator([1e3, 1e4, 1e5]))
    ax.yaxis.set_minor_locator(NullLocator())
    ax.yaxis.set_major_formatter(plt.FuncFormatter(P.fmt_count))
    ax.set_xticks([2014, 2018, 2022, 2026])
    ax.set_xlim(2013.3, 2026.7)
    ax.set_xlabel("Year")
    ax.set_ylabel("Papers submitted")
    ax.set_title("Submissions", loc="left")
    ax.legend(loc="upper left", handlelength=1.4, borderaxespad=0.2)


RATE_STYLES = (  # (label, column, line style, line width, label position (year, share))
    ("Accepted", "acc_rate_used", "-", 1.6, (2019.5, 0.4)),
    ("Spotlights", "spotlight_rate", (0, (3, 1.6)), 1.4, (2017.6, 0.058)),
    ("Orals", "oral_rate", (0, (1, 1.2)), 1.4, (2017.6, 0.0027)),
)


def rates_panel(ax):
    """Share of NeurIPS submissions accepted, given a spotlight and given an oral, per year
    (main track). Gaps mark years with no spotlight tier (2016, 2022). On the log axis a
    constant share is a flat line, so a falling line means the tier grew more slowly than
    submissions."""
    v = venue_counts().assign(spotlight_rate=lambda d: d.spotlights / d.N_used, oral_rate=lambda d: d.orals_used / d.N_used)
    s = v[v.venue == "NeurIPS"]
    for lab, col, ls, lw, (x, y) in RATE_STYLES:
        ax.plot(s.year[:-1], s[col][:-1], color=P.BLUE[450], ls=ls, lw=lw, marker="o", ms=2.6, mew=0)
        ax.plot(s.year[-2:], s[col][-2:], color=P.BLUE[450], ls=ls, lw=lw)
        _neurips_2026(ax, s[col].iloc[-1], 3.2)
        ax.text(x, y, lab, color=P.INK2, ha="center", va="center")
    ax.set_yscale("log")
    ax.set_ylim(2e-3, 0.6)
    ax.yaxis.set_major_locator(FixedLocator([0.003, 0.01, 0.03, 0.1, 0.3]))
    ax.yaxis.set_minor_locator(NullLocator())
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{100 * x:g}%"))
    ax.set_xticks([2014, 2018, 2022, 2026])
    ax.set_xlim(2013.3, 2026.7)
    ax.set_xlabel("Year")
    ax.set_ylabel("Share of submissions")
    ax.set_title("NeurIPS tiers", loc="left")


TIER_CURVES = (  # Fig 1c,d: tier suffix in results/tier_scaling.csv, colour, labels (c: where the Best Paper lands; d: tier overlap)
    ("accept", P.MUTED, "Accepted", "Accepted"),
    ("spot", P.BLUE[250], "Spotlight or above", "Orals + spotlights"),
    ("oral", P.BLUE[450], "Oral or above", "Orals"),
    ("top10", P.BLUE[550], "Top 10", "Top 10"),
    ("best", P.BLUE[700], "Top-scored", None),
)


def tier_curves(ax, prefix: str, which: int):
    """One line per tier from results/tier_scaling.csv: central level, pessimistic-to-optimistic
    band, label at the right end. prefix 'p2' (the Best Paper's rank under a second review)
    or 'ovl' (two committees' tier overlap); log-log axes over N = 1K..100K."""
    t = load("tier_scaling")
    for tier, color, *labels in TIER_CURVES:
        label = labels[which]
        if label is None:
            continue
        col = f"{prefix}_{tier}"
        lo, cen, hi = (t[t.level == lev].sort_values("N") for lev in LEV)
        ax.fill_between(cen.N, lo[col].values, hi[col].values, color=color, alpha=0.12, lw=0)
        ax.plot(cen.N, cen[col], color=color, lw=1.6)
        if tier == "best":  # below its line, clear of the top-10 band
            ax.text(1e5, cen[col].iloc[-1] / 1.12, label, color=color, ha="right", va="top")
        else:
            ax.text(1e5, cen[col].iloc[-1] * 1.12, label, color=color, ha="right", va="bottom")
    P.n_axis(ax)
    ax.set_yscale("log")
    ax.set_ylim(0.003, 1.3)
    ax.yaxis.set_major_locator(FixedLocator([0.01, 0.1, 1.0]))
    ax.yaxis.set_minor_locator(NullLocator())
    P.pct_axis(ax)
    mark_venues(ax)


def fig_headline():
    """(a) Papers submitted per year. (b) Share of NeurIPS submissions accepted, given spotlights
    and given orals. (c) Where a second, independent committee would rank the model's Best Paper
    as N grows, tier by tier, with tier sizes on NeurIPS's trends. (d) How much of each tier a
    second committee reproduces (results/tier_scaling.csv)."""
    fig, axes = plt.subplots(2, 2, figsize=(P.TEXTWIDTH_IN, 2 * 1.35 + 0.25), gridspec_kw=dict(wspace=0.35, hspace=0.58))
    axes = axes.ravel()
    submissions_panel(axes[0])
    rates_panel(axes[1])
    ax = axes[2]
    tier_curves(ax, "p2", 0)
    ax.set_ylabel("Probability")
    ax.set_title("Where the Best Paper lands again", loc="left")
    ax = axes[3]
    tier_curves(ax, "ovl", 1)
    ax.set_ylabel("Overlap of two committees")
    ax.set_title("How much of each tier is reproduced", loc="left")
    for i, a in enumerate(axes):
        P.panel_label(a, "abcd"[i])
    P.save(fig, os.path.join(FIG, "fig1_headline"))


def standing_panel(ax):
    """Stacked bars: where a second, independent committee would rank the model's Best Paper
    (the top-scored paper) at NeurIPS 2014, 2021 and 2026 size, central level (results/best_paper.csv)."""
    b = venue_rows()
    years = (2026, 2021, 2014)
    for y, yr in enumerate(years):
        r = b[(b.venue == "NeurIPS") & (b.year == yr)].iloc[0]
        left = 0.0
        for (lab, c), w in zip(TIERS, tier_shares(r)):
            ax.barh(y, w, left=left, height=0.62, color=c, edgecolor=P.SURFACE, lw=0.8)
            if w >= 0.14:  # narrower segments stay unlabelled; the caption gives Top 10 and Reject
                ax.text(left + w / 2, y, f"{100 * w:.0f}%", ha="center", va="center", color=P.SURFACE if c != P.BLUE[250] else P.INK)
            left += w
    ax.set_yticks(range(len(years)))
    ax.set_yticklabels([str(yr) for yr in years])
    ax.tick_params(axis="y", length=0)
    ax.set_ylabel("NeurIPS")
    ax.set_xlim(0, 1)
    ax.set_ylim(-0.5, 2.95)
    ax.set_xticks([0, 0.25, 0.5, 0.75, 1])
    P.pct_axis(ax, "x")
    ax.set_xlabel("Share of Best Papers")
    ax.grid(axis="y", visible=False)
    ax.set_title("The Best Paper under a second review", loc="left")
    handles = [plt.Rectangle((0, 0), 1, 1, color=c, label=lab) for lab, c in TIERS]
    ax.legend(handles=handles, loc="upper left", ncol=4, handlelength=0.8, columnspacing=0.8,
              borderaxespad=0.1, handletextpad=0.3)


# ---------------------------------------------------------------------------
# Figure 2: is the model faithful? (held-out tests)
# ---------------------------------------------------------------------------

VAR_LABEL = {"gauss/gauss": "Gaussian / Gaussian", "gauss/gauss+shared": "Gaussian / Gaussian + shared",
             "gauss/t3": "Gaussian / $t_3$", "beta/gauss": "Bounded / Gaussian", "beta/t3": "Bounded / $t_3$",
             "exp/gauss": "Exponential / Gaussian"}


def fig_validation():
    v, ic = load("validation_neurips2021"), load("validation_iclr")
    fig, axes = plt.subplots(1, 3, figsize=(P.TEXTWIDTH_IN, ROW_H + 0.05), gridspec_kw=dict(wspace=0.32))
    sub = v[v.design == "subsample"]
    vv = sub[sub.level == "central"].set_index("variant").loc[list(VAR_LABEL)]
    vp = sub[sub.level == "pessimistic"].set_index("variant").loc[list(VAR_LABEL)]
    y = np.arange(len(vv))[::-1].astype(float)

    def rows(ax, cen, pes, lo, hi, mean, obs, obs_text, c_bar, c_dot, xlim):
        ax.axvline(obs, color=P.INK, lw=1.0)
        ax.text(obs, y.max() + 0.75, obs_text, color=P.INK, va="center", ha="center", bbox=dict(fc=P.SURFACE, ec="none", pad=0.6))
        ax.hlines(y, cen[lo], cen[hi], color=c_bar, lw=2.0)
        ax.plot(cen[mean], y, "o", color=c_dot, ms=4.4, mec=P.SURFACE, mew=0.7, label="Central $\\rho^2$ = 0.50")
        ax.plot(pes[mean], y - 0.28, "o", mfc=P.SURFACE, mec=c_dot, mew=1.0, ms=3.8, ls="none",
                label="Pessimistic $\\rho^2$ = 0.44")
        ax.set_xlim(*xlim)
        ax.set_ylim(-0.7, y.max() + 1.15)
        ax.grid(axis="y", visible=False)

    ax = axes[0]
    rows(ax, vv, vp, "overlap_q05", "overlap_q95", "overlap_mean", 3, "Observed 3", P.BLUE[300], P.BLUE[450], (0, 18))
    ax.set_yticks(y)
    ax.set_yticklabels([VAR_LABEL[k] for k in vv.index])
    ax.set_xlabel("Papers highlighted by both")
    ax.set_title("Highlight overlap", loc="left")

    ax = axes[1]
    obs = vv.obs_spot_rej_share.iloc[0]
    rows(ax, vv, vp, "spot_rej_share_q05", "spot_rej_share_q95", "spot_rej_share_mean", obs,
         f"Observed {100 * obs:.0f}%", P.ORANGE[300], P.ORANGE[450], (0, 0.7))
    ax.set_yticks(y)
    ax.set_yticklabels([])
    P.pct_axis(ax, "x")
    ax.set_xlabel("Spotlights the other rejects")
    ax.set_title("Spotlight rejection", loc="left")
    hl = [Line2D([], [], ls="none", marker="o", ms=4.4, color=P.INK2, mec=P.SURFACE, label="Central $\\rho^2$ = 0.50"),
          Line2D([], [], ls="none", marker="o", ms=3.8, mfc=P.SURFACE, mec=P.INK2, mew=1.0, label="Pessimistic $\\rho^2$ = 0.44"),
          Line2D([], [], color=P.MUTED, lw=2.0, label="90% range (central)")]
    fig.legend(handles=hl, loc="upper center", bbox_to_anchor=(0.36, -0.13), ncol=3, handlelength=1.2)

    ax = axes[2]
    d = ic[(ic.placement == "observed") & (ic.in_main.astype(str) == "True")]
    for (oc, mc, lab, c, mk) in (("obs_precision", "model_precision", "Accepted sets", P.BLUE[450], "o"),
                                 ("obs_top30", "model_top30", "Top-30 sets", P.CAT[1], "s"),
                                 ("obs_top10", "model_top10", "Top-10 sets", P.CAT[2], "^")):
        ax.plot(d[mc], d[oc], ls="none", marker=mk, ms=4.2, color=c, mec=P.SURFACE, mew=0.7, label=lab)
    ax.plot([0, 0.8], [0, 0.8], color=P.MUTED, lw=0.8, ls=(0, (3, 2)))
    ax.set_xlim(0, 0.8)
    ax.set_ylim(0, 0.8)
    ax.set_xticks([0, 0.2, 0.4, 0.6, 0.8])
    ax.set_yticks([0, 0.2, 0.4, 0.6, 0.8])
    P.pct_axis(ax)
    P.pct_axis(ax, "x")
    ax.set_xlabel("Model overlap")
    ax.set_ylabel("Observed overlap")
    ax.legend(loc="upper left", handlelength=1.0, borderaxespad=0.2)
    ax.set_title("ICLR split halves", loc="left")
    for i, a in enumerate(axes):
        P.panel_label(a, "abc"[i])
    P.save(fig, os.path.join(FIG, "fig2_validation"))


# ---------------------------------------------------------------------------
# Figure 3: the Best Paper at every real venue-year
# ---------------------------------------------------------------------------


def fig_venues():
    """(a) The NeurIPS Best Paper's standing under a second review in 2014, 2021 and 2026.
    (b, c) Best Paper tier probabilities that depend on the venue's own oral count and
    acceptance rate, at each venue-year (results/best_paper.csv); NeurIPS band = pessimistic
    to optimistic level. The tiers that depend on N alone are Fig. 1c."""
    b = load("best_paper")
    b = b[b.source == "venue"].copy()
    fig, axes = plt.subplots(1, 3, figsize=(P.TEXTWIDTH_IN, ROW_H), gridspec_kw=dict(wspace=0.45, width_ratios=[1.5, 1, 1]))
    standing_panel(axes[0])
    panels = ((axes[1], "p2_oral", "In oral range again", 1.0),
              (axes[2], "p2_reject", "Rejected", 0.3))
    for ax, col, title, ymax in panels:
        for venue, c, mk in VENUES:
            s = b[b.venue == venue].dropna(subset=[col])
            cen = s[s.level == "central"].sort_values("year")
            if venue == "NeurIPS":  # one band, for the longest series
                lo, hi = (s[s.level == lev].sort_values("year") for lev in ("pessimistic", "optimistic"))
                ax.fill_between(cen.year, lo[col].values, hi[col].values, color=c, alpha=0.13, lw=0)
            ax.plot(cen.year, cen[col], color=c, lw=1.6, marker=mk, ms=3.2, mec=P.SURFACE, mew=0.6, label=venue)
        ax.set_ylim(0, ymax)
        P.pct_axis(ax)
        ax.set_xticks([2014, 2020, 2026])
        ax.set_xlim(2013.3, 2026.7)
        ax.set_xlabel("Year")
        ax.set_title(title, loc="left")
    axes[1].set_ylabel("Probability")
    axes[1].legend(loc="upper right", handlelength=1.1, borderaxespad=0.1)  # above the NeurIPS band
    for i, a in enumerate(axes):
        P.panel_label(a, "abc"[i])
    P.save(fig, os.path.join(FIG, "fig3_venues"))


# ---------------------------------------------------------------------------
# Figure 4: why awards lose reproducibility as conferences grow
# ---------------------------------------------------------------------------


def fig_mechanism():
    """Rerun framing throughout: two independent committees. (a) Overlap of their top-10 sets
    (fixed number) against their top-1% sets (fixed share). (b) The second committee's expected
    score for the first committee's top-scored paper falls ever further below the second
    committee's own 10th-best score. (c) Reviews per paper that hold the top-10 overlap at its
    1K value as N grows (results/analytic_R_needed.csv), without and with shared noise."""
    g = load("sweep_g")
    fig, axes = plt.subplots(1, 3, figsize=(P.TEXTWIDTH_IN, ROW_H), gridspec_kw=dict(wspace=0.62))

    ax = axes[0]
    series = (("K", 10, "ovl_K10", P.BLUE[450], "Top 10"), ("p", 0.01, "ovl_p1pct", P.ORANGE[450], "Top 1%"))
    for kind, size, col, c, label in series:
        q, kw = ("ovl_K", dict(K=size)) if kind == "K" else ("ovl_pct_finite", dict(p=size))
        cen, lo, hi = (A(q, lev, **kw) for lev in ("central", "pessimistic", "optimistic"))
        ax.fill_between(cen.N, lo.value, hi.value, color=c, alpha=0.13, lw=0)
        ax.plot(cen.N, cen.value, color=c, lw=1.6, label=label)
        sim_points(ax, g, col, c)
    P.n_axis(ax)
    ax.set_ylim(0, 0.4)
    P.pct_axis(ax)
    ax.set_ylabel("Overlap of two committees")
    ax.set_title("Number falls, share holds", loc="left")
    ax.legend(loc="upper right", handlelength=1.3, borderaxespad=0.2)
    mark_venues(ax)

    ax = axes[1]
    bar = A("E_kth_best", "central", K=10)
    top = A("E_score2_top_score", "central")
    sd = A("cond_sd2", "central").value.iloc[0]
    ax.plot(bar.N, bar.value, color=P.INK, lw=1.6, label="Its 10th-best score")
    ax.fill_between(top.N, top.value - sd, top.value + sd, color=P.BLUE[450], alpha=0.14, lw=0)
    ax.plot(top.N, top.value, color=P.BLUE[450], lw=1.6, label="Best Paper, $\\pm$1 SD")
    ax.set_ylabel("Second committee's score (SD)")
    ax.set_ylim(0, 5)
    ax.legend(loc="upper left", handlelength=1.3, borderaxespad=0.2)
    ax.set_title("The gap grows", loc="left")
    P.n_axis(ax)
    mark_venues(ax)

    ax = axes[2]
    r = load("analytic_R_needed")
    r = r[(r.metric == "overlap") & (r.N <= 1e5)]
    for su, c, label in ((0.5, P.ORANGE[450], "With shared noise"), (0.0, P.BLUE[450], "Reviewer noise only")):
        d = r[np.isclose(r.sigma_u, su)].sort_values("N")
        ax.plot(d.N, d.R_needed, color=c, lw=1.6, label=label)
    P.n_axis(ax)
    ax.set_ylim(0, 20)  # headroom for the legend above the 14.5 end of the shared-noise curve
    ax.set_yticks([0, 5, 10, 15, 20])
    ax.set_ylabel("Reviews per paper")
    ax.set_title("Holding top-10 overlap costs more", loc="left")
    ax.legend(loc="upper left", handlelength=1.3, borderaxespad=0.2)
    mark_venues(ax)
    for i, a in enumerate(axes):
        P.panel_label(a, "abc"[i])
    P.save(fig, os.path.join(FIG, "fig4_mechanism"))


# ---------------------------------------------------------------------------
# Figure 5: how sure are we? Every variant that fits the acceptance data
# ---------------------------------------------------------------------------


def fig_robustness():
    """Where a second committee ranks the Best Paper at NeurIPS 2014 (open) and 2026 (filled)
    size under every variant refitted to the central disagreement, and each variant's replay of
    the NeurIPS 2021 top-tier overlap (results/best_paper_robustness.csv). The grey span in a-c
    is the Gaussian model's pessimistic-to-optimistic range at 2026 size."""
    r = load("best_paper_robustness")
    r["p2_merely"] = r.p2_accept - r.p2_oral
    names = list(dict.fromkeys(r.variant))
    y = np.arange(len(names))[::-1].astype(float)
    rng26 = [venue_rows(lev).query("venue == 'NeurIPS' and year == 2026").iloc[0] for lev in ("pessimistic", "optimistic")]
    fig, axes = plt.subplots(1, 4, figsize=(P.TEXTWIDTH_IN, ROW_H + 0.6),
                             gridspec_kw=dict(wspace=0.34, width_ratios=[1, 1, 1, 0.85]))
    panels = ((axes[0], "p2_best", "Top-scored again", (0, 1), False),
              (axes[1], "p2_merely", "Merely accepted", (0, 1), False),
              (axes[2], "p2_reject", "Rejected", (1e-4, 0.5), True))
    for ax, col, title, xlim, logx in panels:
        span = sorted((x.p2_accept - x.p2_oral) if col == "p2_merely" else x[col] for x in rng26)
        ax.axvspan(max(span[0], xlim[0]), span[1], color=P.GRID, alpha=0.9, lw=0, zorder=0)
        c = P.ORANGE[450] if col == "p2_reject" else P.BLUE[450]
        for yi, n in zip(y, names):
            for yr, hollow in ((2014, True), (2026, False)):
                v = float(r[(r.variant == n) & (r.year == yr)][col].iloc[0])
                floor = logx and v < xlim[0]
                v = xlim[0] * 1.08 if floor else v
                ax.plot(v, yi, "<" if floor else "o", ms=3.8, color=c, mfc=P.SURFACE if hollow else c,
                        mec=c if hollow else P.SURFACE, mew=0.9, ls="none", zorder=3)
        if logx:
            ax.set_xscale("log")
            ax.set_xticks([1e-4, 1e-3, 1e-2, 1e-1])
            ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda v, _p: f"{100 * v:g}%"))
        else:
            ax.set_xticks([0, 0.5, 1] if xlim[1] == 1 else [0, 0.4, 0.8])
            P.pct_axis(ax, "x")
        ax.set_xlim(*xlim)
        ax.set_title(title, loc="left")
        ax.set_xlabel("Probability")

    ax = axes[3]
    o = r[r.year == 2026].set_index("variant").loc[names]
    ax.axvline(3, color=P.INK, lw=1.0)
    ax.hlines(y, o.overlap2021_q05, o.overlap2021_q95, color=P.BLUE[300], lw=2.0)
    ax.plot(o.overlap2021_mean, y, "o", color=P.BLUE[450], ms=3.8, mec=P.SURFACE, mew=0.7, ls="none", zorder=3)
    ax.set_xlim(0, 30)
    ax.set_title("2021 overlap", loc="left")
    ax.set_xlabel("Papers in both tiers")

    for ax in axes:
        ax.set_ylim(-0.6, len(names) - 0.2)
        ax.set_yticks(y)
        ax.set_yticklabels([n[0].upper() + n[1:] for n in names] if ax is axes[0] else [])
        ax.grid(axis="y", visible=False)
    hl = [Line2D([], [], ls="none", marker="o", ms=3.8, color=P.INK2, mfc=P.SURFACE, mew=0.9, label="NeurIPS 2014 size"),
          Line2D([], [], ls="none", marker="o", ms=3.8, color=P.INK2, mec=P.SURFACE, label="NeurIPS 2026 size"),
          plt.Rectangle((0, 0), 1, 1, color=P.GRID, label="Gaussian, reliability range (2026)"),
          Line2D([], [], color=P.BLUE[300], lw=2.0, label="90% range of the 2021 replay"),
          Line2D([], [], color=P.INK, lw=1.0, label="Observed at NeurIPS 2021 (3)")]
    fig.legend(handles=hl, loc="upper center", bbox_to_anchor=(0.5, -0.02), ncol=3, handlelength=1.2)
    for i, a in enumerate(axes):
        P.panel_label(a, "abcd"[i])
    P.save(fig, os.path.join(FIG, "fig5_robustness"))


FIGURES = dict(headline=fig_headline, validation=fig_validation, venues=fig_venues, mechanism=fig_mechanism,
               robustness=fig_robustness)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("names", nargs="*", default=list(FIGURES))
    args = ap.parse_args()
    os.makedirs(FIG, exist_ok=True)
    P.setup()
    for n in args.names:
        FIGURES[n]()
        print("wrote", n)


if __name__ == "__main__":
    main()
