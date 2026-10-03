#!/usr/bin/env bash
# Regenerate every result CSV. Run from the repository root.
set -euo pipefail
W=${WORKERS:-5}
uv run python scripts/iclr_data.py
uv run python scripts/run_calibration.py --workers "$W"
uv run python scripts/run_sweeps.py g h f b a d e c --workers "$W"
uv run python scripts/run_validation_neurips2021.py --workers "$W"
uv run python scripts/run_validation_iclr.py --workers "$W"
uv run python scripts/run_highlight_process.py --workers "$W"
uv run python scripts/build_venues_used.py
uv run python scripts/run_history.py --workers "$W"
uv run python scripts/verify_analytic.py
