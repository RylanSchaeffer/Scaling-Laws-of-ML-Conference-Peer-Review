"""Every figure of the report and paper, from results/*.csv.

Simulation results come from the sweep CSVs; analytic curves come from
results/analytic_curves.csv (scripts/make_analytic_curves.py), so every plotted
number traces to a CSV row. Figures go to figures/fig{n}_{name}.pdf and .png. The file
number n is the report's numbering; the paper orders them 1, 5, 2, 7, 3, 4, 6.

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
ROW_H = 1.72  # height of one row of panels, inches


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
# Figure 1: papers per year; fixed number versus fixed percentage (the main result)
# ---------------------------------------------------------------------------


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


def fig_main():
    """(a) Papers submitted, accepted and given orals per year. (b) Fixed-number against
    fixed-percentage precision: each pair is the same set at N = 1,000 (top 10 = top 1%,
    top 100 = top 10%), then they diverge."""
    g = load("sweep_g")
    fig, axes = plt.subplots(1, 2, figsize=(P.TEXTWIDTH_IN, 2.2),
                             gridspec_kw=dict(wspace=0.3, width_ratios=[1, 1.5]))
    submissions_panel(axes[0])

    ax = axes[1]
    series = (  # (kind, size, simulated column, colour, label, label y offset at N = 1e6)
        ("K", 100, "prec_K100", P.BLUE[700], "top 100", 0.012),
        ("K", 10, "prec_K10", P.BLUE[400], "top 10", -0.012),
        ("p", 0.10, "prec_acc0.10", P.ORANGE[600], "top 10%", 0.0),
        ("p", 0.01, "prec_p1pct", P.ORANGE[450], "top 1%", 0.0),
    )
    for kind, size, col, c, label, dy in series:
        q, kw = ("prec_K", dict(K=size)) if kind == "K" else ("prec_pct_finite", dict(p=size))
        cen, lo, hi = (A(q, lev, **kw) for lev in ("central", "pessimistic", "optimistic"))
        if size == 10:  # one band, for the headline series; figure 5a shows fixed-share bands
            ax.fill_between(cen.N, lo.value, hi.value, color=c, alpha=0.13, lw=0)
        ax.plot(cen.N, cen.value, color=c, lw=1.6)
        sim_points(ax, g, col, c)
        ax.text(1.3e6, cen.value.iloc[-1] + dy, label, fontsize=7, color=P.INK2, va="center", ha="left",
                clip_on=False)
    P.n_axis(ax)
    ax.set_ylim(0, 0.62)
    ax.set_yticks([0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6])
    P.pct_axis(ax)
    ax.set_ylabel("Precision of the selection")
    ax.set_title("Fixed number falls, fixed percentage holds", loc="left")
    mark_venues(ax, label=True, y=0.99)
    ax.legend(handles=sim_legend_handles(), loc="lower left", handlelength=1.3, borderaxespad=0.2)
    for i, a in enumerate(fig.axes):
        P.panel_label(a, "ab"[i])
    P.save(fig, os.path.join(FIG, "fig1_main"))


# ---------------------------------------------------------------------------
# Figure 2: mechanism, best-paper probability, local slope
# ---------------------------------------------------------------------------


def fig_mechanism():
    h = load("sweep_h")
    fig, axes = plt.subplots(1, 3, figsize=(P.TEXTWIDTH_IN, ROW_H), gridspec_kw=dict(wspace=0.62))

    ax = axes[0]
    bar = A("E_kth_best", "central", K=10)
    top = A("E_quality_top_score", "central")
    sd = A("cond_sd", "central").value.iloc[0]
    ax.plot(bar.N, bar.value, color=P.INK, lw=1.6, label="true top-10 bar")
    ax.fill_between(top.N, top.value - sd, top.value + sd, color=P.BLUE[450], alpha=0.14, lw=0)
    ax.plot(top.N, top.value, color=P.BLUE[450], lw=1.6, label="top-scored, $\\pm$1 SD")
    ax.set_ylabel("Standardised quality")
    ax.set_ylim(0, 6)
    ax.legend(loc="upper left", handlelength=1.3, borderaxespad=0.2)
    ax.set_title("The gap grows with $N$", loc="left")
    P.n_axis(ax)

    ax = axes[1]
    for K, c in zip((1, 10, 30), (P.BLUE[700], P.BLUE[450], P.BLUE[250])):
        Aband(ax, "best_in_K", c, K=K, label=f"in the top {K}")
        sim_points(ax, h, f"best_in_K{K}", c)
    ax.set_ylim(0, 1)
    P.pct_axis(ax)
    ax.set_ylabel("P(best paper is selected)")
    ax.set_title("The best paper", loc="left")
    ax.legend(loc="upper right", handlelength=1.3, borderaxespad=0.2)
    P.n_axis(ax)
    mark_venues(ax)

    ax = axes[2]
    for lev, c in zip(LEV, (P.ORANGE[450], P.BLUE[450], P.CAT[2])):
        sl = A("local_slope", lev, K=10)
        beta = A("beta", lev).value.iloc[0]
        ax.plot(sl.N, sl.value, color=c, lw=1.6, label=f"$\\rho^2$ = {LEVELS[lev]:.2f}")
        ax.axhline(-beta, color=c, lw=0.9, ls=(0, (3, 2)))
    ax.set_ylabel("Log-log slope of top-10 precision")
    ax.set_title("Faster than the limit", loc="left")
    ax.legend(loc="lower right", handlelength=1.3, borderaxespad=0.2)
    ax.set_ylim(-0.5, 0)
    P.n_axis(ax)
    for i, a in enumerate(axes):
        P.panel_label(a, "abc"[i])
    P.save(fig, os.path.join(FIG, "fig2_mechanism"))


# ---------------------------------------------------------------------------
# Figure 3: review-system parameters (reliability, reviewers, shared noise)
# ---------------------------------------------------------------------------


def fig_parameters():
    c_s, b = load("sweep_c"), load("sweep_b")
    fig, axes = plt.subplots(1, 3, figsize=(P.TEXTWIDTH_IN, ROW_H), gridspec_kw=dict(wspace=0.62))

    ax = axes[0]
    ac = _AC if _AC is not None else load("analytic_curves")
    curve = ac[ac.quantity == "prec_K_vs_rho2"]
    for N, col in zip((1e3, 1e4, 1e5, 1e6), (P.BLUE[250], P.BLUE[400], P.BLUE[550], P.BLUE[700])):
        d = curve[np.isclose(curve.N, N)].sort_values("rho2")
        ax.plot(d.rho2, d.value, color=col, lw=1.6, label=f"$N$ = {P.fmt_count(N)}")
        s = c_s[np.isclose(c_s.N, N) & (c_s.rho2 <= 0.95)]
        ax.plot(s.rho2, s.prec_K10, ls="none", marker="o", ms=3.4, color=col, mec=P.SURFACE, mew=0.7)
    for lev in LEV:
        ax.axvline(LEVELS[lev], color=P.MUTED, lw=0.6, ls=(0, (2, 2)), zorder=0)
    ax.set_xlabel("Reliability $\\rho^2$ of the mean score")
    ax.set_ylabel("Top-10 precision")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    P.pct_axis(ax)
    ax.legend(loc="upper left", handlelength=1.3, borderaxespad=0.2)
    ax.set_title("Only $\\rho^2$ matters", loc="left")

    ax = axes[1]
    d = b[(b.level == "central") & (b.N == 20000)]
    for su, c, ls in ((0.0, P.BLUE[450], "-"), (0.5, P.ORANGE[450], "-")):
        e = d[np.isclose(d.sigma_u, su)].sort_values("R")
        lab = "$\\sigma_u$ = 0" if su == 0 else "$\\sigma_u$ = 0.5"
        ax.plot(e.R, e.prec_K10, color=c, lw=1.6, marker="o", ms=3.4, mec=P.SURFACE, mew=0.7, label=lab)
    ax.axvline(3, color=P.MUTED, lw=0.6, ls=(0, (2, 2)), zorder=0)
    ax.set_xscale("log")
    ax.set_xticks([1, 2, 3, 5, 10, 20, 50])
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda v, _p: f"{v:g}"))
    ax.xaxis.set_minor_locator(plt.NullLocator())
    ax.set_xlabel("Reviews per paper $R$")
    ax.set_ylabel("Top-10 precision at $N$ = 20K")
    ax.set_ylim(0, 0.8)
    P.pct_axis(ax)
    ax.legend(loc="lower right", handlelength=1.3, borderaxespad=0.2)
    ax.set_title("A ceiling on reviewers", loc="left")

    ax = axes[2]
    rn = load("analytic_R_needed")
    for su, c in ((0.0, P.BLUE[450]), (0.5, P.ORANGE[450])):
        e = rn[np.isclose(rn.sigma_u, su)].sort_values("N")
        lab = "$\\sigma_u$ = 0" if su == 0 else "$\\sigma_u$ = 0.5"
        ax.plot(e.N, e.R_needed, color=c, lw=1.6, marker="o", ms=3.4, mec=P.SURFACE, mew=0.7, label=lab)
    P.n_axis(ax)
    ax.set_ylim(0, 28)
    ax.set_ylabel("Reviews per paper needed")
    ax.set_title("Reviews to hold top 10", loc="left")
    ax.legend(loc="upper left", handlelength=1.3, borderaxespad=0.2)
    mark_venues(ax)
    for i, a in enumerate(axes):
        P.panel_label(a, "abc"[i])
    P.save(fig, os.path.join(FIG, "fig3_parameters"))


# ---------------------------------------------------------------------------
# Figure 4: robustness (quality tails, noise tails, score scales)
# ---------------------------------------------------------------------------

QUAL_LABEL = {"gaussian": "Gaussian", "beta": "bounded", "exp": "exponential",
              "lognormal": "lognormal", "t3": "$t_3$"}
QUAL_ORDER = ("t3", "exp", "lognormal", "gaussian", "beta")
SCALE_LABEL = {"continuous": "continuous", "int10": "1-10", "iclr6": "ICLR",
               "six": "6-point", "five": "5-point"}
SCALE_ORDER = ("continuous", "int10", "iclr6", "six", "five")


def fig_robustness():
    d, e = load("sweep_d"), load("sweep_e")
    fig, axes = plt.subplots(1, 3, figsize=(P.TEXTWIDTH_IN, ROW_H + 0.1), gridspec_kw=dict(wspace=0.38))
    for ax, noise, title in ((axes[0], "gaussian", "Gaussian reviewer noise"), (axes[1], "t3", "Heavy-tailed ($t_3$) noise")):
        for i, qd in enumerate(QUAL_ORDER):
            s = d[(d.noise == noise) & (d.quality == qd)]
            c = P.CAT[i]
            cen = s[s.level == "central"].sort_values("N")
            ax.plot(cen.N, cen.prec_K10, color=c, lw=1.6, marker="o", ms=3.0, mec=P.SURFACE, mew=0.6,
                    label=QUAL_LABEL[qd])
        ax.set_title(title, loc="left")
        P.n_axis(ax)
        ax.set_ylim(0, 1)
        P.pct_axis(ax)
    axes[0].set_ylabel("Top-10 precision")
    # One quality legend serves panels a and b; the upper left of b is empty above its curves.
    axes[1].legend(loc="upper left", ncol=2, handlelength=1.0, columnspacing=0.5, borderaxespad=0.2)

    ax = axes[2]
    st = e[(e.placement == "standard")]
    for i, sc in enumerate(SCALE_ORDER):
        s = st[st.scale == sc]
        c = [P.INK, P.BLUE[450], P.CAT[1], P.CAT[2], P.CAT[6]][i]
        cen = s[s.level == "central"].sort_values("N")
        ax.plot(cen.N, cen.prec_K10, color=c, lw=1.6, marker="o", ms=3.0, mec=P.SURFACE, mew=0.6,
                label=SCALE_LABEL[sc])
    ax.set_title("Discrete scores ($R$ = 4)", loc="left")
    ax.set_yscale("log")
    ax.set_ylim(1e-3, 0.5)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _p: f"{100 * v:g}%"))
    P.n_axis(ax)
    ax.legend(loc="lower left", handlelength=1.3, borderaxespad=0.2, title="Score scale", title_fontsize=7)
    for i, a in enumerate(axes):
        P.panel_label(a, "abc"[i])
    P.save(fig, os.path.join(FIG, "fig4_robustness"))


# ---------------------------------------------------------------------------
# Figure 5: the accept/reject boundary
# ---------------------------------------------------------------------------


def fig_boundary():
    f, h, d, e = load("sweep_f"), load("history"), load("sweep_d"), load("sweep_e")
    fig, axes = plt.subplots(1, 3, figsize=(P.TEXTWIDTH_IN, ROW_H + 0.1),
                             gridspec_kw=dict(wspace=1.05, width_ratios=[1, 1, 0.75]))
    alphas = np.array([0.10, 0.15, 0.20, 0.25, 0.30, 0.35, 0.40])

    ax = axes[0]
    for col, label, c, q in (("dis", "rejected on a rerun", P.ORANGE[450], "dis"),
                             ("swap", "not in the true top $\\alpha N$", P.BLUE[450], "prec_pct")):
        vals = {}
        for lev in LEV:
            cur = np.array([A(q, lev, p=a).value.iloc[0] for a in alphas])
            vals[lev] = 1 - cur if q == "prec_pct" else cur
        ax.fill_between(alphas, vals["pessimistic"], vals["optimistic"], color=c, alpha=0.14, lw=0)
        ax.plot(alphas, vals["central"], color=c, lw=1.6, label=label)
        s = f[f.level == "central"].iloc[0]
        ax.plot(alphas, [s[f"{col}_acc{a:.2f}"] for a in alphas], ls="none", marker="o", ms=3.4, color=c,
                mec=P.SURFACE, mew=0.7)
    ax.set_xlabel("Acceptance rate $\\alpha$")
    ax.set_ylim(0, 0.8)
    P.pct_axis(ax)
    P.pct_axis(ax, "x")
    ax.set_xticks([0.1, 0.2, 0.3, 0.4])
    ax.set_ylabel("Share of accepted papers")
    ax.legend(loc="lower left", handlelength=1.3, borderaxespad=0.2)
    ax.set_title("Acceptance rate", loc="left")

    ax = axes[1]
    for venue, c, mk in (("NeurIPS", P.BLUE[450], "o"), ("ICML", P.CAT[1], "s"), ("ICLR", P.CAT[2], "^")):
        s = h[(h.venue == venue) & (h.denominator != "decided")]
        cen = s[s.level == "central"].sort_values("year")
        lo, hi = (s[s.level == lev].sort_values("year") for lev in ("pessimistic", "optimistic"))
        ax.fill_between(cen.year, lo.wrong_accepts, hi.wrong_accepts, color=c, alpha=0.12, lw=0)
        ax.plot(cen.year, cen.wrong_accepts, color=c, lw=1.6, marker=mk, ms=3.4, mec=P.SURFACE, mew=0.7, label=venue)
    ax.set_ylabel("Wrong accepts per conference")
    ax.set_xlabel("Year")
    ax.set_xticks([2014, 2018, 2022, 2026])
    ax.set_title("Wrong accepts grow", loc="left")
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _p: f"{v:,.0f}"))
    ax.legend(loc="upper left", handlelength=1.3, borderaxespad=0.2)

    ax = axes[2]
    short = {"t3": "$t_3$", "exp": "exp.", "lognormal": "lognorm.", "gaussian": "Gauss.", "beta": "bounded"}
    rows = []
    for qd in QUAL_ORDER:
        for noise in ("gaussian", "t3"):
            s = d[(d.quality == qd) & (d.noise == noise) & (d.level == "central") & (d.N == 100_000)]
            rows.append((f"{short[qd]} / {'Gauss.' if noise == 'gaussian' else '$t_3$'}", s["swap_acc0.25"].iloc[0],
                         P.CAT[QUAL_ORDER.index(qd)]))
    for sc, lab in zip(SCALE_ORDER[1:], ("1-10", "ICLR 6-pt", "6-point", "5-point")):
        s = e[(e.scale == sc) & (e.placement == "standard") & (e.level == "central") & (e.N == 100_000)]
        rows.append((f"{lab} scale", s["swap_acc0.25"].iloc[0], P.INK2))
    y = np.arange(len(rows))[::-1]
    for yi, (lab, v, c) in zip(y, rows):
        ax.plot([0, v], [yi, yi], color=P.GRID, lw=1.0, zorder=1)
        ax.plot(v, yi, "o", color=c, ms=4.2, mec=P.SURFACE, mew=0.7, zorder=3)
    ax.set_yticks(y)
    ax.set_yticklabels([r[0] for r in rows], fontsize=6.3)
    ax.set_xlim(0, 0.5)
    ax.set_xticks([0, 0.25, 0.5])
    P.pct_axis(ax, "x")
    ax.set_xlabel("Swap fraction, $\\alpha$ = 25%")
    ax.grid(axis="y", visible=False)
    ax.set_title("Every variant", loc="left")
    for i, a in enumerate(axes):
        P.panel_label(a, "abc"[i])
    P.save(fig, os.path.join(FIG, "fig5_boundary"))


# ---------------------------------------------------------------------------
# Figure 6: out-of-sample validation
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
    P.save(fig, os.path.join(FIG, "fig6_validation"))


# ---------------------------------------------------------------------------
# Figure 7: the model at each real venue-year (paper Fig. 4)
# ---------------------------------------------------------------------------


def fig_history():
    """The central model at each real venue-year (results/history.csv): top-10 precision,
    precision of the real oral set, and the chance that the best paper is in the top 10.
    Bands span the pessimistic and optimistic levels."""
    h = load("history")
    fig, axes = plt.subplots(1, 3, figsize=(P.TEXTWIDTH_IN, ROW_H), gridspec_kw=dict(wspace=0.6))
    panels = ((axes[0], "prec_K10", "Top 10 by score", "Precision"),
              (axes[1], "prec_orals", "Real oral set", "Precision"),
              (axes[2], "best_in_K10", "Best paper in top 10", "Probability"))
    for ax, col, title, ylabel in panels:
        for venue, c, mk in (("NeurIPS", P.BLUE[450], "o"), ("ICML", P.CAT[1], "s"), ("ICLR", P.CAT[2], "^")):
            s = h[(h.venue == venue) & (h.denominator != "decided")].dropna(subset=[col])
            cen = s[s.level == "central"].sort_values("year")
            lo, hi = (s[s.level == lev].sort_values("year") for lev in ("pessimistic", "optimistic"))
            if venue == "NeurIPS":  # one band, for the longest series
                ax.fill_between(cen.year, lo[col], hi[col], color=c, alpha=0.13, lw=0)
            ax.plot(cen.year, cen[col], color=c, lw=1.6, marker=mk, ms=3.2, mec=P.SURFACE, mew=0.6, label=venue)
        ax.set_ylim(0, 0.62 if col != "best_in_K10" else 0.82)
        P.pct_axis(ax)
        ax.set_xticks([2014, 2018, 2022, 2026])
        ax.set_xlim(2013.3, 2026.7)
        ax.set_xlabel("Year")
        ax.set_ylabel(ylabel)
        ax.set_title(title, loc="left")
    axes[0].legend(loc="upper right", handlelength=1.3, borderaxespad=0.2)
    for i, a in enumerate(axes):
        P.panel_label(a, "abc"[i])
    P.save(fig, os.path.join(FIG, "fig7_history"))


FIGURES = dict(main=fig_main, mechanism=fig_mechanism, parameters=fig_parameters, robustness=fig_robustness,
               boundary=fig_boundary, validation=fig_validation, history=fig_history)


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
