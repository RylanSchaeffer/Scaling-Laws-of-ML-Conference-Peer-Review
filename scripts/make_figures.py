"""Every figure of the paper, from results/*.csv.

Simulation results come from the sweep and robustness CSVs; analytic curves come from
results/analytic_curves.csv, results/analytic_R_needed.csv, results/best_paper.csv and
results/tier_scaling.csv, so every plotted number traces to a CSV row. Figures go to
figures/fig{n}_{name}.pdf and .png. The file numbers predate the merge of the scaling row into
Fig 1: from fig2_validation on, file fig{n} is the paper's Fig n-1.

Usage: uv run python scripts/make_figures.py [names...]
"""

from __future__ import annotations

import argparse
import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from peerreview.tiers import LABEL, tier_size
from matplotlib.lines import Line2D
from matplotlib.ticker import FixedLocator, NullLocator

from peerreview import plotting as P
from peerreview.levels import LEVELS, ROOT

RES = os.path.join(ROOT, "results")
FIG = os.path.join(ROOT, "figures")
LEV = ("pessimistic", "central", "optimistic")
NEURIPS = {2014: 1678, 2026: 30709}
ROW_H = 1.69  # height of one row of panels, inches as printed (drawn at ROW_H * P.S)
LEGEND_GAP_IN = 0.20 * ROW_H  # from the bottom of a row's axes to the top of a legend below it, inches as printed


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


def Aband(ax, quantity, color, K=None, label=None, lw=1.6 * P.S, band=True):
    """Analytic central line, optionally with the pessimistic-optimistic band."""
    c, lo, hi = (A(quantity, lev, K=K) for lev in ("central", "pessimistic", "optimistic"))
    if band:
        ax.fill_between(c.N, lo.value, hi.value, color=color, alpha=0.14, lw=0)
    ax.plot(c.N, c.value, color=color, lw=lw, label=label)


def sim_points(ax, df, col, color, level="central", marker="o", ms=3.6 * P.S, zorder=4):
    d = df[df.level == level].sort_values("N")
    ax.plot(d.N, d[col], ls="none", marker=marker, ms=ms, color=color, mec=P.SURFACE, mew=0.7 * P.S, zorder=zorder)


def mark_venues(ax, label=False, y=0.97, va="top"):
    """Dotted lines at NeurIPS 2014 and 2026 submissions; label=True names them (once per figure)."""
    dy = -0.09 if va == "top" else 0.09  # the second label sits one line below (or above) the first
    for i, (yr, n) in enumerate(sorted(NEURIPS.items())):
        ax.axvline(n, color=P.MUTED, lw=0.6 * P.S, ls=(0, (2, 2)), zorder=0)
        if label:
            text = f"NeurIPS {yr}" if yr == min(NEURIPS) else f"{yr}"
            ax.text(n * 1.08, y + i * dy, text, color=P.INK2, va=va, ha="left", fontsize=P.LEGEND_PT,
                    transform=ax.get_xaxis_transform())


def sim_legend_handles():
    return [Line2D([], [], color=P.INK2, lw=1.6 * P.S, label="Theory"),
            Line2D([], [], color=P.INK2, ls="none", marker="o", ms=3.6 * P.S, mec=P.SURFACE, label="Simulation")]


# ---------------------------------------------------------------------------
# Figure 1: growth, NeurIPS tier proportions, and the NeurIPS Best Papers under a second review
# ---------------------------------------------------------------------------

VENUES = (("NeurIPS", P.BLUE[450], "o"), ("ICML", P.CAT[1], "s"), ("ICLR", P.CAT[2], "^"))  # blue, orange, green (the author's choice)
SEP_TIERS = (  # (key, colour, label): the five separate tiers, gold to last (peerreview.tiers, docs/terminology.md)
    ("best", P.INK, "Best Papers"),
    ("oral", P.BLUE[450], "Oral"),
    ("spot", P.BLUE[250], "Spotlight"),
    ("accept", P.MUTED, "Accepted"),  # accepted with no award
    ("reject", P.ORANGE[450], "Rejected"),
)
TIERS = tuple((label, c) for _, c, label in SEP_TIERS)  # (label, colour), for Fig 1c
LIGHT = {P.BLUE[250], P.MUTED}  # segments that take dark text


def tier_proportions(r) -> list[float]:
    """The separate tier a second review gives one of the Best Papers, in SEP_TIERS order (one best_paper.csv row); sums to 1."""
    return [r[f"p2_{k}"] for k, _, _ in SEP_TIERS]


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


def submissions_panel(ax):
    """Papers submitted per year at NeurIPS, ICML and ICLR (data/venues.csv, N_used)."""
    v = venue_counts()
    for venue, c, mk in VENUES:
        s = v[v.venue == venue]
        ax.plot(s.year, s.N_used, color=c, lw=1.6 * P.S, marker=mk, ms=3.0 * P.S, mew=0, label=venue)
    ax.set_yscale("log")
    ax.set_ylim(400, 1e5)
    ax.yaxis.set_major_locator(FixedLocator([1e3, 1e4, 1e5]))
    ax.yaxis.set_minor_locator(NullLocator())
    ax.yaxis.set_major_formatter(plt.FuncFormatter(P.fmt_count))
    ax.set_xticks([2014, 2020, 2026])
    ax.set_xlim(2013.3, 2026.7)
    ax.set_xlabel("Year")
    ax.set_ylabel("Papers submitted")
    ax.set_title("Submissions", loc="left")
    ax.legend(loc="upper left", handlelength=1.2, borderaxespad=0.2, labelspacing=0.25, handletextpad=0.5)


