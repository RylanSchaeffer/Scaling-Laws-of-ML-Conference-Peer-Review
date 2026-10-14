"""Pull the revision history of every official review in the NeurIPS 2021 experiment pairs, so each
review has its initial (pre-rebuttal) and final rating and text. Also downloads each copy's PDF.

Input:  data/raw/openreview/neurips2021/notes.jsonl (scripts/fetch_openreview_neurips2021.py)
Output: data/raw/openreview/neurips2021/references.jsonl  one line per review: {"review_id", "forum", "references": [...]}
        data/raw/openreview/neurips2021/pdf/<forum>.pdf
Usage:  uv run python scripts/fetch_openreview_revisions.py
"""
from __future__ import annotations

import json
import os
import time
import urllib.parse
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, "data", "raw", "openreview", "neurips2021")
API = "https://api.openreview.net"


def get(url: str, token: str, raw: bool = False):
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}", "User-Agent": "peerreview-study/1.0"})
    for attempt in range(5):
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                b = r.read()
                return b if raw else json.loads(b.decode())
        except Exception as e:  # noqa: BLE001
            time.sleep(10 * (attempt + 1))
            err = e
    raise SystemExit(f"gave up on {url}: {err}")


def main() -> None:
    token = open(os.path.expanduser("~/.openreview_token")).read().strip()
    notes = [json.loads(l) for l in open(os.path.join(RAW, "notes.jsonl"))]
    flagged = [n for n in notes if [r for r in n["details"]["replies"] if r["invitation"].endswith("/Decision")][0]["content"].get("consistency_experiment")]
    print(len(flagged), "experiment copies")
    out_path = os.path.join(RAW, "references.jsonl")
    done = set()
    if os.path.exists(out_path):
        done = {json.loads(l)["review_id"] for l in open(out_path)}
    os.makedirs(os.path.join(RAW, "pdf"), exist_ok=True)
    with open(out_path, "a") as out:
        for k, n in enumerate(flagged, start=1):
            pdf = os.path.join(RAW, "pdf", f"{n['id']}.pdf")
            if not os.path.exists(pdf):
                b = get(f"{API}/pdf?id={n['id']}", token, raw=True)
                open(pdf, "wb").write(b)
                time.sleep(0.3)
            for r in n["details"]["replies"]:
                if not r["invitation"].endswith("/Official_Review") or r["id"] in done:
                    continue
                d = get(f"{API}/references?{urllib.parse.urlencode(dict(referent=r['id'], original='true'))}", token)
                out.write(json.dumps({"review_id": r["id"], "forum": n["id"], "references": d.get("references", [])}) + "\n")
                out.flush()
                time.sleep(0.3)
            if k % 25 == 0:
                print(f"{k}/{len(flagged)} copies", flush=True)
    print("done")


if __name__ == "__main__":
    main()
