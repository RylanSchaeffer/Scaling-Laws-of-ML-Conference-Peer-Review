"""Figure 0: the model of conference peer review, drawn (Methods section).

(a) A conference receives N papers; paper i has a hidden true quality q_i ~ N(5, sigma_q^2).
(b) Each paper receives R = 4 review scores, each the nearest integer from 1 to 10 to s_ij = q_i + u_i + eps_ij: shared noise u_i is the
same for all of its reviewers, reviewer noise eps_ij is new for each; its score is the mean.
(c) Papers are ranked by mean score and the nested tiers are cut by rank. (d) A second review
redraws u and eps on the same papers, so the ranking changes and the first review's Best
Paper lands in a lower tier.

Every panel's data coordinates are inches on the printed page; the canvas is P.S times larger,
so the type prints at P.PRINT_PT. Nothing is read from results/.

Usage: uv run python scripts/make_schematic.py
"""

from __future__ import annotations

import os

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Circle, ConnectionPatch, FancyBboxPatch, Polygon, Rectangle, Wedge

from peerreview import plotting as P
from peerreview.levels import ROOT

FIG = os.path.join(ROOT, "figures")
S = P.S

# Layout, printed inches: four panels in a row, arrows in the gaps, a title row above the axes.
PANELS = (("$N$ papers", 0.95), ("$R=4$ reviews, each scored 1 to 10", 1.3), ("Rank by score; award tiers\nby score $+\\,\\eta$", 1.2), ("A second review", 1.0))
H = 1.9  # axes height
TOP, BOT = 0.22, 0.04  # title row above the axes, margin below
GAP, LEFT, RIGHT = 0.25, 0.14, 0.02  # the left margin holds the panel letter of (a)
IW, IH = 0.09, 0.115  # one paper icon

# Tiers by rank in the column of (c) and (d): label, colour, lowest rank inside the tier.
# Each tier includes the tiers above it; the column is schematic, not to scale.
TIERS = (("Best Paper (rank 1)", P.INK, 1), ("Top 10", P.BLUE[650], 2), ("Oral", P.BLUE[450], 3),
         ("Spotlight", P.BLUE[250], 5), ("Accepted, a fixed\nproportion of $N$", P.MUTED, 7))
RANKS, N_ACC = 11, 7  # ranks drawn; ranks above N_ACC are accepted, the rest rejected
Y1, DR, CUT = 1.70, 0.145, 0.06  # rank 1 height, rank spacing, extra gap at the acceptance cut
LANDS = 5  # the rank the second review gives the first review's Best Paper: spotlight, not oral
ANN = dict(fontsize=P.LEGEND_PT, color=P.INK2)  # in-panel annotations


def paper(ax, x, y, dark=False, z=3):
    """A sheet with a folded top-right corner and three text lines, centred at (x, y).
    dark: the paper the first review names Best Paper (the Best Paper colour, P.INK)."""
    x0, y0, f = x - IW / 2, y - IH / 2, 0.028
    fc, ec, lc, foldc = (P.INK, P.INK, P.SURFACE, P.INK2) if dark else (P.SURFACE, P.INK2, P.MUTED, P.GRID)
    body = [(x0, y0), (x0 + IW, y0), (x0 + IW, y0 + IH - f), (x0 + IW - f, y0 + IH), (x0, y0 + IH)]
    ax.add_patch(Polygon(body, closed=True, fc=fc, ec=ec, lw=0.5 * S, joinstyle="round", zorder=z))
    fold = [(x0 + IW - f, y0 + IH), (x0 + IW - f, y0 + IH - f), (x0 + IW, y0 + IH - f)]
    ax.add_patch(Polygon(fold, closed=True, fc=foldc, ec=ec, lw=0.5 * S, joinstyle="round", zorder=z + 0.1))
    for frac in (0.62, 0.45, 0.28):
        yy = y0 + IH * frac
        ax.plot([x0 + 0.22 * IW, x0 + 0.78 * IW], [yy, yy], color=lc, lw=0.45 * S, solid_capstyle="round", zorder=z + 0.2)


def reviewer(ax, x, y, c=P.INK2):
    """A bust: head over shoulders, centred at (x, y)."""
    ax.add_patch(Circle((x, y + 0.03), 0.021, fc=c, ec="none", zorder=3))
    ax.add_patch(Wedge((x, y - 0.014), 0.044, 0, 180, fc=c, ec="none", zorder=3))


def box(ax, x0, y0, x1, y1, color, z=2):
    """A rounded outline in a tier colour."""
    ax.add_patch(FancyBboxPatch((x0, y0), x1 - x0, y1 - y0, boxstyle="round,pad=0,rounding_size=0.02",
                                fc="none", ec=color, lw=1.0 * S, zorder=z))


# ---------------------------------------------------------------------------
# (a) N papers with hidden quality: a histogram of paper icons under the bell curve
# ---------------------------------------------------------------------------