RATE_TIERS = (  # (count series in results/tier_sizes.csv, count column of venue_counts(), colour, label end, label side)
    ("accept_or_better", "accepted", P.MUTED, "left", "above"),  # every accepted paper; each label sits where no marker lies
    ("spot", "spotlights", P.BLUE[250], "left", "above"),  # Spotlights only
    ("oral_or_better", "orals_used", P.BLUE[450], "right", "below"),  # NeurIPS's Orals, which include its Best Papers
)  # Best Papers (1 to 13 a year; the `best` row of tier_sizes.csv) are fitted but not drawn: too few to show a trend


def rates_panel(ax):
    """Is each NeurIPS tier a constant number, a fixed proportion of submissions, or something
    between? Markers: each year's main-track count over submissions, against that year's
    submissions (no spotlight tier in 2016 and 2022; best-paper awards, 1 to 13 a year, are too few to
    draw). Lines: the fitted power law count = a N^gamma (results/tier_sizes.csv) over the
    fitted years' range of N. On log-log axes a fixed proportion (gamma = 1) is flat and a fixed
    number (gamma = 0) falls as 1/N; the label gives each tier's gamma."""
    s = venue_counts().query("venue == 'NeurIPS'").assign(accepted=lambda d: d.N_used * d.acc_rate_used)
    fits = load("tier_sizes").set_index("tier")
    for tier, col, c, end, side in RATE_TIERS:
        f = fits.loc[tier]
        d = s[s[col].notna() & (s[col] > 0)]
        ax.plot(d.N_used, d[col] / d.N_used, ls="none", marker="o", ms=2.6 * P.S, color=c, mew=0)
        yrs = s[(s.year >= f.year_min) & (s.year <= f.year_max)]
        x0, x1 = yrs.N_used.min(), yrs.N_used.max()
        ax.plot([x0, x1], [f.a * x0 ** (f.gamma - 1), f.a * x1 ** (f.gamma - 1)], color=c, lw=1.4 * P.S)
        label = LABEL[tier]
        tc = P.INK2  # annotations in ink, not in the series colour
        xe = x0 if end == "left" else x1
        lo, hi = P.N_TICKS[0] / 1.15, P.N_TICKS[-1] * 1.15  # the axis limits of P.n_axis
        x = lo * 1.04 if end == "left" else hi / 1.1  # labels start at the frame, so the long ones fit
        y = f.a * xe ** (f.gamma - 1) * (1.45 if side == "above" else 1 / 1.5)
        ax.text(x, y, f"{label} $\\propto N^{{{f.gamma:.2f}}}$", color=tc, ha=end, va="bottom" if side == "above" else "top", fontsize=P.LEGEND_PT)
    ax.set_yscale("log")
    ax.set_ylim(1e-3, 0.9)  # nothing is drawn above 30%; room below the Oral or Better line for its label
    ax.yaxis.set_major_locator(FixedLocator([0.003, 0.01, 0.03, 0.1, 0.3]))
    ax.yaxis.set_minor_locator(NullLocator())
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{100 * x:g}\\%"))
    P.n_axis(ax)
    ax.set_ylabel("Proportion of submissions")
    ax.set_title("NeurIPS tiers", loc="left")

Y_FLOOR = 0.00008  # shared y axis of Fig 1d-g: 0.01% to 100%
Y_TICKS = [0.0001, 0.001, 0.01, 0.1, 1.0]


def log_prob_axis(ax):
    P.n_axis(ax)
    ax.set_yscale("log")
    ax.set_ylim(Y_FLOOR, 1.0)
    ax.yaxis.set_major_locator(FixedLocator(Y_TICKS))
    ax.yaxis.set_minor_locator(NullLocator())
    P.pct_axis(ax)


def fig_headline(stem: str = "fig1_headline"):
    """Figure 1: two rows. (a) Papers submitted per year. (b) NeurIPS tiers as a proportion of submissions,
    with the fitted power law of each tier's count. (c) Where a second review would rank the NeurIPS Best
    Papers in 2014, 2021 and 2026 (results/best_paper.csv). (d-g) The scaling laws of a second review for a
    paper the first review made one of its Best Papers, an Oral, a Spotlight, or Accepted or Better (scaling_row).
    Each row's panels are as tall as in the one-row figures (1.1 and ROW_H inches printed, at the default
    subplot margins), so nothing inside a panel moves."""
    top_h, bot_h, hspace = 1.1, ROW_H, 0.62
    margins = 0.11 + 0.12  # matplotlib's default bottom and top subplot margins, as a fraction of the figure
    plot_h = (1 - margins) * (top_h + bot_h)  # axes heights of the two one-row figures, summed
    H = (plot_h + hspace * plot_h / 2) / (1 - margins)  # figure height that gives those axes heights with the gap between the rows
    fig = plt.figure(figsize=(P.CANVAS_W, H * P.S))
    gs = fig.add_gridspec(2, 1, height_ratios=[top_h, bot_h], hspace=hspace)
    top = gs[0].subgridspec(1, 3, width_ratios=[1, 1, 1.7], wspace=0.4)  # (c) is wide so its narrow segments can carry labels
    bot = gs[1].subgridspec(1, 4, wspace=0.42)
    axes = [fig.add_subplot(top[0, i]) for i in range(3)]
    submissions_panel(axes[0])
    rates_panel(axes[1])
    standing_panel(axes[2])
    for i, a in enumerate(axes):
        P.panel_label(a, "abc"[i])
    row = [fig.add_subplot(bot[0, i]) for i in range(4)]
    scaling_row(fig, row)
    for i, a in enumerate(row):
        P.panel_label(a, "defg"[i])
    P.save(fig, os.path.join(FIG, stem))


