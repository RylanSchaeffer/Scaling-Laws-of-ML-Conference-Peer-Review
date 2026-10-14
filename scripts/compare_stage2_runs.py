"""Stability of stage 2 across two runs. Reads an alignment written by a judge agent
(analysis/stage2/alignment_run<a>_run<b>.json: for every reason of run b, the run a reason it is the same
mechanism as, or null) and both runs' derived/ticks.csv, and reports: how many of run a's (merged) reasons
reappear in run b, how many of run b's are new, and per-pair agreement of the two matrices on the aligned
reasons (fraction of cells equal, and Jaccard per pair). Writes analysis/stage2/stability_run<a>_run<b>.json.

Usage: uv run python scripts/compare_stage2_runs.py 1 2
"""
from __future__ import annotations

import csv
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
A = os.path.join(ROOT, "data", "paired_reviews", "neurips2021", "analysis", "stage2")


def ticks(run):
    rows = list(csv.DictReader(open(f"{A}/run_{run}/derived/ticks.csv")))
    cols = [c for c in rows[0].keys() if c not in ("pair_id", "kind")]
    return {r["pair_id"]: {c: int(r[c]) for c in cols} for r in rows}, cols


def main(a, b):
    ta, ca = ticks(a)
    tb, cb = ticks(b)
    al = json.load(open(f"{A}/alignment_run{a}_run{b}.json"))
    fa = {r["id"]: r for r in json.load(open(f"{A}/run_{a}/derived/reasons_final.json"))["reasons"]}
    fb = {r["id"]: r for r in json.load(open(f"{A}/run_{b}/derived/reasons_final.json"))["reasons"]}
    # map run b (merged) reason -> run a (merged) reason; alignment may name raw ids, so resolve through merges
    def canon(run, rid):
        for r in json.load(open(f"{A}/run_{run}/derived/reasons_final.json"))["reasons"]:
            if rid == r["id"] or rid in r.get("absorbed", []):
                return r["id"]
        return None
    b_to_a = {}
    for m in al["alignment"]:
        rb, ra = canon(b, m["run_b"]), (canon(a, m["run_a"]) if m.get("run_a") else None)
        if rb and ra:
            b_to_a.setdefault(rb, set()).add(ra)
    a_hit = {ra for s in b_to_a.values() for ra in s}
    pairs = sorted(set(ta) & set(tb))
    cells = agree = 0
    per_pair = []
    for p in pairs:
        va = {ra: ta[p][ra] for ra in ca}
        vb = {ra: 0 for ra in ca}
        for rb, s in b_to_a.items():
            if tb[p].get(rb):
                for ra in s:
                    vb[ra] = 1
        eq = sum(va[r] == vb[r] for r in ca)
        inter = sum(va[r] and vb[r] for r in ca)
        union = sum(va[r] or vb[r] for r in ca)
        per_pair.append({"pair_id": p, "agree": eq / len(ca), "jaccard": inter / union if union else 1.0, "yes_a": sum(va.values()), "yes_b": sum(vb.values())})
        cells += len(ca); agree += eq
    out = {"run_a": a, "run_b": b, "reasons_a": len(ca), "reasons_b": len(cb), "a_reappearing_in_b": sorted(a_hit), "n_a_reappearing": len(a_hit),
           "b_new": sorted(set(cb) - set(b_to_a)), "n_b_new": len(set(cb) - set(b_to_a)),
           "cell_agreement": agree / cells if cells else None, "mean_pair_jaccard": sum(x["jaccard"] for x in per_pair) / len(per_pair) if per_pair else None,
           "per_pair": per_pair,
           "per_reason": [{"run_a": ra, "name": fa[ra]["name"], "n_a": sum(ta[p][ra] for p in pairs),
                           "n_b_aligned": sum(any(tb[p].get(rb) for rb, s in b_to_a.items() if ra in s) for p in pairs)} for ra in ca]}
    json.dump(out, open(f"{A}/stability_run{a}_run{b}.json", "w"), indent=1)
    print(json.dumps({k: v for k, v in out.items() if k not in ("per_pair", "per_reason")}, indent=1))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
