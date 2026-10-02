"""Run many simulation configurations in parallel and write one CSV row each (handoff §9).

A task is a plain dict:
  sweep            name of the sweep (also salts the seed, so every configuration
                   gets its own seed)
  kind             "simulate" (all metrics) or "best" (best-paper only, O(N))
  model            ReviewModel keyword arguments
  N, reps          conference size and replicate count (reps None = default budget)
  sel              Selections keyword arguments (kind "simulate")
  best_K           tuple of K (kind "best")
  two_committees   bool (kind "simulate")
  extra            dict of extra columns copied into the row (labels such as level)

Rows already present in the output CSV (same task key) are skipped, so an
interrupted run resumes where it stopped.
"""

from __future__ import annotations

import json
import os
import time
from concurrent.futures import ProcessPoolExecutor, as_completed

import pandas as pd

from .model import ReviewModel
from .simulate import Selections, default_reps, simulate, simulate_best_paper


def task_key(t: dict) -> str:
    keep = {k: t.get(k) for k in ("sweep", "kind", "model", "N", "reps", "sel", "best_K", "two_committees", "extra")}
    return json.dumps(keep, sort_keys=True, default=str)


def _cost(t: dict) -> float:
    m = ReviewModel(**t["model"])
    reps = t.get("reps") or default_reps(t["N"])
    per = 1 if m.gaussian_shortcut else m.R
    return reps * t["N"] * per * (0.2 if t.get("kind") == "best" else 1.0)


def run_task(t: dict) -> dict:
    os.environ.setdefault("OMP_NUM_THREADS", "1")
    m = ReviewModel(**t["model"])
    if t.get("kind", "simulate") == "best":
        row = simulate_best_paper(m, t["N"], t["reps"], best_K=tuple(t.get("best_K", (1, 5, 10, 30))), salt=t["sweep"])
    else:
        sel = Selections(**{k: tuple(v) if isinstance(v, list) else v for k, v in t.get("sel", {}).items()})
        row = simulate(m, t["N"], t.get("reps"), sel=sel, two_committees=t.get("two_committees", True), salt=t["sweep"])
    row = {"sweep": t["sweep"], "kind": t.get("kind", "simulate"), **t.get("extra", {}), **row}
    row["task_key"] = task_key(t)
    return row


def run_tasks(tasks: list[dict], out_csv: str, workers: int = 5, verbose: bool = True) -> pd.DataFrame:
    done = pd.read_csv(out_csv) if os.path.exists(out_csv) else pd.DataFrame()
    have = set(done["task_key"]) if "task_key" in done else set()
    todo = [t for t in tasks if task_key(t) not in have]
    todo.sort(key=_cost, reverse=True)  # longest first for load balance
    if verbose:
        print(f"{out_csv}: {len(tasks)} tasks, {len(tasks) - len(todo)} cached, {len(todo)} to run", flush=True)
    rows = done.to_dict("records") if len(done) else []
    t0 = time.perf_counter()
    if todo:
        with ProcessPoolExecutor(max_workers=workers) as ex:
            futs = {ex.submit(run_task, t): t for t in todo}
            for i, f in enumerate(as_completed(futs), 1):
                rows.append(f.result())
                if i % 5 == 0 or i == len(todo):
                    pd.DataFrame(rows).to_csv(out_csv, index=False)
                    if verbose:
                        print(f"  {i}/{len(todo)} done ({time.perf_counter() - t0:.0f}s)", flush=True)
    df = pd.DataFrame(rows)
    df.to_csv(out_csv, index=False)
    return df