def standing_panel(ax):
    """Stacked bars: where a second review would rank a paper among the first review's Best Papers
    (one of the first three of its award ordering) at NeurIPS 2014, 2021 and 2026 size, central level (results/best_paper.csv)."""
    b = venue_rows()
    years = (2026, 2021, 2014)
    for y, yr in enumerate(years):
        r = b[(b.venue == "NeurIPS") & (b.year == yr)].iloc[0]
        left = 0.0
        for (lab, c), w in zip(TIERS, tier_proportions(r)):
            ax.barh(y, w, left=left, height=0.62, color=c, edgecolor=P.SURFACE, lw=0.8 * P.S)
            if w >= 0.05:  # every segment from 5% up carries its value; narrow segments take a smaller label so it stays inside
                fs = P.LEGEND_PT if w >= 0.08 else 0.72 * P.LEGEND_PT
                ax.text(left + w / 2, y, f"{100 * w:.0f}\\%", ha="center", va="center", color=P.INK if c in LIGHT else P.SURFACE, fontsize=fs)
            left += w
    ax.set_yticks(range(len(years)))
    ax.set_yticklabels([str(yr) for yr in years])
    ax.tick_params(axis="y", length=0)
    ax.set_xlim(0, 1)
    ax.set_ylim(-0.5, 3.8)  # room for a two-row legend above the bars
    ax.set_xticks([0, 0.25, 0.5, 0.75, 1])
    P.pct_axis(ax, "x")
    ax.set_xlabel("Probability")
    ax.grid(axis="y", visible=False)
    ax.set_title("NeurIPS Best Papers, reviewed again", loc="left")
    handles = [plt.Rectangle((0, 0), 1, 1, color=c, label=lab) for lab, c in TIERS]
    handles = [handles[i] for i in (0, 3, 1, 4, 2)]  # column-major fill reads row-wise in bar order
    ax.legend(handles=handles, loc="upper left", ncol=3, handlelength=0.8, columnspacing=0.8,
              borderaxespad=0.1, handletextpad=0.3)


# ---------------------------------------------------------------------------
# Figure 2: is the model faithful? (held-out tests)
# ---------------------------------------------------------------------------

VAR_LABEL = {  # rows of Fig 4a,b: the main model and the variants of the robustness section, in Fig 6's order
    "gauss/gauss": "Main model", "gauss/gauss/noaward": "No award step", "beta/gauss": "Bounded quality", "exp/gauss": "Exponential quality",
    "lognormal/gauss": "Lognormal quality", "t3/gauss": "$t_3$ quality", "gauss/t3": "$t_3$ noise",
    "gauss/gauss+shared": "Shared noise", "careless1": "1\\% rave reviews", "careless5": "5\\% rave reviews",
    "random5": "5\\% random reviews"}


