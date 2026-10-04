"""Every figure of the paper, from results/*.csv.

Simulation results come from the sweep and robustness CSVs; analytic curves come from
results/analytic_curves.csv and results/best_paper.csv, so every plotted number traces to a
CSV row. Figures go to figures/fig{n}_{name}.pdf and .png, numbered as in the paper.

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
            ax.text(n * 1.1, y, text, fontsize=6.3, color=P.INK2, va="top", ha="left",
                    transform=ax.get_xaxis_transform())


def sim_legend_handles():
    return [Line2D([], [], color=P.INK2, lw=1.6, label="theory"),
            Line2D([], [], color=P.INK2, ls="none", marker="o", ms=3.6, mec=P.SURFACE, label="simulation")]


# ---------------------------------------------------------------------------
# Figure 1: growth, and where the Best Paper truly ranks
# ---------------------------------------------------------------------------

VENUES = (("NeurIPS", P.BLUE[450], "o"), ("ICML", P.CAT[1], "s"), ("ICLR", P.CAT[2], "^"))
TIERS = (  # (label, colour): the Best Paper's true standing, best to worst
    ("truly best", P.BLUE[700]),
    ("2nd to 10th", P.BLUE[550]),
    ("rest of oral-worthy", P.BLUE[400]),
    ("merely accept-worthy", P.BLUE[250]),
    ("should have been rejected", P.ORANGE[450]),
)


def tier_shares(r) -> list[float]:
    """Split the Best Paper's true standing into the five TIERS (one best_paper.csv row)."""
    return [r.p_best, r.p_top10 - r.p_best, r.p_oral - r.p_top10, r.p_accept - r.p_oral, 1 - r.p_accept]


def venue_rows(level: str = "central") -> pd.DataFrame:
    b = load("best_paper")
    return b[(b.source == "venue") & (b.level == level)]


def submissions_panel(ax):
    """Submitted (solid), accepted (dashed) and oral (dotted) papers per year at NeurIPS, ICML
    and ICLR (data/venues.csv: N_used, N_used x acc_rate_used, orals_used). On the log axis a
    constant rate is a constant gap between two lines; a widening gap is a falling rate."""
    v = pd.read_csv(os.path.join(ROOT, "data", "venues.csv"))
    v = v[v.denominator != "decided"].copy()
    v["accepted_n"] = (v.N_used * v.acc_rate_used).round()
    for venue, c, mk in (("NeurIPS", P.BLUE[450], "o"), ("ICML", P.CAT[1], "s"), ("ICLR", P.CAT[2], "^")):
        s = v[v.venue == venue].sort_values("year")
        ax.plot(s.year, s.N_used, color=c, lw=1.6, marker=mk, ms=3.2, mec=P.SURFACE, mew=0.6)
        ax.plot(s.year, s.accepted_n, color=c, lw=1.2, ls=(0, (3, 1.6)), marker=mk, ms=2.6, mec=P.SURFACE, mew=0.5)
        o = s.dropna(subset=["orals_used"])
        ax.plot(o.year, o.orals_used, color=c, lw=1.0, ls=(0, (1, 1.3)), marker=mk, ms=2.2, mec=P.SURFACE, mew=0.4)
    # NeurIPS 2026 is reported by secondary aggregators only (docs/claims.md): open markers.
    last = v[(v.venue == "NeurIPS") & (v.year == 2026)]
    for col, ms in (("N_used", 3.2), ("accepted_n", 2.6), ("orals_used", 2.2)):
        ax.plot(last.year, last[col], ls="none", marker="o", ms=ms, mfc=P.SURFACE, mec=P.BLUE[450], mew=1.0, zorder=5)
    ax.set_yscale("log")
    ax.set_ylim(9, 1e6)  # headroom so the legend clears the 2023-2026 NeurIPS points
    ax.yaxis.set_major_locator(FixedLocator([10, 100, 1e3, 1e4, 1e5]))
    ax.yaxis.set_minor_locator(NullLocator())
    ax.yaxis.set_major_formatter(plt.FuncFormatter(P.fmt_count))
    ax.set_xticks([2014, 2018, 2022, 2026])
    ax.set_xlim(2013.3, 2026.7)
    ax.set_xlabel("Year")
    ax.set_ylabel("Papers per year")
    ax.set_title("Submitted, accepted, orals", loc="left")
    handles = [Line2D([], [], color=c, lw=1.6, marker=mk, ms=3.2, mec=P.SURFACE, label=venue)
               for venue, c, mk in (("NeurIPS", P.BLUE[450], "o"), ("ICML", P.CAT[1], "s"), ("ICLR", P.CAT[2], "^"))]
    handles += [Line2D([], [], color=P.INK2, lw=1.6, label="submitted"),
                Line2D([], [], color=P.INK2, lw=1.2, ls=(0, (3, 1.6)), label="accepted"),
                Line2D([], [], color=P.INK2, lw=1.0, ls=(0, (1, 1.3)), label="orals")]
    ax.legend(handles=handles, loc="upper left", ncol=2, handlelength=1.6, columnspacing=0.8, borderaxespad=0.2,
              fontsize=6.5)


