"""Print the next batch of pairs for stage 1: the first N pairs in analysis/order.json that have no
stage 1 notes yet and are not listed as in flight. Usage: next_batch.py N [inflight ids...]"""
import json, os, sys
A = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "data", "paired_reviews", "neurips2021", "analysis")
n = int(sys.argv[1]); inflight = set(sys.argv[2:])
order = json.load(open(f"{A}/order.json"))["order"]
done = {f[:-5] for f in os.listdir(f"{A}/stage1") if f.endswith(".json") and f.startswith("n21-")}
todo = [p for p in order if p not in done and p not in inflight]
print(json.dumps(todo[:n])); print(f"done {len(done)}  in flight {len(inflight)}  remaining {len(todo)}", file=sys.stderr)