def fig_validation():
    """(c) ICLR split halves: observed against model overlap of the accepted, top-30 and top-3
    sets (three: the Best Papers' size), reviewer noise fitted per year. (a, b) The NeurIPS 2021 experiment under the main model and the
    nine variants of the robustness section (results/validation_neurips2021.csv):
    papers in both committees' Spotlight or Better sets (Orals plus Spotlights; the experiment had no Best Papers tier),
    and the proportion of one committee's Spotlight or Better papers the other rejects; central level (circles,
    90% range) and pessimistic level (diamonds)."""
    v, ic = load("validation_neurips2021"), load("validation_iclr")
    fig, axes = plt.subplots(1, 3, figsize=(P.CANVAS_W, (ROW_H + 0.7) * P.S), gridspec_kw=dict(wspace=0.36))
    sub = v[v.design == "subsample"]
    vv = sub[sub.level == "central"].set_index("variant").loc[list(VAR_LABEL)]
    vp = sub[sub.level == "pessimistic"].set_index("variant").reindex(list(VAR_LABEL))  # NaN where not calibrated
    y = np.arange(len(vv))[::-1].astype(float)

    ax = axes[2]  # ICLR on the right: the variant row labels of (a) need the left margin
    ICLR_LO = 0.005  # floor of the log axes
    d = ic[(ic.placement == "observed") & (ic.in_main.astype(str) == "True")]
    for (oc, mc, lab, c, mk) in (("obs_precision", "model_precision", "Accepted or Better", P.MUTED, "o"),
                                 ("obs_top30", "model_top30", "Top 30", P.BLUE[450], "s"),
                                 ("obs_top3", "model_top3", "Top 3", P.INK, "^")):
        sd = d[oc + "_sd"].values if oc + "_sd" in d else np.zeros(len(d))  # SD over the random splits
        err = np.vstack([np.minimum(sd, d[oc].values - 1.02 * ICLR_LO), sd])  # the lower bar stops at the floor of the log axes
        ax.errorbar(d[mc], d[oc], yerr=err, ls="none", marker=mk, ms=4.2 * P.S, color=c, elinewidth=0.8 * P.S,
                    capsize=0, label=lab)
    ax.plot([ICLR_LO, 1], [ICLR_LO, 1], color=P.MUTED, lw=0.8 * P.S, ls=(0, (3, 2)))  # observed = model
    for set_scale, set_lim, set_ticks, axis in ((ax.set_xscale, ax.set_xlim, ax.set_xticks, "x"), (ax.set_yscale, ax.set_ylim, ax.set_yticks, "y")):
        set_scale("log")  # log axes: the top-three overlaps, a few percent, would pile up at the origin on linear ones
        set_lim(ICLR_LO, 1)
        set_ticks([0.01, 0.1, 1])
        (ax.xaxis if axis == "x" else ax.yaxis).set_minor_locator(NullLocator())
        (ax.xaxis if axis == "x" else ax.yaxis).set_major_formatter(plt.FuncFormatter(lambda v, _p: f"{100 * v:g}\\%"))
    ax.set_xlabel("Model overlap")
    ax.set_ylabel("Observed overlap")
    ax.legend(loc="upper left", handlelength=1.0, borderaxespad=0.2)
    ax.set_title("ICLR split-half overlap", loc="left")

    def rows(ax, cen, pes, lo, hi, mean, obs, obs_text, c_bar, c_dot, xlim):
        ax.axvline(obs, color=P.INK, lw=1.0 * P.S)
        left = obs < sum(xlim) / 2
        ax.text(obs + (0.02 if left else -0.02) * (xlim[1] - xlim[0]), y.max() + 0.75, obs_text, color=P.INK,
                va="center", ha="left" if left else "right", fontsize=P.LEGEND_PT)  # beside the line, roomier side
        ax.hlines(y, cen[lo], cen[hi], color=c_bar, lw=2.0 * P.S)
        ax.plot(cen[mean], y, "o", color=c_dot, ms=4.4 * P.S, mec=P.SURFACE, mew=0.7 * P.S)
        ok = pes[mean].notna().values
        ax.plot(pes[mean].values[ok], (y - 0.3)[ok], "D", color=c_dot, ms=3.0 * P.S, mec=P.SURFACE, mew=0.7 * P.S, ls="none")
        ax.set_xlim(*xlim)
        ax.set_ylim(-0.7, y.max() + 1.15)
        ax.grid(axis="y", visible=False)

    ax = axes[0]
    rows(ax, vv, vp, "sob_overlap_q05", "sob_overlap_q95", "sob_overlap_mean", 3, "Observed 3", P.BLUE[300], P.BLUE[450], (0, 20))
    ax.set_xticks([0, 10, 20])
    ax.set_yticks(y)
    ax.set_yticklabels([VAR_LABEL[k] for k in vv.index])
    ax.set_xlabel("Chosen by both committees")
    ax.set_title("NeurIPS 2021 Spotlight or Better", loc="left")

    ax = axes[1]
    obs = vv.obs_sob_rej_share.iloc[0]  # 26 of the 54 Spotlight or Better papers, rejected by the other committee
    rows(ax, vv, vp, "sob_rej_share_q05", "sob_rej_share_q95", "sob_rej_share_mean", obs,
         f"Observed {100 * obs:.0f}\\%", P.ORANGE[300], P.ORANGE[450], (0, 0.7))
    ax.set_yticks(y)
    ax.set_yticklabels([])
    P.pct_axis(ax, "x")
    ax.set_xlabel("Rejected by the other committee")
    ax.set_title("The same papers, rejected", loc="left")
    hl = [Line2D([], [], ls="none", marker="o", ms=4.4 * P.S, color=P.INK2, mec=P.SURFACE, label=f"Central level, $\\rho^2$ = {LEVELS['central']:.2f}"),
          Line2D([], [], color=P.MUTED, lw=2.0 * P.S, label="90\\% range, central level"),
          Line2D([], [], ls="none", marker="D", ms=3.0 * P.S, color=P.INK2, mec=P.SURFACE, label=f"Pessimistic level, $\\rho^2$ = {LEVELS['pessimistic']:.2f}")]
    fig.legend(handles=hl, loc="upper center", bbox_to_anchor=(0.36, -0.08), ncol=3, handlelength=1.2)
    for i, a in enumerate(axes):
        P.panel_label(a, "abc"[i])
    P.save(fig, os.path.join(FIG, "fig2_validation"))


# ---------------------------------------------------------------------------
# Figure 3: the Best Papers and the tiers as N grows, and at every real venue-year
# ---------------------------------------------------------------------------


