"""For every public copy in the NeurIPS 2021 experiment, pull the submission note's revision history and
download the PDF as the reviewers saw it: the last revision with a PDF dated before the reviews were
released to authors (2021-08-03). The PDF on the forum today is the camera-ready for accepted papers.

Output: data/raw/openreview/neurips2021/submission_revisions[_shard].jsonl  {"forum", "revisions": [...], "reviewed_pdf_ref": id|null}
        data/raw/openreview/neurips2021/pdf_submitted/<forum>.pdf
Usage:  uv run python scripts/fetch_openreview_submitted_pdfs.py [shard/nshards]
"""
from __future__ import annotations

import glob
import json
import os
import sys
import time
import urllib.error
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, "data", "raw", "openreview", "neurips2021")
API = "https://api.openreview.net"
REVIEWS_RELEASED = 1627948800000  # 2021-08-03 00:00 UTC


def get(url: str, token: str, raw: bool = False):
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}", "User-Agent": "peerreview-study/1.0"})
    err = None
    for attempt in range(5):
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                b = r.read()
                return b if raw else json.loads(b.decode())
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None  # this revision's attachment is gone; the caller tries an earlier one
            err = e
            time.sleep(10 * (attempt + 1))
        except Exception as e:  # noqa: BLE001
            err = e
            time.sleep(10 * (attempt + 1))
    raise SystemExit(f"gave up on {url}: {err}")


def main() -> None:
    shard, nshards = (int(x) for x in (sys.argv[1] if len(sys.argv) > 1 else "0/1").split("/"))
    token = open(os.path.expanduser("~/.openreview_token")).read().strip()
    notes = [json.loads(l) for l in open(os.path.join(RAW, "notes.jsonl"))]
    flagged = [n for n in notes if [r for r in n["details"]["replies"] if r["invitation"].endswith("/Decision")][0]["content"].get("consistency_experiment")]
    done = set()
    for f in glob.glob(os.path.join(RAW, "submission_revisions*.jsonl")):
        done |= {json.loads(l)["forum"] for l in open(f)}
    todo = [n for n in flagged[shard::nshards] if n["id"] not in done]
    os.makedirs(os.path.join(RAW, "pdf_submitted"), exist_ok=True)
    out_path = os.path.join(RAW, f"submission_revisions_{shard}.jsonl" if nshards > 1 else "submission_revisions.jsonl")
    print(len(todo), f"copies to do in shard {shard}/{nshards}", flush=True)
    with open(out_path, "a") as out:
        for k, n in enumerate(todo, start=1):
            d = get(f"{API}/references?referent={n['id']}&original=true", token)
            revs = sorted(d.get("references", []), key=lambda r: r["tcdate"])
            with_pdf = [r for r in revs if r["content"].get("pdf") and r["tcdate"] < REVIEWS_RELEASED]
            ref = None
            for cand in reversed(with_pdf):  # the latest pre-review PDF whose attachment is still served
                b = get(f"{API}/references/attachment?id={cand['id']}&name=pdf", token, raw=True)
                if b:
                    open(os.path.join(RAW, "pdf_submitted", f"{n['id']}.pdf"), "wb").write(b)
                    ref = cand["id"]
                    break
            out.write(json.dumps({"forum": n["id"], "reviewed_pdf_ref": ref,
                                  "revisions": [{"id": r["id"], "tcdate": r["tcdate"], "pdf": r["content"].get("pdf"), "fields": sorted(r["content"].keys())} for r in revs]}) + "\n")
            out.flush()
            time.sleep(0.3)
            if k % 25 == 0:
                print(f"{k}/{len(todo)}", flush=True)
    print("done")


if __name__ == "__main__":
    main()
