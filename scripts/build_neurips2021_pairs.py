"""Build the NeurIPS 2021 paired-review dataset: both committees' reviews of each duplicated paper.

The NeurIPS 2021 consistency experiment reviewed 10% of submissions twice, by two independent
committees (Beygelzimer, Dauphin, Liang and Wortman Vaughan, arXiv:2306.03262). For every
duplicated paper that was accepted, and for the rejected ones whose authors opted in, both copies
are public on OpenReview under two forum IDs with the same title and abstract. This script pairs
them from a mirror of OpenReview reviews (the AlgorithmicResearchGroup/openreview-papers-with-reviews
dataset on Hugging Face, parquet files in data/raw/openreview_mirror/) and the Paper Copilot
decision list (data/raw/openreview_mirror/papercopilot_nips2021.json).

Outputs:
  data/paired_reviews/neurips2021_pairs.csv       one row per pair: forum IDs, review counts, mean
                                                   final ratings per side, Paper Copilot decision
  data/raw/paired_reviews/neurips2021_reviews.jsonl one row per review, both sides, full text
                                                   (ignored by git; rebuilt by this script)

Usage: uv run --with pyarrow python scripts/build_neurips2021_pairs.py
"""
from __future__ import annotations

import glob
import json
import os
import re

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MIRROR = os.path.join(ROOT, "data", "raw", "openreview_mirror")
OUT_PAIRS = os.path.join(ROOT, "data", "paired_reviews", "neurips2021_pairs.csv")
OUT_REVIEWS = os.path.join(ROOT, "data", "raw", "paired_reviews", "neurips2021_reviews.jsonl")
VENUE = "NeurIPS.cc/2021/Conference"
TEXT_FIELDS = ("summary", "main_review", "limitations_and_societal_impact", "ethical_concerns")


def leading_int(s: str | None) -> float:
    """'6: Marginally above the acceptance threshold' -> 6."""
    if not isinstance(s, str):
        return np.nan
    m = re.match(r"\s*(\d+)", s)
    return float(m.group(1)) if m else np.nan


def norm_title(t: str) -> str:
    return re.sub(r"\s+", " ", t.strip().lower())


def main() -> None:
    files = sorted(glob.glob(os.path.join(MIRROR, "*.parquet")))
    if not files:
        raise SystemExit(f"no parquet files in {MIRROR}; download the mirror first")
    d = pd.concat([pd.read_parquet(f) for f in files], ignore_index=True)
    n = d[d.venue == VENUE].copy()
    n["key"] = n.paper_title.map(norm_title)
    forums = n.groupby("key").paper_id.agg(lambda s: sorted(set(s)))
    pairs = forums[forums.map(len) == 2]
    more = forums[forums.map(len) > 2]
    print(f"{VENUE}: {len(n)} reviews, {n.paper_id.nunique()} forums, {len(pairs)} titles under two forums, "
          f"{len(more)} under more than two (skipped)")

    with open(os.path.join(MIRROR, "papercopilot_nips2021.json")) as f:
        pc = json.load(f)
    decision = {norm_title(p["title"]): p.get("status", "") for p in pc}

    rows, reviews = [], []
    for k, (key, (forum_a, forum_b)) in enumerate(pairs.items(), start=1):
        pair_id = f"n21-{k:03d}"
        sides = {}
        for side, forum in (("a", forum_a), ("b", forum_b)):
            sub = n[n.paper_id == forum]
            ratings, confs = [], []
            for _, r in sub.iterrows():
                raw = json.loads(r.raw_review)
                rating, conf = leading_int(raw.get("rating")), leading_int(raw.get("confidence"))
                ratings.append(rating)
                confs.append(conf)
                reviews.append({"pair_id": pair_id, "side": side, "forum": forum, "review_id": r.review_id,
                                "title": r.paper_title, "rating": rating, "confidence": conf,
                                "time_spent_reviewing": raw.get("time_spent_reviewing"),
                                **{f: raw.get(f) for f in TEXT_FIELDS}})
            sides[side] = dict(forum=forum, n=len(sub), mean_rating=float(np.nanmean(ratings)),
                               min_rating=float(np.nanmin(ratings)), max_rating=float(np.nanmax(ratings)),
                               mean_confidence=float(np.nanmean(confs)))
        rows.append({"pair_id": pair_id, "title": n[n.paper_id == forum_a].paper_title.iloc[0],
                     "forum_a": sides["a"]["forum"], "forum_b": sides["b"]["forum"],
                     "n_reviews_a": sides["a"]["n"], "n_reviews_b": sides["b"]["n"],
                     "mean_rating_a": round(sides["a"]["mean_rating"], 3), "mean_rating_b": round(sides["b"]["mean_rating"], 3),
                     "min_rating_a": sides["a"]["min_rating"], "min_rating_b": sides["b"]["min_rating"],
                     "max_rating_a": sides["a"]["max_rating"], "max_rating_b": sides["b"]["max_rating"],
                     "mean_confidence_a": round(sides["a"]["mean_confidence"], 3),
                     "mean_confidence_b": round(sides["b"]["mean_confidence"], 3),
                     "decision_papercopilot": decision.get(key, "")})
    p = pd.DataFrame(rows)
    os.makedirs(os.path.dirname(OUT_PAIRS), exist_ok=True)
    os.makedirs(os.path.dirname(OUT_REVIEWS), exist_ok=True)
    p.to_csv(OUT_PAIRS, index=False)
    with open(OUT_REVIEWS, "w") as f:
        for r in reviews:
            f.write(json.dumps(r) + "\n")

    gap = (p.mean_rating_a - p.mean_rating_b).abs()
    print(f"wrote {OUT_PAIRS}: {len(p)} pairs, {len(reviews)} reviews; decisions {p.decision_papercopilot.value_counts().to_dict()}")
    print(f"mean final rating, side a vs b: r = {np.corrcoef(p.mean_rating_a, p.mean_rating_b)[0, 1]:.2f}; "
          f"|gap| mean {gap.mean():.2f}, median {gap.median():.2f}, >= 1 point in {(gap >= 1).mean():.0%} of pairs, "
          f">= 2 points in {(gap >= 2).mean():.0%}")


if __name__ == "__main__":
    main()