def experiment_points() -> list[tuple[str, str, int, float]]:
    """The two NeurIPS two-committee experiments as points of Fig 1d-g (data/experiments.json): for the papers one
    committee put in a group, the proportion the other committee put in each separate tier, pooled over both
    directions. Groups: the separate Oral and Spotlight tiers (2021 only; that experiment had no Best Papers tier) and
    Accepted or Better (2014 reported only acceptance). Zero proportions are left out (log axis).
    Returns (first-review group, second-review tier, submissions N, proportion)."""
    import json
    e = json.load(open(os.path.join(ROOT, "data", "experiments.json")))
    pts = []
    a = e["neurips2014"]["table_2x2"]["value"]
    pts.append(("accept_or_better", "reject", e["neurips2014"]["design"]["value"]["conference_submissions"],
                1 - 2 * a["both_accept"] / (a["committee_1_accepts"] + a["committee_2_accepts"])))
    n21 = e["neurips2021"]; N21 = n21["design"]["value"]["conference_submissions"]
    c = np.array(n21["table1"]["value"]["counts"])[:4, :4]  # rows: original Oral, Spotlight, Poster, Reject; columns: the copy
    rows = {"oral": [0], "spot": [1], "accept_or_better": [0, 1, 2]}  # first-review groups, as rows/columns of c
    cols = {"oral": 0, "spot": 1, "accept": 2, "reject": 3}  # second-review tiers (Poster = Accepted, no award)
    for first, idx in rows.items():
        n = c[idx, :].sum() + c[:, idx].sum()  # the group's papers, counted from both committees
        for second, j in cols.items():
            k = c[idx, j].sum() + c[j, idx].sum()
            if k:
                pts.append((first, second, N21, k / n))
    return pts


def scaling_row(fig, axes):
    """The scaling laws: the separate tier a second review gives a paper that the first review made one of its Best
    Papers (results/best_paper.csv grid rows, p2_*), an Oral or a Spotlight, or Accepted or Better
    (results/placement.csv, place_{first}_in_{tier}), against submissions N on NeurIPS's tier trends, central level.
    Each panel's five curves sum to 1; at the paper's own tier the curve is the tier's overlap. Draws into four axes
    of `fig` and puts the shared legend below the row, clear of the x-axis labels."""
    pl = load("placement")
    pl = pl[pl.level == "central"].sort_values("N")
    t = load("best_paper")
    t = t[(t.source == "grid") & (t.level == "central")].sort_values("N")
    panels = (("best", t, "p2_{}", "Best Papers"), ("oral", pl, "place_oral_in_{}", "Oral"),
              ("spot", pl, "place_spot_in_{}", "Spotlight"), ("accept_or_better", pl, "place_accept_or_better_in_{}", "Accepted or Better"))
    for ax, (_, d, col, title) in zip(axes, panels):
        for key, color, label in SEP_TIERS:
            ax.plot(d.N, d[col.format(key)], color=color, lw=1.6 * P.S, label=label)
        log_prob_axis(ax)
        ax.set_title(title, loc="left")
    panel = {first: ax for ax, (first, *_) in zip(axes, panels)}
    colour = {key: c for key, c, _ in SEP_TIERS}
    pts = experiment_points()
    for first, second, N, v in pts:  # the NeurIPS 2014 and 2021 experiments
        near = [w for f2, s2, N2, w in pts if f2 == first and N2 == N and s2 != second and abs(np.log10(w / v)) < 0.13]
        dx = (1.17 if v > near[0] else 1 / 1.17) if near else 1.0  # two markers that would overlap step apart sideways
        panel[first].plot([N * dx], [v], ls="none", marker="o", ms=4.2 * P.S, mfc=colour[second], mec=P.INK, mew=0.8 * P.S, zorder=7,
                          clip_on=False)  # the 6-of-6 Orals accepted with no award sit at 100%, on the frame
    for ax in axes:  # where we are this year: NeurIPS 2026 submissions
        ax.axvline(NEURIPS[2026], color=P.INK2, lw=0.9 * P.S, ls=(0, (4, 3)), zorder=0)
        ax.text(NEURIPS[2026] / 1.1, 0.0001, "2026", color=P.INK2, va="bottom", ha="right", fontsize=P.LEGEND_PT, zorder=6,
                bbox=dict(facecolor=P.SURFACE, edgecolor="none", pad=1.5))  # a white halo where a curve passes under the label
    axes[0].set_ylabel("Probability of each tier")
    h, l = axes[0].get_legend_handles_labels()  # the tiers, from the Best Papers panel
    h.append(Line2D([], [], ls="none", marker="o", ms=4.2 * P.S, mfc=P.SURFACE, mec=P.INK, mew=0.8 * P.S))
    l.append("NeurIPS 2014 and 2021 experiments")
    legend_y = axes[0].get_position().y0 - LEGEND_GAP_IN * P.S / fig.get_size_inches()[1]  # the legend's top, in figure coordinates
    fig.legend(h, l, loc="upper center", bbox_to_anchor=(0.5, legend_y), ncol=6, handlelength=1.3, columnspacing=1.0,
               title="Tier the second review gives the paper", title_fontsize=P.LEGEND_PT)


def fig_scaling():
    """The scaling row on its own (not in the paper, which has it as Fig 1d-g)."""
    fig, axes = plt.subplots(1, 4, figsize=(P.CANVAS_W, ROW_H * P.S), gridspec_kw=dict(wspace=0.42))
    scaling_row(fig, axes)
    for i, a in enumerate(axes):
        P.panel_label(a, "abcd"[i])
    P.save(fig, os.path.join(FIG, "fig2_scaling"))