def panel_papers(ax):
    counts = (1, 2, 4, 6, 4, 2, 1)
    xs = 0.14 + 0.12 * np.arange(len(counts))
    y0, dy = 0.68, 0.13  # bottom of the lowest icon, stack spacing
    for k, (x, n) in enumerate(zip(xs, counts)):
        for m in range(n):
            paper(ax, x, y0 + IH / 2 + dy * m, dark=(k == 5 and m == n - 1))  # high quality, not the highest
    amp, sd = max(counts) * dy + 0.04, 0.21  # the curve clears every stack, tails included
    xx = np.linspace(0.03, 0.93, 200)
    ax.plot(xx, y0 + 0.015 + amp * np.exp(-((xx - xs[3]) ** 2) / (2 * sd * sd)), color=P.INK2, lw=1.0 * S, zorder=1)
    ax.text(xs[3], y0 + amp + 0.07, r"$q_i\sim\mathcal N(5,\sigma_q^2)$", ha="center", va="bottom",
            fontsize=P.LEGEND_PT, color=P.INK)
    ax.annotate("", xy=(0.95, y0 - 0.035), xytext=(0.03, y0 - 0.035),
                arrowprops=dict(arrowstyle="-|>", color=P.INK2, lw=0.8 * S, mutation_scale=6 * S))
    ax.text(xs[3], y0 - 0.09, "True quality $q$\n(hidden)", ha="center", va="top", linespacing=1.15, **ANN)


# ---------------------------------------------------------------------------
# (b) Three reviewers score one paper: each score is quality + shared noise + reviewer noise
# ---------------------------------------------------------------------------

SEG = (dict(fc=P.INK2, ec=P.INK2),  # q_i: solid
       dict(fc=P.SURFACE, ec=P.INK2, hatch="///"),  # u_i: hatched, the same length in every row
       dict(fc=P.SURFACE, ec=P.INK2))  # eps_ij: empty, a different length in every row


def bar(ax, x, y, eps, label, lq=0.36, lu=0.10, bh=0.085):
    """One review score as a bar of three segments; eps is the reviewer-noise length."""
    for style, length in zip(SEG, (lq, lu, eps)):
        ax.add_patch(Rectangle((x, y - bh / 2), length, bh, lw=0.5 * S, zorder=3, **style))
        x += length
    ax.text(x + 0.04, y, label, ha="left", va="center", fontsize=P.LEGEND_PT, color=P.INK)


def panel_reviews(ax):
    rows, eps = (1.62, 1.49, 1.36, 1.23), (0.05, 0.14, 0.08, 0.11)
    xi, yi, xr, xq = 0.16, 1.80, 0.37, 0.47  # paper icon, reviewer glyphs, bars
    paper(ax, xi, yi, dark=True)
    ax.text(xi + IW / 2 + 0.04, yi, "paper $i$", ha="left", va="center", **ANN)
    ax.plot([xi, xi], [yi - IH / 2 - 0.01, rows[-1]], color=P.MUTED, lw=0.6 * S, zorder=1)  # tree to its reviewers
    for y, e, j in zip(rows, eps, (1, 2, 3, 4)):
        ax.plot([xi, xr - 0.05], [y, y], color=P.MUTED, lw=0.6 * S, zorder=1)
        reviewer(ax, xr, y)
        bar(ax, xq, y, e, f"$s_{{i{j}}}$")
    ym = 1.04
    ax.text(xq - 0.035, ym, "Mean score", ha="right", va="center", **ANN)
    bar(ax, xq, ym, float(np.mean(eps)), r"$\bar s_i$")
    ax.text(0.68, 0.83, r"$s_{ij}=q_i+u_i+\varepsilon_{ij}$", ha="center", va="center", fontsize=P.LEGEND_PT, color=P.INK)
    legend = ((0.60, SEG[0], "$q_i$: true quality"),
              (0.48, SEG[1], "$u_i$: shared noise, same"),
              (0.36, None, "for all of its reviewers"),
              (0.24, SEG[2], r"$\varepsilon_{ij}$: reviewer noise"))
    for y, style, text in legend:
        if style is not None:
            ax.add_patch(Rectangle((0.12, y - 0.035), 0.09, 0.07, lw=0.5 * S, zorder=3, **style))
        ax.text(0.26, y, text, ha="left", va="center", **ANN)


# ---------------------------------------------------------------------------
# (c), (d) A column of papers ranked by mean score, the nested tiers as nested boxes
# ---------------------------------------------------------------------------


def rank_y(r: int) -> float:
    return Y1 - (r - 1) * DR - (CUT if r > N_ACC else 0.0)


def column(ax, xc: float, dark_rank: int) -> list[tuple[float, float]]:
    """Icons at every rank, the tier boxes around the top of the column and a box around the
    rejected ranks. Returns (left edge, bottom) of each tier box, then of the rejected box."""
    for r in range(1, RANKS + 1):
        paper(ax, xc, rank_y(r), dark=(r == dark_rank), z=4)
    anchors = []
    for k, (_, c, r) in enumerate(TIERS):
        pad = 0.03 + 0.028 * k
        top = rank_y(1) + IH / 2 + 0.02 + 0.022 * k
        bot = rank_y(r) - IH / 2 - 0.025 if r == N_ACC else rank_y(r) - DR / 2  # in the gap below rank r
        box(ax, xc - IW / 2 - pad, bot, xc + IW / 2 + pad, top, c)
        anchors.append((xc - IW / 2 - pad, bot))
    lo, hi = rank_y(RANKS) - IH / 2 - 0.02, rank_y(N_ACC + 1) + IH / 2 + 0.02
    box(ax, xc - IW / 2 - 0.03, lo, xc + IW / 2 + 0.03, hi, P.ORANGE[450])
    anchors.append((xc - IW / 2 - 0.03, (lo + hi) / 2))
    return anchors


