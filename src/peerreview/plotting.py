"""Shared figure style for the report and paper.

Rylan's default plot settings: seaborn whitegrid, LaTeX text rendering with Computer Modern,
amsmath, 23 pt for titles, labels and ticks and 18 pt for legends and in-panel annotations. A figure is drawn S times larger than it
prints and LaTeX scales it to the text width, so the type prints at PRINT_PT. Colours follow
the dataviz reference palette: categorical slots in fixed order, a single-hue blue ramp for
ordered magnitudes, text in ink tokens (never in a series colour).
"""

from __future__ import annotations

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from matplotlib.ticker import FixedLocator, FuncFormatter, NullLocator

# Categorical slots, fixed order (never cycled past 8).
CAT = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#4a3aa7", "#e34948"]
# Sequential blue ramp, light -> dark (ordinal use starts at step 250).
BLUE = {250: "#86b6ef", 300: "#6da7ec", 350: "#5598e7", 400: "#3987e5", 450: "#2a78d6",
        500: "#256abf", 550: "#1c5cab", 600: "#184f95", 650: "#104281", 700: "#0d366b"}
ORANGE = {300: "#f3a27f", 450: "#eb6834", 600: "#a8431b"}
INK = "#0b0b0b"
INK2 = "#52514e"
MUTED = "#8a8985"
GRID = "#e4e3df"
SURFACE = "#ffffff"

TEXTWIDTH_IN = 5.5  # \textwidth of the paper (NeurIPS 2026 style)
FONT_PT = 23  # Rylan's default: titles, axis labels and tick labels
LEGEND_PT = 18  # legends and in-panel annotations are smaller than the labels, never larger
PRINT_PT = 8.0  # the size that type prints at once LaTeX scales a figure to the text width
S = FONT_PT / PRINT_PT  # canvas scale: every length in inches or points is drawn S times larger
CANVAS_W = TEXTWIDTH_IN * S  # width of a full-width figure as drawn
N_TICKS = [1e3, 1e4, 1e5]  # no venue has reached 1M submissions; axes stop at 100K


def setup() -> None:
    sns.set_style("whitegrid")
    mpl.rcParams.update({
        # LaTeX rendering, see https://stackoverflow.com/a/23856968
        "text.usetex": True,
        "font.family": "serif",
        "font.serif": "Computer Modern",
        "text.latex.preamble": "\n".join([r"\usepackage{amsmath}"]),
        "font.size": FONT_PT,
        "axes.titlesize": FONT_PT,
        "axes.titleweight": "normal",
        "axes.labelsize": FONT_PT,
        "xtick.labelsize": FONT_PT,
        "ytick.labelsize": FONT_PT,
        "legend.fontsize": LEGEND_PT,
        "axes.labelcolor": INK,
        "xtick.color": INK2,
        "ytick.color": INK2,
        "xtick.major.pad": 2.5 * S,
        "ytick.major.pad": 2.0 * S,
        "axes.labelpad": 2.0 * S,
        "legend.frameon": True,  # opaque, borderless: guide lines never run through legend text
        "legend.framealpha": 1.0,
        "legend.facecolor": SURFACE,
        "legend.edgecolor": "none",
        "legend.fancybox": False,
        "lines.linewidth": 1.6 * S,
        "lines.solid_capstyle": "round",
        "lines.solid_joinstyle": "round",
        "lines.markersize": 4.5 * S,
        "figure.facecolor": SURFACE,
        "savefig.facecolor": SURFACE,
        "savefig.dpi": 300,
        "pdf.fonttype": 42,
        "text.color": INK,
    })


def fmt_count(x: float, _pos=None) -> str:
    if x >= 1e6:
        return f"{x / 1e6:g}M"
    if x >= 1e3:
        return f"{x / 1e3:g}K"
    return f"{x:g}"


def n_axis(ax, label: str = "Submissions $N$") -> None:
    """Log x-axis over N = 1e3..1e5 with 1K/10K/100K ticks."""
    ax.set_xscale("log")
    ax.set_xlim(1e3 / 1.15, 1e5 * 1.15)
    ax.xaxis.set_major_locator(FixedLocator(N_TICKS))
    ax.xaxis.set_major_formatter(FuncFormatter(fmt_count))
    ax.xaxis.set_minor_locator(NullLocator())
    ax.set_xlabel(label)


def pct_axis(ax, axis: str = "y") -> None:
    f = FuncFormatter(lambda v, _p: f"{100 * v:.0f}\\%")
    (ax.yaxis if axis == "y" else ax.xaxis).set_major_formatter(f)


def band(ax, x, lo, mid, hi, color, label=None, marker="o", lw=1.6 * S, alpha=0.14, ls="-", ms=3.5 * S):
    """Central line with a shaded pessimistic-optimistic band."""
    x, lo, mid, hi = map(np.asarray, (x, lo, mid, hi))
    ax.fill_between(x, np.minimum(lo, hi), np.maximum(lo, hi), color=color, alpha=alpha, lw=0)
    ax.plot(x, mid, color=color, lw=lw, ls=ls, marker=marker, ms=ms, mec=SURFACE, mew=0.8 * S, label=label)


def end_label(ax, x, y, text, dx=1.08, dy=0.0, color=INK, **kw):
    ax.annotate(text, (x, y), xytext=(x * dx, y + dy), color=color, va="center",
                ha="left", annotation_clip=False, **kw)


def panel_label(ax, s: str) -> None:
    ax.text(-0.13, 1.06, s, transform=ax.transAxes, fontweight="bold", va="bottom", ha="left")


def save(fig, path_stem: str, width: float = CANVAS_W) -> None:
    """Write PDF and PNG with the tight bounding box exactly `width` wide (CANVAS_W = S times
    the paper's text width), so \\includegraphics[width=\\textwidth] scales by 1/S, the type
    prints at PRINT_PT and no white margin is left on either side. The figure width is
    adjusted iteratively because labels outside the axes have fixed sizes; the height is kept."""
    for _ in range(4):
        fig.canvas.draw()
        bb = fig.get_tightbbox(fig.canvas.get_renderer())  # inches
        w, h = fig.get_size_inches()
        fig.set_size_inches(w * width / bb.width, h)
    fig.savefig(path_stem + ".pdf", bbox_inches="tight", pad_inches=0.01 * S, dpi=300)
    fig.savefig(path_stem + ".png", bbox_inches="tight", pad_inches=0.01 * S, dpi=300)
    plt.close(fig)