# ---------------------------------------------------------------------------
# Figure 4: why awards lose reproducibility as conferences grow
# ---------------------------------------------------------------------------


def fig_mechanism():
    """Why the Best Papers lose reproducibility as conferences grow, and what holding each tier costs in reviews
    (results/R_needed_tiers_curve.csv). (a) The overlap of two reviews' tiers with infinitely many reviewers,
    when only the chair noise separates them: the ceiling the chairs' call sets, against submissions.
    (b) Reviews per paper that hold each tier's overlap at its 1,000-submission value, against submissions."""
    r = load("R_needed_tiers_curve")  # each rung's overlap fitted across sizes and inverted on a fine grid (summarize_R_needed_tiers.py)
    fig, axes = plt.subplots(1, 2, figsize=(P.CANVAS_W, ROW_H * P.S), gridspec_kw=dict(wspace=0.4))

    ax = axes[0]  # the ceiling: overlap with infinitely many reviewers, per tier
    summ = load("R_needed_tiers_summary")
    for tier, c, label, lift in (("spot", P.BLUE[250], "Spotlight", 0.02), ("oral", P.BLUE[450], "Oral", -0.02), ("best", P.INK, "Best Papers", -0.02)):
        # the award tiers, separate; the Accepted tier (83% to 96%) is not drawn: the chairs' call acts on the awards
        d = r[r.tier == tier].sort_values("N")
        ax.plot(d.N, d.limit_overlap, color=c, lw=1.8 * P.S, zorder=3)
        ax.text(1e5, d.limit_overlap.iloc[-1] + lift, label, color=c, va="bottom" if lift > 0 else "top", ha="right", fontsize=P.LEGEND_PT, zorder=6)
    d = r[r.tier == "best"]
    n_star, target = float(d.N_star.iloc[0]), float(summ[summ.tier == "best"].target.iloc[0])
    if np.isfinite(n_star):
        ax.plot([n_star], [target], ls="none", marker="o", ms=4.5 * P.S, mfc=P.SURFACE, mec=P.INK, mew=1.2 * P.S, zorder=5)
        ax.annotate(f"The Best Papers' ceiling\nmeets their 1K level with\nfour reviews, {100 * target:.1f}\\%, at {n_star / 1e3:.0f}K", xy=(n_star, target),
                    xytext=(6e3, 0.135), ha="left", va="bottom", color=P.INK, fontsize=P.LEGEND_PT, linespacing=1.1, zorder=6,
                    arrowprops=dict(arrowstyle="-", color=P.INK, lw=0.9 * P.S, shrinkA=2 * P.S, shrinkB=3 * P.S, relpos=(0.85, 0.0)))  # between the Oral and Best Papers curves, leader down to the point
    P.n_axis(ax)
    ax.set_ylim(0, 0.4)  # nothing drawn reaches 31%
    ax.set_yticks([0, 0.1, 0.2, 0.3, 0.4])
    P.pct_axis(ax)
    ax.set_ylabel("Overlap of two reviews with\ninfinitely many reviewers")
    ax.set_title("Chair noise caps agreement", loc="left")

    ax = axes[1]  # reviews per paper that hold each tier's overlap at its 1,000-submission value
    ymax = 1e4
    for tier, c, label in (("accept", P.MUTED, "Accepted: always 4"), ("spot", P.BLUE[250], "Spotlight"), ("oral", P.BLUE[450], "Oral"),
                           ("best", P.INK, "Best Papers")):
        d = r[r.tier == tier].sort_values("N")
        fin = d[np.isfinite(d.R_needed)]
        x, y = fin.N.values.astype(float), fin.R_needed.values
        n_star = float(d.N_star.iloc[0])
        if np.isfinite(n_star):  # from N* on no number of reviews holds the tier: the curve goes vertical there and leaves the panel
            x, y = np.append(x, n_star), np.append(y, ymax * 10)
            ax.text(n_star / 1.2, ymax / 1.6, f"{label}: from about {n_star / 1e4:.0f}0K\nsubmissions no number\nof reviews holds them",
                    color=c, va="top", ha="right", fontsize=P.LEGEND_PT, linespacing=1.1, zorder=6)
        elif tier == "accept":  # under the flat line, where no curve runs
            ax.text(1e5, y[-1] / 1.2, label, color=c, va="top", ha="right", fontsize=P.LEGEND_PT, zorder=6)
        else:  # the Spotlight label above its curve's end, the Oral label below its own
            above = tier == "spot"
            ax.text(1e5, y[-1] * (1.2 if above else 1 / 1.2), label, color=c, va="bottom" if above else "top", ha="right",
                    fontsize=P.LEGEND_PT, zorder=6)
        ax.plot(x, y, color=c, lw=1.8 * P.S, zorder=3)
    P.n_axis(ax)
    ax.set_yscale("log")
    ax.set_ylim(1.8, ymax)
    ax.yaxis.set_major_locator(FixedLocator([4, 10, 100, 1000, 10000]))
    ax.yaxis.set_minor_locator(NullLocator())
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _p: f"{v:g}" if v < 1000 else f"{v / 1000:g}K"))
    ax.set_ylabel("Reviews per paper that hold\nthe overlap of 1K submissions")
    ax.set_title("Same overlap, more reviews", loc="left")
    for i, a in enumerate(axes):
        P.panel_label(a, "ab"[i])
    P.save(fig, os.path.join(FIG, "fig4_mechanism"))


