#!/usr/bin/env bash
# Regenerate every simulated and data CSV; the analytic CSVs come from the make_*.py chain in README.md. Run from the repository root.
set -euo pipefail
W=${WORKERS:-5}
uv run python scripts/iclr_data.py
uv run python scripts/run_calibration.py --workers "$W"
uv run python scripts/run_sweeps.py g h f b a d e c --workers "$W"
uv run python scripts/fit_award_noise.py
uv run python scripts/run_validation_neurips2021.py --workers "$W"
uv run python scripts/run_validation_iclr.py --workers "$W"
uv run python scripts/run_best_paper_robustness.py --workers "$W"
uv run python scripts/make_tier_scaling.py
uv run python scripts/run_best_paper.py --workers "$W"
uv run python scripts/run_best_paper_hirep.py --workers "$W"
uv run python scripts/run_best_paper.py --cited --reps 50000 --workers "$W"
uv run python scripts/run_placement.py --workers "$W"
uv run python scripts/run_R_needed.py --workers "$W"
uv run python scripts/run_R_needed_tiers.py --workers "$W"
uv run python scripts/run_R_needed_tiers_large.py --workers "$W"
uv run python scripts/run_scale_impact.py --workers "$W"
uv run python scripts/run_scale_impact.py --grid-only --grid-reps 20000 --workers "$W"
uv run python scripts/build_venues_used.py
uv run python scripts/run_history.py --workers "$W"
uv run python scripts/verify_analytic.py