def fig_headline():
    """(a) Papers submitted, accepted and given orals per year. (b) The true standing of the
    model's Best Paper (the top-scored paper) at NeurIPS 2014, 2021 and 2026 size, central level
    (results/best_paper.csv)."""
    fig, axes = plt.subplots(1, 2, figsize=(P.TEXTWIDTH_IN, 1.85), gridspec_kw=dict(wspace=0.42, width_ratios=[1, 1.5]))
    submissions_panel(axes[0])

    ax = axes[1]
    b = venue_rows()
    years = (2026, 2021, 2014)
    for y, yr in enumerate(years):
        r = b[(b.venue == "NeurIPS") & (b.year == yr)].iloc[0]
        left = 0.0
        for (lab, c), w in zip(TIERS, tier_shares(r)):
            ax.barh(y, w, left=left, height=0.62, color=c, edgecolor=P.SURFACE, lw=0.8)
            if w >= 0.055:
                ax.text(left + w / 2, y, f"{100 * w:.0f}%", ha="center", va="center", fontsize=6.5 if w >= 0.09 else 5.6,
                        color=P.SURFACE if c != P.BLUE[250] else P.INK)
            left += w
        ax.text(1.015, y, f"{100 * (1 - r.p_accept):.1f}%", ha="left", va="center", fontsize=6.5, color=P.ORANGE[600],
                clip_on=False)
    ax.set_yticks(range(len(years)))
    ax.set_yticklabels([f"{yr}\n{int(b[(b.venue == 'NeurIPS') & (b.year == yr)].N.iloc[0]):,}" for yr in years],
                       fontsize=6.5)
    ax.set_ylabel("NeurIPS size")
    ax.set_xlim(0, 1)
    ax.set_ylim(-0.5, 3.35)
    ax.set_xticks([0, 0.25, 0.5, 0.75, 1])
    P.pct_axis(ax, "x")
    ax.set_xlabel("Share of Best Papers")
    ax.grid(axis="y", visible=False)
    ax.set_title("Where the Best Paper truly ranks", loc="left")
    handles = [plt.Rectangle((0, 0), 1, 1, color=c, label=lab) for lab, c in TIERS]
    ax.legend(handles=handles, loc="upper left", ncol=3, fontsize=6.2, handlelength=0.9, columnspacing=0.6,
              borderaxespad=0.1, handletextpad=0.3)
    for i, a in enumerate(axes):
        P.panel_label(a, "ab"[i])
    P.save(fig, os.path.join(FIG, "fig1_headline"))


# ---------------------------------------------------------------------------
# Figure 2: is the model faithful? (held-out tests)
# ---------------------------------------------------------------------------

VAR_LABEL = {"gauss/gauss": "Gaussian / Gaussian", "gauss/gauss+shared": "Gaussian / Gaussian + shared",
             "gauss/t3": "Gaussian / $t_3$", "beta/gauss": "bounded / Gaussian", "beta/t3": "bounded / $t_3$",
             "exp/gauss": "exponential / Gaussian"}


