"""The stage 2 binary chart: pairs (rows, grouped by kind of discrepancy) by reasons (columns, most
frequent first), one filled cell where a judgement said the reason applied. A second panel gives each
reason's share of pairs by kind. Reads run_<k>/derived/ from build_stage2_matrix.py.

Usage: uv run python scripts/make_stage2_figure.py [run]
"""
from __future__ import annotations

import csv
import json
import os
import sys

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import ListedColormap
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))
from peerreview import plotting as P  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
A = os.path.join(ROOT, "data", "paired_reviews", "neurips2021", "analysis")
KIND_LABEL = {"oral/poster": "Oral vs Poster", "spotlight/poster": "Spotlight vs Poster", "spotlight/reject": "Spotlight vs Reject",
              "spotlight": "Spotlight, Spotlight", "poster/reject": "Poster vs Reject", "poster": "Poster, Poster", "reject": "Reject, Reject"}
KIND_ORDER = ["oral/poster", "spotlight/poster", "spotlight/reject", "spotlight", "poster/reject", "poster", "reject"]
KIND_COLOR = {"oral/poster": P.CAT[0], "spotlight/poster": P.CAT[1], "spotlight/reject": P.CAT[2], "spotlight": P.CAT[3],
              "poster/reject": P.CAT[4], "poster": P.CAT[5], "reject": P.CAT[6]}


def tex(s: str) -> str:
    for a, b in [("\\", r"\textbackslash{}"), ("&", r"\&"), ("%", r"\%"), ("$", r"\$"), ("#", r"\#"), ("_", r"\_"), ("{", r"\{"), ("}", r"\}"), ("~", r"\textasciitilde{}"), ("^", r"\textasciicircum{}")]:
        s = s.replace(a, b)
    return s


def cap(s: str) -> str:
    return s[:1].upper() + s[1:]


def main(run: str) -> None:
    D = f"{A}/stage2/run_{run}/derived"
    rows = list(csv.DictReader(open(f"{D}/ticks.csv")))
    final = json.load(open(f"{D}/reasons_final.json"))["reasons"]
    cols = [r["id"] for r in final]
    names = {r["id"]: r["name"] for r in final}
    kinds_present = [k for k in KIND_ORDER if any(r["kind"] == k for r in rows)]
    rows.sort(key=lambda r: (KIND_ORDER.index(r["kind"]), r["pair_id"]))  # grouped by kind, pair id within
    M = np.array([[int(r[c]) for c in cols] for r in rows])
    n_pairs, n_reasons = M.shape

    P.setup()
    cell = 0.22 * P.S  # inches per cell as drawn
    fig_w = max(P.CANVAS_W, n_reasons * cell + 4 * P.S)
    fig_h = n_pairs * cell + 5.5 * P.S
    fig, (ax, axb) = plt.subplots(1, 2, figsize=(fig_w + 4 * P.S, fig_h), gridspec_kw={"width_ratios": [n_reasons * cell, 3.4 * P.S], "wspace": 0.04})

    # Panel a: the binary matrix. Rows coloured by kind through the tick colour; filled cells in one ink.
    cmap = ListedColormap([P.SURFACE, P.BLUE[500]])
    ax.imshow(M, cmap=cmap, vmin=0, vmax=1, aspect="equal", interpolation="nearest")
    ax.set_xticks(np.arange(-0.5, n_reasons, 1), minor=True)
    ax.set_yticks(np.arange(-0.5, n_pairs, 1), minor=True)
    ax.grid(which="minor", color=P.GRID, lw=0.5 * P.S)
    ax.grid(which="major", visible=False)
    ax.tick_params(which="minor", length=0)
    ax.set_xticks(range(n_reasons))
    ax.set_xticklabels([tex(cap(names[c])) for c in cols], rotation=90, ha="center", va="top")
    ax.set_yticks(range(n_pairs))
    ax.set_yticklabels([tex(r["pair_id"]) for r in rows])
    ax.tick_params(axis="y", labelsize=P.LEGEND_PT)
    for lbl, r in zip(ax.get_yticklabels(), rows):
        lbl.set_color(KIND_COLOR[r["kind"]])
    # separators and group labels
    start = 0
    for k in kinds_present:
        n = sum(r["kind"] == k for r in rows)
        if start > 0:
            ax.axhline(start - 0.5, color=P.INK, lw=1.2 * P.S)
        ax.text(-0.5 - 0.36 * n_reasons / 10 - 2.2, start + n / 2 - 0.5, tex(KIND_LABEL[k]) + f" ($n={n}$)", ha="right", va="center", color=KIND_COLOR[k], rotation=0)
        start += n
    for s in ax.spines.values():
        s.set_visible(True); s.set_color(P.INK); s.set_linewidth(0.8 * P.S)
    ax.set_xlim(-0.5, n_reasons - 0.5); ax.set_ylim(n_pairs - 0.5, -0.5)
    ax.set_title("Reasons the two committees recommended differently", pad=8 * P.S)

    # Panel b: pairs per reason, stacked by kind, in the matrix's column order rotated to rows.
    axb.set_ylim(n_pairs - 0.5, -0.5)
    axb.axis("off")
    # a per-reason bar chart does not share the y axis with pairs; put reason totals under panel a instead
    totals = M.sum(axis=0)
    for j, t in enumerate(totals):
        ax.text(j, n_pairs - 0.5 + 0.35, str(t), ha="center", va="top", fontsize=P.LEGEND_PT, color=P.INK2)
    handles = [Patch(facecolor=P.BLUE[500], label="Reason applies")] + [Line2D([], [], color=KIND_COLOR[k], lw=4 * P.S, label=tex(KIND_LABEL[k])) for k in kinds_present]
    axb.legend(handles=handles, loc="upper left", bbox_to_anchor=(0.0, 1.0), borderaxespad=0)
    os.makedirs(f"{ROOT}/figures", exist_ok=True)
    P.save(fig, f"{ROOT}/figures/stage2_matrix_run{run}", width=fig_w)

    # Figure 2: share of pairs per reason by kind group (horizontal bars), most frequent first.
    groups = [("Award split", ["oral/poster", "spotlight/poster", "spotlight/reject"]), ("Both spotlight", ["spotlight"]),
              ("Accept split", ["poster/reject"]), ("Agreed", ["poster", "reject"])]
    groups = [(g, ks) for g, ks in groups if any(r["kind"] in ks for r in rows)]
    fig2, ax2 = plt.subplots(figsize=(P.CANVAS_W, (0.42 * n_reasons + 2) * P.S))
    h = 0.8 / len(groups)
    for gi, (g, ks) in enumerate(groups):
        idx = [i for i, r in enumerate(rows) if r["kind"] in ks]
        share = M[idx].mean(axis=0) * 100 if idx else np.zeros(n_reasons)
        ax2.barh(np.arange(n_reasons) + (gi - (len(groups) - 1) / 2) * h, share, height=h * 0.92, color=P.CAT[gi], label=f"{g} ($n={len(idx)}$)")
    ax2.set_yticks(range(n_reasons)); ax2.set_yticklabels([tex(cap(names[c])) for c in cols]); ax2.invert_yaxis()
    ax2.set_xlabel(r"Pairs where the reason applies (\%)"); ax2.set_xlim(0, 100)
    ax2.legend(loc="lower right")
    P.save(fig2, f"{ROOT}/figures/stage2_reasons_by_kind_run{run}")
    print(f"figures/stage2_matrix_run{run}.pdf  figures/stage2_reasons_by_kind_run{run}.pdf  ({n_pairs} pairs x {n_reasons} reasons)")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "1")
