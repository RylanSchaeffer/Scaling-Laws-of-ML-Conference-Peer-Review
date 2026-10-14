"""Pull every public NeurIPS 2021 submission from OpenReview's own API, with every reply in its forum
(official reviews, meta-reviews, decisions, author responses and discussion), and keep the raw API
responses unmodified as the source of truth.

Output: data/raw/openreview/neurips2021/notes.jsonl (one submission per line, the API's note object
with details.replies), plus pull.json with the date, the API count and the number of notes saved.
Ignored by git (data/raw/). The token comes from ~/.openreview_token (OpenReview login token).

Usage: uv run python scripts/fetch_openreview_neurips2021.py
"""
from __future__ import annotations

import datetime as dt
import json
import os
import sys
import time
import urllib.parse
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "data", "raw", "openreview", "neurips2021")
API = "https://api.openreview.net"
INVITATION = "NeurIPS.cc/2021/Conference/-/Blind_Submission"
PAGE = 500


def get(path: str, token: str, **params) -> dict:
    url = f"{API}{path}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}", "User-Agent": "peerreview-study/1.0"})
    for attempt in range(5):
        try:
            with urllib.request.urlopen(req, timeout=180) as r:
                return json.loads(r.read().decode())
        except Exception as e:  # noqa: BLE001
            wait = 10 * (attempt + 1)
            print(f"  {e}; retry in {wait}s", flush=True)
            time.sleep(wait)
    raise SystemExit(f"gave up on {url}")


def main() -> None:
    with open(os.path.expanduser("~/.openreview_token")) as f:
        token = f.read().strip()
    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(OUT, "notes.jsonl")
    total, saved, offset = None, 0, 0
    with open(path, "w") as out:
        while True:
            d = get("/notes", token, invitation=INVITATION, details="replies,original", limit=PAGE, offset=offset)
            total = d.get("count", total)
            notes = d.get("notes", [])
            for n in notes:
                out.write(json.dumps(n) + "\n")
            saved += len(notes)
            print(f"{saved}/{total} submissions", flush=True)
            if not notes or saved >= (total or 0):
                break
            offset += PAGE
            time.sleep(1)
    meta = {"pulled": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"), "api": API, "invitation": INVITATION,
            "api_count": total, "saved": saved}
    with open(os.path.join(OUT, "pull.json"), "w") as f:
        json.dump(meta, f, indent=1)
    print(json.dumps(meta))
    if saved != total:
        sys.exit(f"saved {saved} of {total}")


if __name__ == "__main__":
    main()