def fig_validation():
    v, ic = load("validation_neurips2021"), load("validation_iclr")
    fig, axes = plt.subplots(1, 3, figsize=(P.TEXTWIDTH_IN, ROW_H + 0.2), gridspec_kw=dict(wspace=0.32))
    sub = v[v.design == "subsample"]
    vv = sub[sub.level == "central"].set_index("variant").loc[list(VAR_LABEL)]
    vp = sub[sub.level == "pessimistic"].set_index("variant").loc[list(VAR_LABEL)]
    y = np.arange(len(vv))[::-1].astype(float)

    def rows(ax, cen, pes, lo, hi, mean, obs, obs_text, c_bar, c_dot, xlim):
        ax.axvline(obs, color=P.INK, lw=1.0)
        ax.text(obs, y.max() + 0.75, obs_text, fontsize=6.5, color=P.INK, va="center", ha="center", bbox=dict(fc=P.SURFACE, ec="none", pad=0.6))
        ax.hlines(y, cen[lo], cen[hi], color=c_bar, lw=2.0)
        ax.plot(cen[mean], y, "o", color=c_dot, ms=4.4, mec=P.SURFACE, mew=0.7, label="central $\\rho^2$ = 0.50")
        ax.plot(pes[mean], y - 0.28, "o", mfc=P.SURFACE, mec=c_dot, mew=1.0, ms=3.8, ls="none",
                label="pessimistic $\\rho^2$ = 0.44")
        ax.set_xlim(*xlim)
        ax.set_ylim(-0.7, y.max() + 1.15)
        ax.grid(axis="y", visible=False)

    ax = axes[0]
    rows(ax, vv, vp, "overlap_q05", "overlap_q95", "overlap_mean", 3, "observed 3", P.BLUE[300], P.BLUE[450], (0, 18))
    ax.set_yticks(y)
    ax.set_yticklabels([VAR_LABEL[k] for k in vv.index], fontsize=6.3)
    ax.set_xlabel("Papers highlighted by both")
    ax.set_title("Highlight overlap", loc="left")

    ax = axes[1]
    obs = vv.obs_spot_rej_share.iloc[0]
    rows(ax, vv, vp, "spot_rej_share_q05", "spot_rej_share_q95", "spot_rej_share_mean", obs,
         f"observed {100 * obs:.0f}%", P.ORANGE[300], P.ORANGE[450], (0, 0.7))
    ax.set_yticks(y)
    ax.set_yticklabels([])
    P.pct_axis(ax, "x")
    ax.set_xlabel("Spotlights the other rejects")
    ax.set_title("Spotlight rejection", loc="left")
    hl = [Line2D([], [], ls="none", marker="o", ms=4.4, color=P.INK2, mec=P.SURFACE, label="central $\\rho^2$ = 0.50"),
          Line2D([], [], ls="none", marker="o", ms=3.8, mfc=P.SURFACE, mec=P.INK2, mew=1.0, label="pessimistic $\\rho^2$ = 0.44"),
          Line2D([], [], color=P.MUTED, lw=2.0, label="90% range (central)")]
    fig.legend(handles=hl, loc="upper center", bbox_to_anchor=(0.36, -0.04), ncol=3, handlelength=1.2, fontsize=7)

    ax = axes[2]
    d = ic[(ic.placement == "observed") & (ic.in_main.astype(str) == "True")]
    for (oc, mc, lab, c, mk) in (("obs_precision", "model_precision", "accepted sets", P.BLUE[450], "o"),
                                 ("obs_top30", "model_top30", "top-30 sets", P.CAT[1], "s"),
                                 ("obs_top10", "model_top10", "top-10 sets", P.CAT[2], "^")):
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
    """Best Paper tier probabilities at each venue-year's submissions, acceptance rate and oral
    count (results/best_paper.csv); NeurIPS band = pessimistic to optimistic level."""
    b = load("best_paper")
    b = b[b.source == "venue"].copy()
    b["p_merely"] = b.p_accept - b.p_oral
    fig, axes = plt.subplots(1, 4, figsize=(P.TEXTWIDTH_IN, ROW_H), gridspec_kw=dict(wspace=0.5))
    panels = ((axes[0], "p_best", "Truly best", 0.4),
              (axes[1], "p_top10", "In true top 10", 0.82),
              (axes[2], "p_oral", "Oral-worthy", 1.0),
              (axes[3], "p_reject", "Should be rejected", 0.03))
    for ax, col, title, ymax in panels:
        for venue, c, mk in VENUES:
            s = b[b.venue == venue].dropna(subset=[col])
            cen = s[s.level == "central"].sort_values("year")
            if venue == "NeurIPS":  # one band, for the longest series
                lo, hi = (s[s.level == lev].sort_values("year") for lev in ("pessimistic", "optimistic"))
                ax.fill_between(cen.year, lo[col].values, hi[col].values, color=c, alpha=0.13, lw=0)
            ax.plot(cen.year, cen[col], color=c, lw=1.6, marker=mk, ms=3.2, mec=P.SURFACE, mew=0.6, label=venue)
        ax.set_ylim(0, ymax)
        if col == "p_reject":
            ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _p: f"{100 * v:.1f}%"))
        else:
            P.pct_axis(ax)
        ax.set_xticks([2014, 2020, 2026])
        ax.set_xlim(2013.3, 2026.7)
        ax.set_xlabel("Year")
        ax.set_title(title, loc="left", fontsize=7.5)
    axes[0].set_ylabel("Probability")
    axes[1].legend(loc="upper right", handlelength=1.1, borderaxespad=0.1, fontsize=6.3)
    for i, a in enumerate(axes):
        P.panel_label(a, "abcd"[i])
    P.save(fig, os.path.join(FIG, "fig3_venues"))


