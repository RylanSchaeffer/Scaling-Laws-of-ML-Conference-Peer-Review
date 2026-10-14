"""The NeurIPS 2021 consistency experiment's public pairs, from OpenReview's own record.

Source: data/raw/openreview/neurips2021/notes.jsonl, the raw API response of
scripts/fetch_openreview_neurips2021.py (every public NeurIPS 2021 submission with every reply).
Every paper in the experiment carries, in its decision note, a `consistency_experiment` field that
states that committee's own decision, the other committee's recommendation and the link to the other
copy. The pairing below uses that field; the title match (same title under two forums) is checked
against it.

Outputs
  data/paired_reviews/neurips2021_pairs.csv        one row per pair (index only: ids, decisions, counts, mean ratings)
  data/paired_reviews/neurips2021_reconciliation.md the pair counts against the report's Table 1
  data/raw/paired_reviews/neurips2021_sides.jsonl  one row per copy: meta-review, author responses, discussion (ignored by git)
  data/raw/paired_reviews/neurips2021_reviews.jsonl one row per review, every field (ignored by git)

Usage: uv run python scripts/build_neurips2021_pairs.py
"""
from __future__ import annotations

import collections
import json
import os
import re

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, "data", "raw", "openreview", "neurips2021", "notes.jsonl")
OUT_DIR = os.path.join(ROOT, "data", "paired_reviews")
RAW_OUT = os.path.join(ROOT, "data", "raw", "paired_reviews")
TIER = {"Accept (Oral)": "oral", "Accept (Spotlight)": "spotlight", "Accept (Poster)": "poster", "Reject": "reject"}
RX_OWN = re.compile(r"(?:This copy.s committee reached the following decision|Both committees reached the same decision): \*\*(.+?)\*\*")
RX_OTHER = re.compile(r"The other committee assigned to the paper recommended \*\*(.+?)\*\*")
RX_URL = re.compile(r"forum\?id=([\w\-]+)")


def leading_int(s) -> float:
    m = re.match(r"\s*(\d+)", s) if isinstance(s, str) else None
    return float(m.group(1)) if m else np.nan


def replies(n, kind):
    return [r for r in n["details"]["replies"] if r["invitation"].endswith("/" + kind)]


def side_record(n, pair_id, side):
    d = replies(n, "Decision")[0]["content"]
    comments = [{"id": c["id"], "replyto": c.get("replyto"), "signature": c["signatures"][0].split("/")[-1],
                 "title": c["content"].get("title"), "comment": c["content"].get("comment"), "tcdate": c["tcdate"]}
                for c in replies(n, "Official_Comment")]
    return {"pair_id": pair_id, "side": side, "forum": n["id"], "number": n["number"], "title": n["content"]["title"],
            "own_decision": RX_OWN.search(d["consistency_experiment"]).group(1),
            "other_recommendation": RX_OTHER.search(d["consistency_experiment"]).group(1),
            "final_decision": d["decision"], "meta_review": d.get("comment"), "comments": comments}


