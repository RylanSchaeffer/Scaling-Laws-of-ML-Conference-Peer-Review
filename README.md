# Scaling Laws of Machine Learning Conference Peer Review

How does the quality of a conference's selections change as the number of submissions
grows, with the review process held fixed? This repository holds a calibrated model
of the review pipeline, its analytical solution, simulations from 1,000 to 1,000,000
submissions, two out-of-sample tests, and the paper.

- **Paper:** [`paper/main.pdf`](paper/main.pdf) (source `paper/main.tex`)
- **Report of all findings:** [`REPORT.md`](REPORT.md)
- **Specification:** [`docs/handoff.md`](docs/handoff.md)
- **Metric definitions:** [`docs/metrics.md`](docs/metrics.md)
- **Derivations:** [`docs/derivations.md`](docs/derivations.md) (two independent
  derivations in `docs/derivations/`)
- **Empirical claims and their sources:** [`docs/claims.md`](docs/claims.md),
  `data/venues.csv`, `data/experiments.json`

## Layout

| Path | Contents |
|---|---|
| `src/peerreview/model.py` | generative model: quality, shared and reviewer noise, score scales |
| `src/peerreview/simulate.py` | vectorised Monte Carlo of whole conferences; every metric |
| `src/peerreview/analytic.py` | closed forms and exact finite-$N$ integrals for the Gaussian model |
| `src/peerreview/calibrate.py`, `levels.py` | calibration to the NeurIPS experiments; the three reliability levels |
| `src/peerreview/validation.py` | replay of the NeurIPS 2021 top tier |
| `src/peerreview/iclr.py` | ICLR public-review pipeline (paperlists dumps) |
| `scripts/` | one script per result family; `scripts/run_all.sh` regenerates every simulated and data CSV; `make_analytic_curves.py` and `make_R_needed.py` write the two `analytic_*.csv` files |
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
uv run python scripts/make_analytic_curves.py && uv run python scripts/make_R_needed.py && uv run python scripts/make_figures.py
```

```bash
cd paper && tectonic main.tex
```

The paper uses the NeurIPS 2026 style file (`paper/neurips_2026.sty`, `preprint` option).
`uv run python scripts/check_paper.py` checks its layout.

The ICLR dumps (about 300 MB) download into `data/raw/`, which git ignores.