# ---------------------------------------------------------------------------
# Figure 5: how sure are we? Every variant that fits the acceptance data
# ---------------------------------------------------------------------------


def fig_robustness():
    """Where a second review ranks the Best Papers at NeurIPS 2014 (small marker) and 2026 (large)
    size under every variant refitted to the central disagreement (results/best_paper_robustness.csv);
    each variant's replay of the NeurIPS 2021 experiment is in Fig 4a,b. The grey span is the Gaussian
    model's pessimistic-to-optimistic range at 2026 size. Rows are grouped by family."""
    r = load("best_paper_robustness")
    r["variant"] = r.variant.replace({"Gaussian": "Main model"})  # the paper's name for the base model on the 1-10 form
    names = list(dict.fromkeys(r.variant))
    groups = [r[r.variant == n].group.iloc[0] for n in names]
    y, pos = [], 0.0  # a gap of 0.6 rows between families
    for k, g in enumerate(groups):
        if k and g != groups[k - 1]:
            pos -= 0.6
        y.append(pos)
        pos -= 1.0
    y = np.array(y) - y[-1]  # bottom row at 0
    rng26 = [venue_rows(lev).query("venue == 'NeurIPS' and year == 2026").iloc[0] for lev in LEV]  # span all three levels
    fig, axes = plt.subplots(1, 3, figsize=(P.CANVAS_W, (ROW_H + 0.7) * P.S), gridspec_kw=dict(wspace=0.34))
    panels = ((axes[0], "p2_best", "Best Papers again", (1e-3, 1), [1e-3, 1e-2, 1e-1, 1], P.INK),
              (axes[1], "p2_accept", "Accepted", (0, 1), [0, 0.5, 1], P.MUTED),
              (axes[2], "p2_reject", "Rejected", (1e-3, 0.5), [1e-3, 1e-2, 1e-1], P.ORANGE[450]))
    SIZES = ((2014, 2.8, 0.16), (2026, 4.2, -0.16))  # year, marker size, row offset: the bigger conference, the bigger dot
    for ax, col, title, xlim, ticks, c in panels:
        logx = xlim[0] > 0
        span = sorted(x[col] for x in rng26)
        ax.axvspan(max(span[0], xlim[0]), span[-1], color=P.GRID, alpha=0.55, lw=0, zorder=0)
        for yi, n in zip(y, names):
            for yr, ms, dy in SIZES:
                v = float(r[(r.variant == n) & (r.year == yr)][col].iloc[0])
                floor = logx and v < xlim[0]
                v = xlim[0] * 0.8 if floor else v  # a floor arrow sits left of the spine
                ax.plot(v, yi + dy, "<" if floor else "o", ms=ms * P.S, color=c, mec=P.SURFACE, mew=0.7 * P.S,
                        ls="none", zorder=3, clip_on=False)
        if logx:
            ax.set_xscale("log")
            ax.set_xticks(ticks)
            ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda v, _p: f"{100 * v:g}\\%"))
        else:
            ax.set_xticks(ticks)
            P.pct_axis(ax, "x")
        ax.set_xlim(*xlim)
        ax.set_title(title, loc="left")
        ax.set_xlabel("Probability")

    for ax in axes:
        ax.set_ylim(-0.6, y.max() + 1.15)
        ax.set_yticks(y)
        ax.set_yticklabels([(n[0].upper() + n[1:]).replace("%", "\\%").replace("1-10", "1--10") for n in names]
                           if ax is axes[0] else [])
        ax.grid(axis="y", visible=False)
    hl = [Line2D([], [], ls="none", marker="o", ms=2.8 * P.S, color=P.INK2, mec=P.SURFACE, label="NeurIPS 2014 size"),
          Line2D([], [], ls="none", marker="o", ms=4.2 * P.S, color=P.INK2, mec=P.SURFACE, label="NeurIPS 2026 size"),
          plt.Rectangle((0, 0), 1, 1, color=P.GRID, label="Main model, range over the three calibration levels, 2026 size")]
    fig.legend(handles=hl, loc="upper center", bbox_to_anchor=(0.5, -0.02), ncol=3, handlelength=1.2)
    for i, a in enumerate(axes):
        P.panel_label(a, "abc"[i])
    P.save(fig, os.path.join(FIG, "fig5_robustness"))

# ---------------------------------------------------------------------------
# Figure 6: does the score scale matter? The same model on every real review form
# ---------------------------------------------------------------------------

FORM_LINES = (  # form label in results/scale_impact.csv, colour, line style, legend label
    ("Integer 1--10, 4 reviews", P.INK, "-", "Integer 1--10 (main)"),
    ("Six-point, 4 reviews", P.BLUE[450], "-", "Six-point"),
    ("1/3/5/6/8/10, 4 reviews", P.BLUE[250], "-", "ICLR 1/3/5/6/8/10"),
    ("Continuous, 4 reviews", P.INK2, (0, (4, 2)), "Continuous"),
)


