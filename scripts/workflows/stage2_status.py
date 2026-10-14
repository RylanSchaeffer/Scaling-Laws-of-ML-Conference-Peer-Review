"""Stage 2 state for run k: turns written, reasons in the set, back-fills written, merges present, and which
turns can start (their stage 1 notes exist). Usage: stage2_status.py [run]"""
import json, os, re, sys
A = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "data", "paired_reviews", "neurips2021", "analysis")
run = sys.argv[1] if len(sys.argv) > 1 else "1"
R = f"{A}/stage2/run_{run}"
order = json.load(open(f"{A}/order.json"))["order"]
notes = {f[:-5] for f in os.listdir(f"{A}/stage1") if f.endswith(".json") and f.startswith("n21-")}
files = os.listdir(R) if os.path.isdir(R) else []
turns = sorted(int(m.group(1)) for f in files for m in [re.match(r"turn_(\d+)\.json$", f)] if m)
blocks = sorted(int(m.group(1)) for f in files for m in [re.match(r"block_(\d+)\.json$", f)] if m)
bf = {f[9:-5] for f in files if f.startswith("backfill_")}
reasons = json.load(open(f"{R}/reasons.json")) if os.path.exists(f"{R}/reasons.json") else []
missing = [n for n in range(1, (turns[-1] if turns else 0) + 1) if n not in turns]
ready = 0
for i, p in enumerate(order):
    if p in notes: ready = i + 1
    else: break
print(json.dumps({"turns_done": len(turns), "last_turn": turns[-1] if turns else 0, "missing_turns": missing, "blocks": blocks,
    "reasons": len(reasons), "backfilled": len(bf), "merges": os.path.exists(f"{R}/merges.json"),
    "stage1_notes": len(notes), "turns_ready_from_notes": ready}))