# ---------------------------------------------------------------------------
# Figure 4: why awards lose accuracy as conferences grow
# ---------------------------------------------------------------------------


def fig_mechanism():
    """(a) Fixed number against fixed percentage. (b) The top-scored paper falls ever further
    below the true top-10 bar. (c) The Best Paper's chances out to a million submissions."""
    g = load("sweep_g")
    fig, axes = plt.subplots(1, 3, figsize=(P.TEXTWIDTH_IN, ROW_H), gridspec_kw=dict(wspace=0.62))

    ax = axes[0]
    series = (("K", 10, "prec_K10", P.BLUE[450], "top 10"), ("p", 0.01, "prec_p1pct", P.ORANGE[450], "top 1%"))
    for kind, size, col, c, label in series:
        q, kw = ("prec_K", dict(K=size)) if kind == "K" else ("prec_pct_finite", dict(p=size))
        cen, lo, hi = (A(q, lev, **kw) for lev in ("central", "pessimistic", "optimistic"))
        ax.fill_between(cen.N, lo.value, hi.value, color=c, alpha=0.13, lw=0)
        ax.plot(cen.N, cen.value, color=c, lw=1.6, label=label)
        sim_points(ax, g, col, c)
    P.n_axis(ax)
    ax.set_ylim(0, 0.6)
    P.pct_axis(ax)
    ax.set_ylabel("Precision")
    ax.set_title("Number falls, share holds", loc="left")
    ax.legend(loc="lower left", handlelength=1.3, borderaxespad=0.2)
    mark_venues(ax)

    ax = axes[1]
    bar = A("E_kth_best", "central", K=10)
    top = A("E_quality_top_score", "central")
    sd = A("cond_sd", "central").value.iloc[0]
    ax.plot(bar.N, bar.value, color=P.INK, lw=1.6, label="true top-10 bar")
    ax.fill_between(top.N, top.value - sd, top.value + sd, color=P.BLUE[450], alpha=0.14, lw=0)
    ax.plot(top.N, top.value, color=P.BLUE[450], lw=1.6, label="top-scored, $\\pm$1 SD")
    ax.set_ylabel("Standardised quality")
    ax.set_ylim(0, 6)
    ax.legend(loc="upper left", handlelength=1.3, borderaxespad=0.2)
    ax.set_title("The gap grows", loc="left")
    P.n_axis(ax)
    mark_venues(ax)

    ax = axes[2]
    b = load("best_paper")
    grid = b[b.source == "grid"]
    for col, c, label in (("p_top10", P.BLUE[400], "in true top 10"), ("p_best", P.BLUE[700], "truly best")):
        cen, lo, hi = (grid[grid.level == lev].sort_values("N") for lev in ("central", "pessimistic", "optimistic"))
        ax.fill_between(cen.N, lo[col].values, hi[col].values, color=c, alpha=0.14, lw=0)
        ax.plot(cen.N, cen[col], color=c, lw=1.6, label=label)
    P.n_axis(ax)
    ax.set_ylim(0, 0.8)
    P.pct_axis(ax)
    ax.set_ylabel("P(Best Paper is ...)")
    ax.set_title("The Best Paper", loc="left")
    ax.legend(loc="upper right", handlelength=1.3, borderaxespad=0.2)
    mark_venues(ax)
    for i, a in enumerate(axes):
        P.panel_label(a, "abc"[i])
    P.save(fig, os.path.join(FIG, "fig4_mechanism"))


