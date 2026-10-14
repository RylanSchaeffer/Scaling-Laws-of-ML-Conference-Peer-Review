"""Derive the stage 2 matrix from the saved judgements of one run. Nothing here judges; it only reads
turn_<nnn>.json, backfill_<pair>.json and merges.json under analysis/stage2/run_<k>/ and writes, under
run_<k>/derived/:

  reasons_final.json   every reason with name, definition, creating pair and turn, the ids merged into it
  ticks.csv            rows pairs in turn order, columns reasons (after merge), 1 where any judgement said yes
  justifications.jsonl one line per yes: pair, reason, source (turn | created | backfill), justification
  summary.csv          per reason: pairs applied overall and by kind of discrepancy
  coverage.json        every (pair, reason) with no judgement, and turn files whose fields were missing

Usage: uv run python scripts/build_stage2_matrix.py [run]
"""
from __future__ import annotations

import csv
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
A = os.path.join(ROOT, "data", "paired_reviews", "neurips2021", "analysis")


def load(path):
    with open(path) as f:
        return json.load(f)


def main(run: str) -> None:
    R = f"{A}/stage2/run_{run}"
    D = f"{R}/derived"
    os.makedirs(D, exist_ok=True)
    order = load(f"{A}/order.json")["order"]
    kinds = {r["pair_id"]: r["kind"] for r in csv.DictReader(open(f"{ROOT}/data/paired_reviews/neurips2021/pairs.csv"))}
    reasons = load(f"{R}/reasons.json")
    by_id = {r["id"]: r for r in reasons}

    # merges: absorb -> keep, resolved transitively
    canon = {}
    merge_log = []
    if os.path.exists(f"{R}/merges.json"):
        for m in load(f"{R}/merges.json").get("merges", []):
            canon[m["absorb"]] = m["keep"]
            merge_log.append(m)

    def c(rid):
        seen = set()
        while rid in canon and rid not in seen:
            seen.add(rid)
            rid = canon[rid]
        return rid

    turns = {}
    for f in sorted(os.listdir(R)):
        m = re.match(r"turn_(\d+)\.json$", f)
        if m:
            turns[int(m.group(1))] = load(f"{R}/{f}")
    pairs = [t["pair_id"] for _, t in sorted(turns.items())]
    yes = {p: {} for p in pairs}  # pair -> canonical reason -> (source, justification)
    judged = {p: set() for p in pairs}  # pair -> raw reason ids with any judgement
    problems = []

    def record(p, rid, applies, source, just):
        judged[p].add(rid)
        if applies:
            k = c(rid)
            if k not in yes[p]:
                yes[p][k] = (source, just)

    for n, t in sorted(turns.items()):
        p = t["pair_id"]
        for j in t.get("judgements", []):
            if "id" not in j or "applies" not in j:
                problems.append({"turn": n, "pair_id": p, "problem": f"judgement missing fields: {j}"})
                continue
            record(p, j["id"], bool(j["applies"]), "turn", j.get("justification", ""))
        for a in t.get("added", []):
            rid = a.get("id")
            if rid not in by_id:
                problems.append({"turn": n, "pair_id": p, "problem": f"added reason {rid} not in reasons.json"})
                continue
            record(p, rid, True, "created", a.get("justification") or by_id[rid].get("exemplar", ""))
    for p in pairs:
        f = f"{R}/backfill_{p}.json"
        if not os.path.exists(f):
            continue
        for j in load(f).get("judgements", []):
            if "id" not in j or "applies" not in j:
                problems.append({"pair_id": p, "problem": f"backfill judgement missing fields: {j}"})
                continue
            record(p, j["id"], bool(j["applies"]), "backfill", j.get("justification", ""))

    final_ids = sorted({c(r["id"]) for r in reasons}, key=lambda x: int(re.sub(r"\D", "", x) or 0))
    gaps = [{"pair_id": p, "reason": r["id"]} for p in pairs for r in reasons if r["id"] not in judged[p]]

    final = []
    for rid in final_ids:
        r = dict(by_id[rid])
        r["absorbed"] = sorted(a for a, k in canon.items() if c(a) == rid)
        r["n_pairs"] = sum(rid in yes[p] for p in pairs)
        final.append(r)
    final.sort(key=lambda r: (-r["n_pairs"], r["created_turn"]))
    json.dump({"run": int(run), "pairs": pairs, "merges": merge_log, "reasons": final}, open(f"{D}/reasons_final.json", "w"), indent=1)

    cols = [r["id"] for r in final]
    with open(f"{D}/ticks.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["pair_id", "kind"] + cols)
        for p in pairs:
            w.writerow([p, kinds.get(p, "")] + [int(rid in yes[p]) for rid in cols])
    with open(f"{D}/justifications.jsonl", "w") as f:
        for p in pairs:
            for rid in cols:
                if rid in yes[p]:
                    src, just = yes[p][rid]
                    f.write(json.dumps({"pair_id": p, "kind": kinds.get(p, ""), "reason": rid, "name": by_id[rid]["name"], "source": src, "justification": just}) + "\n")
    kind_order = [k for k in ["oral/poster", "spotlight/poster", "spotlight/reject", "spotlight", "poster/reject", "poster", "reject"] if any(kinds.get(p) == k for p in pairs)]
    with open(f"{D}/summary.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["reason", "name", "definition", "created_by_pair", "created_turn", "absorbed", "n_pairs"] + [f"n_{k}" for k in kind_order] + [f"n_pairs_{k}" for k in kind_order])
        for r in final:
            counts = [sum(r["id"] in yes[p] and kinds.get(p) == k for p in pairs) for k in kind_order]
            totals = [sum(kinds.get(p) == k for p in pairs) for k in kind_order]
            w.writerow([r["id"], r["name"], r["definition"], r["created_by_pair"], r["created_turn"], " ".join(r["absorbed"]), r["n_pairs"]] + counts + totals)
    json.dump({"pairs": len(pairs), "reasons_raw": len(reasons), "reasons_final": len(final), "turns_missing": [n for n in range(1, max(turns) + 1) if n not in turns] if turns else [],
               "backfills_missing": [p for p in pairs if not os.path.exists(f"{R}/backfill_{p}.json")], "gaps": gaps, "problems": problems},
              open(f"{D}/coverage.json", "w"), indent=1)
    print(f"{len(pairs)} pairs, {len(reasons)} reasons ({len(final)} after merge), {sum(len(v) for v in yes.values())} ticks, {len(gaps)} gaps, {len(problems)} problems")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "1")
