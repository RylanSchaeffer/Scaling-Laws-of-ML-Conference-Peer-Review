"""Calibration (handoff §7): reliability estimates, the three levels, and per-variant
recalibration of sigma_eps by bisection.

Writes
  results/calibration_reliability.csv  every rho^2 estimate of §7.1 and §7.2
  results/calibration_levels.csv       the three levels and their analytic sigma_eps
  results/calibration_variants.csv     calibrated sigma_eps per (variant, level)

Usage: uv run python scripts/run_calibration.py [--workers 5]
"""

from __future__ import annotations

import argparse
import os
import time
from concurrent.futures import ProcessPoolExecutor, as_completed

import numpy as np
import pandas as pd

from peerreview import analytic as an
from peerreview.calibrate import calibrate_sigma_eps, reliability_table
from peerreview.levels import CAL_ALPHA, CALIB_CSV, LEVELS, ROOT, target_dis
from peerreview.model import MAIN_FORM, ReviewModel
from peerreview.simulate import stable_seed

CAL_N, CAL_REPS, CAL_TOL = 5000, 2000, 5e-4
CARELESS = ((0.01, "rave"), (0.05, "rave"), (0.05, "random"))


def placement_variants() -> list[ReviewModel]:
    """Alternative placements of coarse scales on the latent axis (§3.2), central level only."""
    out = []
    # Native range: points 1..k with the latent distribution mapped affinely onto [1, k].
    for k, name in ((6, "six"), (5, "five")):
        f = (k - 1) / 9.0
        out.append(ReviewModel(R=4, scale="custom", scale_points=tuple(float(i) for i in range(1, k + 1)),
                               mu_q=1 + 4.0 * f, sigma_q=1.2 * f))
    # Latent mean shifted by half a grid step relative to the points.
    for scale, shift in (("int10", 0.5), ("six", 0.9), ("iclr6", 0.5), ("five", 1.125)):
        out.append(ReviewModel(R=4, scale=scale, mu_q=5.0 + shift))
    return out


def bisection_variants() -> list[tuple[ReviewModel, tuple[str, ...]]]:
    v: list[tuple[ReviewModel, tuple[str, ...]]] = []
    all_levels = tuple(LEVELS)
    # (e) score scales at R = 4, plus a continuous bisection check of the analytic inverse.
    for scale in ("int10", "six", "iclr6", "five", "continuous"):
        v.append((ReviewModel(R=4, scale=scale), all_levels))
    for m in placement_variants():
        v.append((m, ("central",)))
    # (d) quality tails at R = 3, Gaussian and t3 noise.
    for qd in ("beta", "exp", "t3", "lognormal"):
        v.append((ReviewModel(R=3, quality=qd), all_levels))
    for qd in ("gaussian", "beta", "exp", "t3", "lognormal"):
        v.append((ReviewModel(R=3, quality=qd, noise="t3"), all_levels))
    # §3.5 validation variants at R = 4 (Gaussian ones are analytic).
    for qd, nz in (("gaussian", "t3"), ("beta", "gaussian"), ("beta", "t3"), ("exp", "gaussian")):
        v.append((ReviewModel(R=4, quality=qd, noise=nz), all_levels))
    # Heavy-tailed noise on a bounded 1-to-10 scale (NeurIPS 2021 validation).
    for qd in ("gaussian", "beta"):
        v.append((ReviewModel(R=4, quality=qd, noise="t3", scale="int10"), all_levels))
    # A few careless reviewers on the 1-to-10 scale (Best Paper robustness), central level.
    for share, kind in CARELESS:
        v.append((ReviewModel(R=4, scale="int10", careless=share, careless_kind=kind), ("central",)))
    return v


def form_variants() -> list[tuple[ReviewModel, tuple[str, ...]]]:
    """The real review forms (data/review_forms.csv): each distinct (reviews per paper, score scale),
    for the score-scale section (scripts/run_scale_impact.py)."""
    forms = pd.read_csv(os.path.join(ROOT, "data", "review_forms.csv"))
    keys = sorted({(int(r.R), str(r.scale)) for r in forms.itertuples()})
    return [(ReviewModel(R=R, scale=scale), tuple(LEVELS)) for R, scale in keys]


def main_form_variants() -> list[tuple[ReviewModel, tuple[str, ...]]]:
    """Model variants on the main form (MAIN_FORM): the NeurIPS 2021 replay variants (Fig. 2) at every level,
    the robustness variants (Fig. 5) at the central level."""
    v: list[tuple[ReviewModel, tuple[str, ...]]] = []
    for kw in (dict(sigma_u=0.5), dict(noise="t3"), dict(quality="beta"), dict(quality="beta", noise="t3"), dict(quality="exp")):
        v.append((ReviewModel(**MAIN_FORM, **kw), tuple(LEVELS)))
    for kw in (dict(quality="lognormal"), dict(quality="t3"),
               *(dict(careless=share, careless_kind=kind) for share, kind in CARELESS)):
        v.append((ReviewModel(**MAIN_FORM, **kw), ("central",)))
    return v


def _job(m: ReviewModel, level: str) -> dict:
    seed = stable_seed(m.as_dict(), level, "calibration")
    t0 = time.perf_counter()
    res = calibrate_sigma_eps(m, target_dis(level), alpha=CAL_ALPHA, N=CAL_N, reps=CAL_REPS, seed=seed, tol=CAL_TOL)
    d = m.as_dict()
    d.pop("sigma_eps")
    return {**d, "level": level, "rho2_level": LEVELS[level], "target_dis": target_dis(level),
            "method": "bisection", **res, "wall_s": time.perf_counter() - t0}


