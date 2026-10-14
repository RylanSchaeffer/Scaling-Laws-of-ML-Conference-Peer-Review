# Scaling Laws of Machine Learning Conference Peer Review

How does the quality of a conference's selections change as the number of submissions
grows, with the review process held fixed? This repository holds a calibrated model
of the review pipeline, its analytical solution, simulations from 1,000 to 1,000,000
submissions, two out-of-sample tests, and the paper.

- **Paper:** [`paper/main.pdf`](paper/main.pdf) (source `paper/main.tex`)
- **Report of all findings:** [`REPORT.md`](REPORT.md)
- **Specification:** [`docs/handoff.md`](docs/handoff.md)
- **Terminology (tiers, awards, second review):** [`docs/terminology.md`](docs/terminology.md)
- **Metric definitions:** [`docs/metrics.md`](docs/metrics.md)
- **Derivations:** [`docs/derivations.md`](docs/derivations.md) (two independent
  derivations in `docs/derivations/`)
- **Empirical claims and their sources:** [`docs/claims.md`](docs/claims.md),
  `data/venues.csv`, `data/spotlights.csv`, `data/experiments.json`

## Layout

| Path | Contents |
|---|---|
| `src/peerreview/model.py` | generative model: quality, shared and reviewer noise, score scales; the award step (`award_order`: score plus chair noise within the accepted set) |
| `src/peerreview/simulate.py` | vectorised Monte Carlo of whole conferences; every metric |
| `src/peerreview/analytic.py` | closed forms and exact finite-$N$ integrals for the Gaussian model |
| `src/peerreview/calibrate.py`, `levels.py` | calibration to the NeurIPS experiments; the three reliability levels |
| `src/peerreview/validation.py` | replay of the NeurIPS 2021 top tier |
| `scripts/fit_award_noise.py` | fits the chair noise σ_η on the NeurIPS 2021 pairs' scores (`results/award_noise.json`) |
| `data/paired_reviews/neurips2021/` | the 301 public pairs of the NeurIPS 2021 consistency experiment and the two-stage language-model analysis of the 50 award pairs (`analysis/`) |
| `src/peerreview/iclr.py` | ICLR public-review pipeline (paperlists dumps) |
| `src/peerreview/tiers.py` | tier sizes as conferences grow: power-law fits of NeurIPS oral and spotlight counts to $N$ |
| `scripts/` | one script per result family; `scripts/run_all.sh` regenerates every simulated and data CSV. The main results are simulated on the main review form (integer 1-10 scores, four reviews per paper; `peerreview.model.MAIN_FORM`): `run_best_paper.py` writes `best_paper.csv` (every venue-year and the submissions grid: where a second review places the Best Paper, tier overlaps, score positions), `run_best_paper_hirep.py` adds replays for its two smallest tiers, `run_R_needed.py` writes `R_needed.csv`, `run_scale_impact.py` writes `scale_impact.csv` (the same model on every real score scale, `data/review_forms.csv`). `make_tier_scaling.py` writes `tier_sizes.csv` (the oral and spotlight fits) and `tier_scaling.csv`; `make_analytic_curves.py`, `make_R_needed.py` and `make_best_paper.py` write the continuous-score closed forms (`analytic_*.csv`, `best_paper_continuous.csv`), used to explain the power laws |
| `results/` | one CSV row per configuration, with parameters, metrics, replicates, seed and wall time |
| `figures/` | every figure, from `scripts/make_figures.py` |
| `tests/` | unit tests (`uv run pytest -q`) |

## Reproduce

```bash
uv sync
```

```bash
WORKERS=5 bash scripts/run_all.sh
```

```bash
uv run python scripts/make_tier_scaling.py && uv run python scripts/run_best_paper.py && uv run python scripts/run_best_paper_hirep.py && uv run python scripts/run_R_needed.py && uv run python scripts/run_scale_impact.py && uv run python scripts/make_figures.py
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