XC, XD = 1.0, 0.23  # column centres in (c) and (d): the two columns face each other across the gap


def panel_rank(ax):
    anchors = column(ax, XC, dark_rank=1)
    labels = [t[0] for t in TIERS] + ["Rejected"]
    x_outer = min(x for x, _ in anchors)  # left edge of the widest box
    colours = [c for _, c, _ in TIERS] + [P.ORANGE[450]]
    for (_, y), text, c in zip(anchors, labels, colours):
        ax.plot([x_outer - 0.075, x_outer - 0.015], [y, y], color=c, lw=1.0 * S, solid_capstyle="butt")  # leader
        ax.text(x_outer - 0.095, y, text, ha="right", va="center", linespacing=1.15, **ANN)


def panel_second(ax):
    column(ax, XD, dark_rank=LANDS)
    x = XD + IW / 2 + 0.03 + 0.028 * (len(TIERS) - 1) + 0.05  # right of the widest box
    ax.text(x, rank_y(1), "new Best Paper", ha="left", va="center", **ANN)
    ax.text(x, 1.45, "same papers,\nnew $u$, $\\varepsilon$ and $\\eta$", ha="left", va="center", linespacing=1.15, **ANN)
    ax.text(x, rank_y(LANDS), "lands in\nSpotlight", ha="left", va="center", linespacing=1.15, **ANN)


# ---------------------------------------------------------------------------
# Assembly
# ---------------------------------------------------------------------------


def stage_arrow(ax_from, ax_to, y=H / 2):
    con = ConnectionPatch((ax_from.get_xlim()[1], y), (0, y), "data", "data", axesA=ax_from, axesB=ax_to,
                          arrowstyle="-|>", mutation_scale=8 * S, color=P.INK2, lw=1.4 * S, shrinkA=3 * S, shrinkB=3 * S)
    con.set_clip_on(False)
    ax_to.add_artist(con)


def best_paper_arrow(ax_c, ax_d):
    """Dashed: the first review's Best Paper, from rank 1 in (c) to its rank in (d)."""
    x_from = XC + IW / 2 + 0.03 + 0.028 * (len(TIERS) - 1) + 0.012
    con = ConnectionPatch((x_from, rank_y(1)), (XD - IW / 2 - 0.012, rank_y(LANDS)), "data", "data",
                          axesA=ax_c, axesB=ax_d, arrowstyle="-|>", mutation_scale=7 * S, color=P.INK,
                          lw=1.0 * S, ls=(0, (3, 2)), zorder=10)
    con.set_clip_on(False)
    ax_d.add_artist(con)


def check_text(fig, axes) -> None:
    """Print every pair of overlapping texts and every text outside the canvas (none expected)."""
    fig.canvas.draw()
    r = fig.canvas.get_renderer()
    items = [(t.get_text(), t.get_window_extent(r)) for ax in axes for t in ax.texts + [ax.title] if t.get_text()]
    fb = fig.bbox
    for s, b in items:
        if not (b.x0 >= fb.x0 and b.x1 <= fb.x1 and b.y0 >= fb.y0 and b.y1 <= fb.y1):
            print("text outside the canvas:", s)
    for i, (s, b) in enumerate(items):
        for s2, b2 in items[i + 1:]:
            if b.overlaps(b2):
                print("texts overlap:", repr(s), "|", repr(s2))


def main() -> None:
    os.makedirs(FIG, exist_ok=True)
    P.setup()
    mpl.rcParams["hatch.linewidth"] = 0.5 * S
    W = LEFT + sum(w for _, w in PANELS) + GAP * (len(PANELS) - 1) + RIGHT
    HT = BOT + H + TOP
    fig = plt.figure(figsize=(W * S, HT * S))
    axes, x = [], LEFT
    for title, w in PANELS:
        ax = fig.add_axes([x / W, BOT / HT, w / W, H / HT])
        ax.set_xlim(0, w)
        ax.set_ylim(0, H)
        ax.axis("off")
        ax.set_title(title, loc="left")
        axes.append(ax)
        x += w + GAP
    panel_papers(axes[0])
    panel_reviews(axes[1])
    panel_rank(axes[2])
    panel_second(axes[3])
    stage_arrow(axes[0], axes[1])
    stage_arrow(axes[1], axes[2])
    best_paper_arrow(axes[2], axes[3])
    for i, ax in enumerate(axes):
        P.panel_label(ax, "abcd"[i])
    check_text(fig, axes)
    P.save(fig, os.path.join(FIG, "fig0_schematic"))
    print("wrote fig0_schematic")


if __name__ == "__main__":
    main()