def analytic_rows() -> list[dict]:
    rows = []
    for R in (1, 2, 3, 4, 5, 6, 8, 10, 15, 20, 50):
        for su in (0.0, 0.5):
            for level, r2 in LEVELS.items():
                m = ReviewModel(R=R, sigma_u=su)
                d = m.as_dict()
                d.pop("sigma_eps")
                rows.append({**d, "level": level, "rho2_level": r2, "target_dis": target_dis(level),
                             "method": "analytic", "sigma_eps": float(an.sigma_eps_for_rho2(r2, R, 1.2, su)),
                             "achieved": target_dis(level), "converged": True, "alpha": CAL_ALPHA})
    return rows


def write_levels_table() -> None:
    lv = []
    for level, r2 in LEVELS.items():
        row = {"level": level, "rho2": r2, "rho": np.sqrt(r2), "cal_alpha": CAL_ALPHA, "target_dis": target_dis(level),
               "target_incons": 2 * CAL_ALPHA * target_dis(level)}
        for R in (3, 4):
            for su in (0.0, 0.5):
                row[f"sigma_eps_R{R}_su{su:g}"] = float(an.sigma_eps_for_rho2(r2, R, 1.2, su))
        lv.append(row)
    pd.DataFrame(lv).to_csv(os.path.join(ROOT, "results", "calibration_levels.csv"), index=False)
    print(pd.DataFrame(lv).round(4).to_string(index=False))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=5)
    ap.add_argument("--forms-only", action="store_true",
                    help="calibrate only the review forms of data/review_forms.csv and the variants on them that the store lacks, and append them")
    ap.add_argument("--level", default="", help="recalibrate every variant and form at this level only, replacing its rows in the store")
    args = ap.parse_args()
    os.makedirs(os.path.join(ROOT, "results"), exist_ok=True)
    if args.level:
        from peerreview.levels import variant_key
        write_levels_table()
        seen, jobs = set(), []
        for m, levels in bisection_variants() + form_variants() + main_form_variants():
            if args.level in levels and variant_key(m) not in seen:
                seen.add(variant_key(m)); jobs.append((m, args.level))
        print(f"{len(jobs)} calibrations at the {args.level} level")
        rows = [r for r in analytic_rows() if r["level"] == args.level]
        t0 = time.perf_counter()
        with ProcessPoolExecutor(max_workers=args.workers) as ex:
            for i, r in enumerate(ex.map(_job, [m for m, _ in jobs], [lev for _, lev in jobs]), 1):
                rows.append(r)
                print(f"[{i}/{len(jobs)} {time.perf_counter() - t0:.0f}s] R={r['R']} {r['scale']} q={r['quality']} n={r['noise']} su={r['sigma_u']}: "
                      f"sigma_eps={r['sigma_eps']:.4f} dis={r['achieved']:.4f} (target {r['target_dis']:.4f}) converged={r['converged']}", flush=True)
        old = pd.read_csv(CALIB_CSV, keep_default_na=False, na_values=[""])
        df = pd.concat([old[old.level != args.level], pd.DataFrame(rows)], ignore_index=True)
        df.to_csv(CALIB_CSV, index=False)
        print(f"wrote {CALIB_CSV}: {len(df)} rows")
        return
    if args.forms_only:
        from peerreview.levels import _store, variant_key
        store = _store()
        have = {(variant_key(ReviewModel(**{k: r[k] for k in ("R", "scale", "quality", "noise", "sigma_u", "mu_q", "careless", "careless_kind")}
                                          | {"scale_points": tuple(float(x) for x in str(r["scale_points"]).split(",") if x)})), r["level"])
                for _, r in store.iterrows()}
        jobs = [(m, lev) for m, levels in form_variants() + main_form_variants() for lev in levels
                if (variant_key(m), lev) not in have]
        print(f"{len(jobs)} form calibrations to run")
        rows = []
        t0 = time.perf_counter()
        with ProcessPoolExecutor(max_workers=args.workers) as ex:
            for i, r in enumerate(ex.map(_job, [m for m, _ in jobs], [lev for _, lev in jobs]), 1):
                rows.append(r)
                print(f"[{i}/{len(jobs)} {time.perf_counter() - t0:.0f}s] R={r['R']} {r['scale']} {r['level']}: "
                      f"sigma_eps={r['sigma_eps']:.4f} dis={r['achieved']:.4f} (target {r['target_dis']:.4f}) converged={r['converged']}", flush=True)
        df = pd.concat([pd.read_csv(CALIB_CSV, keep_default_na=False, na_values=[""]), pd.DataFrame(rows)], ignore_index=True)
        df.to_csv(CALIB_CSV, index=False)
        return

    pd.DataFrame(reliability_table()).to_csv(os.path.join(ROOT, "results", "calibration_reliability.csv"), index=False)
    write_levels_table()

    jobs = [(m, lev) for m, levels in bisection_variants() for lev in levels]
    rows = analytic_rows()
    t0 = time.perf_counter()
    with ProcessPoolExecutor(max_workers=args.workers) as ex:
        futs = [ex.submit(_job, m, lev) for m, lev in jobs]
        for i, f in enumerate(as_completed(futs), 1):
            r = f.result()
            rows.append(r)
            print(f"[{i}/{len(jobs)} {time.perf_counter() - t0:.0f}s] R={r['R']} {r['scale']} {r['quality']}/{r['noise']} "
                  f"mu={r['mu_q']} {r['level']}: sigma_eps={r['sigma_eps']:.4f} dis={r['achieved']:.4f} "
                  f"(target {r['target_dis']:.4f}) converged={r['converged']}", flush=True)
    df = pd.DataFrame(rows)
    df.to_csv(CALIB_CSV, index=False)
    bad = df[~df["converged"].astype(bool)]
    if len(bad):
        print("NOT CONVERGED:\n", bad.to_string())


if __name__ == "__main__":
    main()