def fig_scales():
    """The same calibrated model on every real review form (results/scale_impact.csv). (a-c) Where a
    second review ranks the Best Papers at NeurIPS 2014 (small marker) and 2026 (large) size under
    each form, rows in the order of the main form first; grey span: the main form, pessimistic to
    optimistic level, at 2026 size. (d) The chance of Best Papers again along the
    submissions axis for four forms."""
    r = load("scale_impact")
    conf = r[r.part == "conference"]
    names = [f for f, *_ in FORM_LINES[:1]] + [f for f in dict.fromkeys(conf.form) if f != FORM_LINES[0][0]]
    names = [n for n in names if n != "Continuous, 4 reviews"] + ["Continuous, 4 reviews"]  # continuous last
    y = np.arange(len(names))[::-1].astype(float)
    y[-1] -= 0.6  # a gap before the continuous row, which is no real scale
    rng26 = [venue_rows(lev).query("venue == 'NeurIPS' and year == 2026").iloc[0] for lev in LEV]  # span all three levels
    fig, axs = plt.subplots(1, 5, figsize=(P.CANVAS_W, (ROW_H + 0.5) * P.S),
                            gridspec_kw=dict(wspace=0.36, width_ratios=[1, 1, 1, 0.12, 1.15]))
    axs[3].axis("off")  # a spacer, so the y label of (d) clears panel (c)
    axes = [axs[0], axs[1], axs[2], axs[4]]
    panels = ((axes[0], "p2_best", "Best Papers again", (3e-4, 0.2), [1e-3, 1e-2, 1e-1], P.INK),
              (axes[1], "p2_oral", "Oral", (0, 0.25), [0, 0.1, 0.2], P.BLUE[450]),
              (axes[2], "p2_reject", "Rejected", (0, 0.35), [0, 0.15, 0.3], P.ORANGE[450]))
    SIZES = ((2014, 2.8, 0.16), (2026, 4.2, -0.16))
    for ax, col, title, xlim, ticks, c in panels:
        logx = xlim[0] > 0
        span = sorted(x[col] for x in rng26)
        ax.axvspan(max(span[0], xlim[0]), span[-1], color=P.GRID, alpha=0.55, lw=0, zorder=0)
        for yi, n in zip(y, names):
            for yr, ms, dy in SIZES:
                v = float(conf[(conf.form == n) & (conf.year == yr)][col].iloc[0])
                ax.plot(v, yi + dy, "o", ms=ms * P.S, color=c, mec=P.SURFACE, mew=0.7 * P.S, ls="none", zorder=3, clip_on=False)
        if logx:
            ax.set_xscale("log")
            ax.set_xticks(ticks)
            ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda v, _p: f"{100 * v:g}\\%"))
        else:
            ax.set_xticks(ticks)
            P.pct_axis(ax, "x")
        ax.set_xlim(*xlim)
        ax.set_title(title, loc="left")
        ax.set_xlabel("Probability")
    for ax in axes[:3]:
        ax.set_ylim(y.min() - 0.6, y.max() + 0.6)
        ax.set_yticks(y)
        ax.set_yticklabels([n.replace("%", "\\%") for n in names] if ax is axes[0] else [])
        ax.grid(axis="y", visible=False)

    ax = axes[3]
    grid = r[r.part == "grid"]
    for form, c, ls, label in FORM_LINES:
        d = grid[grid.form == form].sort_values("N")
        ax.plot(d.N, d.p2_best, color=c, ls=ls, lw=1.6 * P.S, label=label)
    P.n_axis(ax)
    ax.set_yscale("log")
    ax.set_ylim(5e-4, 0.1)
    ax.yaxis.set_major_locator(FixedLocator([0.001, 0.01, 0.1]))
    ax.yaxis.set_minor_locator(NullLocator())
    P.pct_axis(ax)
    ax.set_ylabel("Probability")
    ax.set_title("Best Papers again", loc="left")
    hl = [Line2D([], [], ls="none", marker="o", ms=2.8 * P.S, color=P.INK2, mec=P.SURFACE, label="NeurIPS 2014 size"),
          Line2D([], [], ls="none", marker="o", ms=4.2 * P.S, color=P.INK2, mec=P.SURFACE, label="NeurIPS 2026 size"),
          plt.Rectangle((0, 0), 1, 1, color=P.GRID, label="Main form, range over the three calibration levels, 2026 size")]
    fig.legend(handles=hl, loc="upper center", bbox_to_anchor=(0.5, -0.02), ncol=3, handlelength=1.2)
    lines, labels = ax.get_legend_handles_labels()  # the four forms of (d), in a second legend row under the first
    fig.legend(handles=lines, labels=["(d) " + labels[0]] + labels[1:], loc="upper center", bbox_to_anchor=(0.5, -0.12), ncol=4, handlelength=1.6)
    for i, a in enumerate(axes):
        P.panel_label(a, "abcd"[i])
    P.save(fig, os.path.join(FIG, "fig6_scales"))


FIGURES = dict(headline=fig_headline, scaling=fig_scaling, validation=fig_validation, mechanism=fig_mechanism,
               robustness=fig_robustness, scales=fig_scales)


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
