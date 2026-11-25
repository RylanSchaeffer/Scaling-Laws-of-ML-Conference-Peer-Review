# Scaling Laws of Machine Learning Conference Peer Review

How does the quality of a conference's selections change as the number of submissions
grows, with the review process held fixed? This repository holds a calibrated model
of the review pipeline, its analytical solution, simulations from 1,000 to 1,000,000
submissions, two out-of-sample tests, and the paper.

- **Paper:** `paper/main.pdf` (source `paper/main.tex`), in its own repository
  [Scaling-Laws-of-ML-Conference-Peer-Review-Manuscript](https://github.com/RylanSchaeffer/Scaling-Laws-of-ML-Conference-Peer-Review-Manuscript),
  checked out here as the `paper/` submodule (see [The paper submodule](#the-paper-submodule))
- **Report of all findings:** [`REPORT.md`](REPORT.md)
- **Specification:** [`docs/handoff.md`](docs/handoff.md)
- **Terminology (separate tiers, "or Better" sets, second review):** [`docs/terminology.md`](docs/terminology.md)
- **Metric definitions:** [`docs/metrics.md`](docs/metrics.md)
- **Derivations:** [`docs/derivations.md`](docs/derivations.md) (two independent
  derivations in `docs/derivations/`)
- **Empirical claims and their sources:** [`docs/claims.md`](docs/claims.md),
  `data/venues.csv`, `data/spotlights.csv`, `data/experiments.json`

## Tiers: separate, like gold, silver and bronze

Every paper gets exactly one tier: **Best Papers** (gold, the first three papers of the award
ordering), **Oral** (silver, not one of the Best Papers), **Spotlight** (bronze, nothing higher),
**Accepted** (accepted with no award) or **Rejected**. No tier contains another.
A tier together with every tier above it is named in full: **Oral or Better**, **Spotlight or
Better**, **Accepted or Better** (every accepted paper). In code and result files a bare key
(`oral`) is the separate tier and a key ending in `_or_better` is the set
([`docs/terminology.md`](docs/terminology.md), [`src/peerreview/tiers.py`](src/peerreview/tiers.py)).

## Layout

| Path | Contents |
|---|---|
| `src/peerreview/model.py` | generative model: quality, shared and reviewer noise, score scales; the award step (`award_order`: score plus chair noise within the accepted set) |
| `src/peerreview/simulate.py` | vectorised Monte Carlo of whole conferences; every metric |
| `src/peerreview/analytic.py` | closed forms and exact finite-$N$ integrals for the Gaussian model |
| `src/peerreview/calibrate.py`, `levels.py` | calibration to the NeurIPS experiments; the three reliability levels |
| `src/peerreview/validation.py` | replay of the NeurIPS 2021 Orals and Spotlights (Spotlight or Better; 2021 had no Best Papers) |
| `scripts/fit_award_noise.py` | fits the chair noise σ_η on the NeurIPS 2021 pairs' scores (`results/award_noise.json`) |
| `data/paired_reviews/neurips2021/` | the 301 public pairs of the NeurIPS 2021 consistency experiment and the two-stage language-model analysis of the 50 award pairs (`analysis/`) |
| `src/peerreview/iclr.py` | ICLR public-review pipeline (paperlists dumps) |
| `src/peerreview/tiers.py` | the tier definitions (separate tiers, "or Better" sets, `CUTS`, `add_separate`) and tier sizes as conferences grow: power-law fits of NeurIPS's Oral or Better, Spotlight, Accepted or Better and Best Papers counts to $N$ (`fit_tier_sizes`, `fitted_count`, `SERIES_COLUMNS`); `spotlight_counts` (0 Spotlights where a venue-year had no Spotlight tier) |
| `scripts/` | one script per result family; `scripts/run_all.sh` regenerates every simulated and data CSV. The main results are simulated on the main review form (integer 1-10 scores, four reviews per paper; `peerreview.model.MAIN_FORM`): `run_best_paper.py` writes `best_paper.csv` (every venue-year and the submissions grid: where a second review places the Best Papers, the first three of the award ordering, tier overlaps, score positions), `run_best_paper_hirep.py` re-simulates every `p2_*` (all cuts and the separate tiers) with more replays in chunks of 10,000 (120,000 for the central grid above 10K submissions), `run_placement.py` writes `placement.csv` (where a second review places each separate tier and "or Better" set; 20,000 replays at the central level), `run_best_paper_size.py` writes `best_paper_size.csv` (two, three and four Best Papers), `run_R_needed.py` writes `R_needed.csv`, `run_scale_impact.py` writes `scale_impact.csv` (the same model on every real score scale, `data/review_forms.csv`). `make_tier_scaling.py` writes `tier_sizes.csv` (the fitted count series `accept_or_better`, `spot`, `oral_or_better`, `best`, and `oral`, the Oral tier alone) and `tier_scaling.csv`; `make_analytic_curves.py`, `make_R_needed.py` and `make_best_paper.py` write the continuous-score closed forms (`analytic_*.csv`, `best_paper_continuous.csv`), used to explain the power laws |
| `results/` | one CSV row per configuration, with parameters, metrics, replicates, seed and wall time |
| `figures/` | every figure, from `scripts/make_figures.py` |
| `paper/` | the manuscript: a git submodule, the repository Overleaf syncs. `paper/figures/` holds copies of the figure PDFs `main.tex` includes |
| `tests/` | unit tests (`uv run pytest -q`) |

## Reproduce

```bash
uv sync
```

```bash
WORKERS=5 bash scripts/run_all.sh
```

```bash
uv run python scripts/make_tier_scaling.py && uv run python scripts/run_best_paper.py && uv run python scripts/run_best_paper_hirep.py && uv run python scripts/run_placement.py && uv run python scripts/run_R_needed.py && uv run python scripts/run_scale_impact.py && uv run python scripts/make_figures.py
```

```bash
cd paper && tectonic main.tex
```

The paper uses the NeurIPS 2026 style file (`paper/neurips_2026.sty`, `preprint` option).
`uv run python scripts/check_paper.py` checks its layout. The figure files are numbered as in
the paper, in its figure order: `fig1_headline`, `fig2_scaling` (the four-panel scaling figure, from
`results/best_paper.csv` and `results/placement.csv`), `fig0_schematic`, `fig2_validation`,
`fig4_mechanism`, `fig5_robustness`, `fig6_scales`.

The ICLR dumps (about 300 MB) download into `data/raw/`, which git ignores.

## The paper submodule

The manuscript lives in its own repository, checked out here at `paper/`. Overleaf syncs that
repository alone, so it never pulls the data. Clone both with

```bash
git clone --recurse-submodules git@github.com:RylanSchaeffer/Scaling-Laws-of-ML-Conference-Peer-Review.git
```

or, in an existing clone,

```bash
git submodule update --init
```

A fresh checkout leaves `paper/` on a detached commit. Before editing there, put it on its branch:

```bash
git -C paper switch main
```

- **Figures.** The paper includes its own copies in `paper/figures/`. Redrawing a figure that
  `main.tex` includes also refreshes its copy (`peerreview.plotting.save`). After adding a new
  figure to `main.tex`, run `uv run python scripts/sync_paper_figures.py` (`--check` only reports).
- **Committing.** Commit and push inside `paper/` first, then commit the new `paper` pointer in this
  repository: `git add paper`.
- **Overleaf edits.** Overleaf pushes to the manuscript repository. Bring them here with
  `git -C paper pull`, then commit the new `paper` pointer.
