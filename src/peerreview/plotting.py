"""Shared figure style for the report and paper (static, print, light surface).

Colours follow the dataviz reference palette: categorical slots in fixed order,
a single-hue blue ramp for ordered magnitudes, recessive hairline grids, 2px lines,
text in ink tokens (never in a series colour).
"""

from __future__ import annotations

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
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
N_TICKS = [1e3, 1e4, 1e5, 1e6]


def setup() -> None:
    mpl.rcParams.update({
        "font.family": "sans-serif",
        "font.sans-serif": ["Helvetica", "Arial", "DejaVu Sans"],
        "font.size": 8,
        "axes.titlesize": 8.5,
        "axes.titleweight": "normal",
        "axes.labelsize": 8,
        "axes.labelcolor": INK,
        "axes.edgecolor": MUTED,
        "axes.linewidth": 0.6,
        "axes.grid": True,
        "axes.axisbelow": True,
        "grid.color": GRID,
        "grid.linewidth": 0.6,
        "grid.linestyle": "-",
        "xtick.color": INK2,
        "ytick.color": INK2,
        "xtick.labelsize": 7,
        "ytick.labelsize": 7,
        "xtick.major.width": 0.6,
        "ytick.major.width": 0.6,
        "legend.fontsize": 7,
        "legend.frameon": True,  # opaque, borderless: guide lines never run through legend text
        "legend.framealpha": 1.0,
        "legend.facecolor": SURFACE,
        "legend.edgecolor": "none",
        "legend.fancybox": False,
        "lines.linewidth": 1.6,
        "lines.solid_capstyle": "round",
        "lines.solid_joinstyle": "round",
        "lines.markersize": 4.5,
        "axes.spines.top": False,
        "axes.spines.right": False,
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
    """Log x-axis over N = 1e3..1e6 with 1K/10K/100K/1M ticks."""
    ax.set_xscale("log")
    ax.set_xlim(1e3 / 1.15, 1e6 * 1.15)
    ax.xaxis.set_major_locator(FixedLocator(N_TICKS))
    ax.xaxis.set_major_formatter(FuncFormatter(fmt_count))
    ax.xaxis.set_minor_locator(NullLocator())
    ax.set_xlabel(label)


def pct_axis(ax, axis: str = "y") -> None:
    f = FuncFormatter(lambda v, _p: f"{100 * v:.0f}%")
    (ax.yaxis if axis == "y" else ax.xaxis).set_major_formatter(f)


def band(ax, x, lo, mid, hi, color, label=None, marker="o", lw=1.6, alpha=0.14, ls="-", ms=3.5):
    """Central line with a shaded pessimistic-optimistic band."""
    x, lo, mid, hi = map(np.asarray, (x, lo, mid, hi))
    ax.fill_between(x, np.minimum(lo, hi), np.maximum(lo, hi), color=color, alpha=alpha, lw=0)
    ax.plot(x, mid, color=color, lw=lw, ls=ls, marker=marker, ms=ms, mec=SURFACE, mew=0.8, label=label)


def end_label(ax, x, y, text, dx=1.08, dy=0.0, color=INK, **kw):
    ax.annotate(text, (x, y), xytext=(x * dx, y + dy), color=color, fontsize=7.5, va="center",
                ha="left", annotation_clip=False, **kw)


def panel_label(ax, s: str) -> None:
    ax.text(-0.13, 1.06, s, transform=ax.transAxes, fontsize=9, fontweight="bold", va="bottom", ha="left")


def save(fig, path_stem: str) -> None:
    fig.savefig(path_stem + ".pdf", bbox_inches="tight")
    fig.savefig(path_stem + ".png", bbox_inches="tight", dpi=200)
    plt.close(fig)