def main() -> None:
    notes = [json.loads(l) for l in open(RAW)]
    byid = {n["id"]: n for n in notes}
    flagged = [n for n in notes if replies(n, "Decision")[0]["content"].get("consistency_experiment")]
    partner = {n["id"]: RX_URL.search(replies(n, "Decision")[0]["content"]["consistency_experiment"]).group(1) for n in flagged}

    # title match, as a check on the official pairing
    norm = lambda t: re.sub(r"\s+", " ", t.strip().lower())
    by_title = collections.defaultdict(list)
    for n in notes:
        by_title[norm(n["content"]["title"])].append(n["id"])
    title_pairs = {frozenset(v) for v in by_title.values() if len(v) == 2}
    official_pairs = {frozenset((a, b)) for a, b in partner.items() if b in byid}
    assert title_pairs == official_pairs, (len(title_pairs), len(official_pairs))

    rows, sides, reviews = [], [], []
    keys = sorted({frozenset((a, b)) for a, b in partner.items()}, key=lambda k: min(byid[x]["number"] for x in k if x in byid))
    for k, key in enumerate(keys, start=1):
        pair_id = f"n21-{k:03d}"
        ids = sorted((x for x in key if x in byid), key=lambda x: byid[x]["number"])
        private = [x for x in key if x not in byid]
        rec = {"pair_id": pair_id, "title": byid[ids[0]]["content"]["title"], "both_public": not private}
        for side, fid in zip("ab", ids + private):
            if fid not in byid:  # the other copy is not public: its decision is in this copy's note
                rec.update({f"forum_{side}": fid, f"own_decision_{side}": sides[-1]["other_recommendation"], f"n_reviews_{side}": np.nan})
                continue
            n = byid[fid]
            s = side_record(n, pair_id, side)
            sides.append(s)
            ratings, confs = [], []
            for r in replies(n, "Official_Review"):
                c = r["content"]
                rating, conf = leading_int(c.get("rating")), leading_int(c.get("confidence"))
                ratings.append(rating)
                confs.append(conf)
                reviews.append({"pair_id": pair_id, "side": side, "forum": fid, "review_id": r["id"],
                                "reviewer": r["signatures"][0].split("/")[-1], "rating": rating, "confidence": conf,
                                "tcdate": r["tcdate"], "tmdate": r["tmdate"],
                                **{f: c.get(f) for f in ("rating", "confidence", "summary", "main_review",
                                                          "limitations_and_societal_impact", "ethical_concerns",
                                                          "needs_ethics_review", "time_spent_reviewing")}})
            rec.update({f"forum_{side}": fid, f"number_{side}": n["number"], f"own_decision_{side}": s["own_decision"],
                        f"n_reviews_{side}": len(ratings), f"mean_rating_{side}": round(float(np.mean(ratings)), 3),
                        f"min_rating_{side}": min(ratings), f"max_rating_{side}": max(ratings),
                        f"mean_confidence_{side}": round(float(np.mean(confs)), 3)})
        rec["final_decision"] = replies(byid[ids[0]], "Decision")[0]["content"]["decision"]
        rows.append(rec)

    p = pd.DataFrame(rows)
    os.makedirs(OUT_DIR, exist_ok=True)
    os.makedirs(RAW_OUT, exist_ok=True)
    p.to_csv(os.path.join(OUT_DIR, "neurips2021_pairs.csv"), index=False)
    for name, data in (("neurips2021_sides.jsonl", sides), ("neurips2021_reviews.jsonl", reviews)):
        with open(os.path.join(RAW_OUT, name), "w") as f:
            for r in data:
                f.write(json.dumps(r) + "\n")

    # reconciliation with the report's Table 1 (unordered, because the public record does not say which copy was the original)
    e = json.load(open(os.path.join(ROOT, "data", "experiments.json")))["neurips2021"]["table1"]["value"]
    lab = e["row_labels_original"][:4]
    rep = np.array(e["counts"])[:4, :4]
    report = collections.Counter()
    for i, a in enumerate(lab):
        for j, b in enumerate(lab):
            report[frozenset((a, b)) if a != b else frozenset((a,))] += rep[i, j]
    ours = collections.Counter()
    for r in rows:
        a, b = TIER[r["own_decision_a"]], TIER[r["own_decision_b"]]
        ours[frozenset((a, b)) if a != b else frozenset((a,))] += 1
    lines = ["# NeurIPS 2021 pairs against the report's Table 1", "",
             "Unordered pairs of the two committees' own decisions. Report: arXiv:2306.03262, Table 1 (recommendations after calibration), 764 decided papers.",
             "Public: pairs with at least one copy on OpenReview, built by `scripts/build_neurips2021_pairs.py`.", "",
             "| Pair of decisions | Report | Public | Difference |", "|---|---|---|---|"]
    order = ["oral", "spotlight", "poster", "reject"]
    cells = [frozenset((a,)) if a == b else frozenset((a, b)) for i, a in enumerate(order) for b in order[i:]]
    for c in cells:
        name = " / ".join(sorted(c, key=order.index)) if len(c) == 2 else f"{next(iter(c))} / {next(iter(c))}"
        lines.append(f"| {name} | {report[c]} | {ours[c]} | {ours[c] - report[c]} |")
    acc = {"oral", "spotlight", "poster"}
    def split(cnt):
        return sum(v for k, v in cnt.items() if len(k) == 2 and len(k & acc) == 1)
    lines += ["", f"Accepted by both: report {sum(v for k, v in report.items() if k <= acc)}, public {sum(v for k, v in ours.items() if k <= acc)}.",
              f"Split decisions: report {split(report)}, public {split(ours)}. The report says a paper with one accept recommendation was accepted "
              "unless the other committee found a fatal flaw; the split pairs missing from the public record are those rejections, whose reviews are private.",
              f"Rejected by both: report {report[frozenset(('reject',))]}, public {ours[frozenset(('reject',))]} (authors who opted in; {sum(1 for r in rows if not r['both_public'])} of them with only one copy public).",
              "", f"Pairs: {len(rows)}; both copies public: {sum(r['both_public'] for r in rows)}; reviews: {len(reviews)}; title match equals the official pairing: yes."]
    with open(os.path.join(OUT_DIR, "neurips2021_reconciliation.md"), "w") as f:
        f.write("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