# ---------------------------------------------------------------------------
# Figure 5: how sure are we? Every variant that fits the acceptance data
# ---------------------------------------------------------------------------


def fig_robustness():
    """Best Paper tier probabilities at NeurIPS 2014 (open) and 2026 (filled) size under every
    variant refitted to the central disagreement, and each variant's replay of the NeurIPS 2021
    top-tier overlap (results/best_paper_robustness.csv). The grey span in a-c is the Gaussian
    model's pessimistic-to-optimistic range at 2026 size."""
    r = load("best_paper_robustness")
    r["p_merely"] = r.p_accept - r.p_oral
    names = list(dict.fromkeys(r.variant))
    y = np.arange(len(names))[::-1].astype(float)
    rng26 = [venue_rows(lev).query("venue == 'NeurIPS' and year == 2026").iloc[0] for lev in ("pessimistic", "optimistic")]
    fig, axes = plt.subplots(1, 4, figsize=(P.TEXTWIDTH_IN, ROW_H + 0.75),
                             gridspec_kw=dict(wspace=0.34, width_ratios=[1, 1, 1, 0.85]))
    panels = ((axes[0], "p_best", "Truly best", (0, 1), False),
              (axes[1], "p_merely", "Merely accept-worthy", (0, 0.8), False),
              (axes[2], "p_reject", "Should be rejected", (1e-4, 0.2), True))
    for ax, col, title, xlim, logx in panels:
        span = sorted((x.p_accept - x.p_oral) if col == "p_merely" else x[col] for x in rng26)
        ax.axvspan(max(span[0], xlim[0]), span[1], color=P.GRID, alpha=0.9, lw=0, zorder=0)
        c = P.ORANGE[450] if col == "p_reject" else P.BLUE[450]
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
        ax.set_title(title, loc="left", fontsize=7.5)
        ax.set_xlabel("Probability")

    ax = axes[3]
    o = r[r.year == 2026].set_index("variant").loc[names]
    ax.axvline(3, color=P.INK, lw=1.0)
    ax.hlines(y, o.overlap2021_q05, o.overlap2021_q95, color=P.BLUE[300], lw=2.0)
    ax.plot(o.overlap2021_mean, y, "o", color=P.BLUE[450], ms=3.8, mec=P.SURFACE, mew=0.7, ls="none", zorder=3)
    ax.set_xlim(0, 30)
    ax.set_title("2021 overlap", loc="left", fontsize=7.5)
    ax.set_xlabel("Papers in both tiers")

    for ax in axes:
        ax.set_ylim(-0.6, len(names) - 0.2)
        ax.set_yticks(y)
        ax.set_yticklabels(names if ax is axes[0] else [], fontsize=6.5)
        ax.grid(axis="y", visible=False)
    hl = [Line2D([], [], ls="none", marker="o", ms=3.8, color=P.INK2, mfc=P.SURFACE, mew=0.9, label="NeurIPS 2014 size"),
          Line2D([], [], ls="none", marker="o", ms=3.8, color=P.INK2, mec=P.SURFACE, label="NeurIPS 2026 size"),
          plt.Rectangle((0, 0), 1, 1, color=P.GRID, label="Gaussian, reliability range (2026)"),
          Line2D([], [], color=P.BLUE[300], lw=2.0, label="90% range of the 2021 replay"),
          Line2D([], [], color=P.INK, lw=1.0, label="observed at NeurIPS 2021 (3)")]
    fig.legend(handles=hl, loc="upper center", bbox_to_anchor=(0.5, -0.02), ncol=3, handlelength=1.2, fontsize=6.6)
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
