"""The NeurIPS 2021 consistency experiment's public pairs, from OpenReview's own record.

Inputs (raw API responses, never edited; scripts/fetch_openreview_neurips2021.py and fetch_openreview_revisions.py):
  data/raw/openreview/neurips2021/notes.jsonl       every public NeurIPS 2021 submission with every reply
  data/raw/openreview/neurips2021/references*.jsonl  the /references answer per review (one version each: the API exposes no edit history)
  data/raw/openreview/neurips2021/pdf/<forum>.pdf   each copy's PDF

Every paper in the experiment carries, in its decision note, a `consistency_experiment` field that states
that committee's own decision, the other committee's recommendation and the link to the other copy. The
pairing uses that field; the title match (same title under two forums) is asserted equal to it.

Outputs, under data/paired_reviews/neurips2021/:
  README.md, pairs.csv, copies.csv, reviews.csv      index tables (in git)
  reconciliation.md                                  pair counts against the report's Table 1 (in git)
  pairs/<pair_id>/paper.json, pair.md, a/, b/        the full record per pair (not in git; rebuilt by this script)
     a|b/decision.json, reviews.jsonl, discussion.jsonl, ethics.jsonl, paper.pdf

Usage: uv run python scripts/build_neurips2021_pairs.py
"""
from __future__ import annotations

import collections
import datetime as dt
import json
import os
import re
import shutil

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, "data", "raw", "openreview", "neurips2021")
OUT = os.path.join(ROOT, "data", "paired_reviews", "neurips2021")
TIER = {"Accept (Oral)": "oral", "Accept (Spotlight)": "spotlight", "Accept (Poster)": "poster", "Reject": "reject"}
RANK = {"oral": 0, "spotlight": 1, "poster": 2, "reject": 3}
RX_OWN = re.compile(r"(?:This copy.s committee reached the following decision|Both committees reached the same decision): \*\*(.+?)\*\*")
RX_OTHER = re.compile(r"The other committee assigned to the paper recommended \*\*(.+?)\*\*")
RX_URL = re.compile(r"forum\?id=([\w\-]+)")
REVIEW_FIELDS = ("summary", "main_review", "limitations_and_societal_impact", "ethical_concerns", "needs_ethics_review",
                 "ethics_review_area", "time_spent_reviewing")


def leading_int(s) -> float:
    m = re.match(r"\s*(\d+)", s) if isinstance(s, str) else None
    return float(m.group(1)) if m else np.nan


def ts(ms) -> str:
    return dt.datetime.fromtimestamp(ms / 1000, dt.timezone.utc).strftime("%Y-%m-%d")


def replies(n, kind):
    return [r for r in n["details"]["replies"] if r["invitation"].endswith("/" + kind)]


def role(sig: str) -> str:
    return sig.split("/")[-1]


def kind_of(a: str, b: str) -> str:
    """The pair's kind of discrepancy from the two committees' own decisions (tier names, unordered)."""
    x, y = sorted((a, b), key=RANK.get)
    return x if x == y else f"{x}/{y}"


def main() -> None:
    notes = [json.loads(l) for l in open(os.path.join(RAW, "notes.jsonl"))]
    byid = {n["id"]: n for n in notes}
    import glob
    revisions = {}
    for refs_path in sorted(glob.glob(os.path.join(RAW, "references*.jsonl"))):
        for l in open(refs_path):
            d = json.loads(l)
            revisions[d["review_id"]] = sorted(d["references"], key=lambda r: r["tcdate"])
    pull = json.load(open(os.path.join(RAW, "pull.json")))

    flagged = [n for n in notes if replies(n, "Decision")[0]["content"].get("consistency_experiment")]
    partner = {n["id"]: RX_URL.search(replies(n, "Decision")[0]["content"]["consistency_experiment"]).group(1) for n in flagged}
    norm = lambda t: re.sub(r"\s+", " ", t.strip().lower())
    by_title = collections.defaultdict(list)
    for n in notes:
        by_title[norm(n["content"]["title"])].append(n["id"])
    title_pairs = {frozenset(v) for v in by_title.values() if len(v) == 2}
    official_pairs = {frozenset((a, b)) for a, b in partner.items() if b in byid}
    assert title_pairs == official_pairs, (len(title_pairs), len(official_pairs))

    keys = sorted({frozenset((a, b)) for a, b in partner.items()}, key=lambda k: min(byid[x]["number"] for x in k if x in byid))
    pair_rows, copy_rows, review_rows = [], [], []
    os.makedirs(os.path.join(OUT, "pairs"), exist_ok=True)
    for k, key in enumerate(keys, start=1):
        pair_id = f"n21-{k:03d}"
        ids = sorted((x for x in key if x in byid), key=lambda x: byid[x]["number"])
        private = [x for x in key if x not in byid]
        pdir = os.path.join(OUT, "pairs", pair_id)
        os.makedirs(pdir, exist_ok=True)
        first = byid[ids[0]]
        c = first["content"]
        paper = {"pair_id": pair_id, "title": c["title"], "abstract": c.get("abstract"), "keywords": c.get("keywords"),
                 "authors": c.get("authors"), "tldr": c.get("TL;DR"), "code": c.get("code"),
                 "prior_submission_venue": c.get("submission_history_-_venue_and_year") or None,
                 "prior_submission_improvements": c.get("submission_history_-_improvements_made") or None,
                 "forums": {"a": ids[0], "b": (ids + private)[1]}, "both_public": not private,
                 "final_decision": replies(first, "Decision")[0]["content"]["decision"],
                 "source": {"api": pull["api"], "pulled": pull["pulled"], "licence": "reviews and comments CC BY 4.0 (OpenReview terms)"}}
        rec = {"pair_id": pair_id, "title": c["title"], "both_public": not private, "final_decision": paper["final_decision"]}
        md = [f"# {pair_id}: {c['title']}", "", f"Final decision (program chairs, both copies): **{paper['final_decision']}**", "",
              f"Abstract: {c.get('abstract','')}", ""]
        sides = {}
        for side, fid in zip("ab", ids + private):
            sdir = os.path.join(pdir, side)
            os.makedirs(sdir, exist_ok=True)
            if fid not in byid:
                other = sides["a"]["other_recommendation"]
                rec.update({f"forum_{side}": fid, f"own_decision_{side}": other})
                json.dump({"pair_id": pair_id, "side": side, "forum": fid, "public": False, "own_decision": other,
                           "note": "this copy's reviews are not public; its decision is stated on the other copy"}, open(os.path.join(sdir, "decision.json"), "w"), indent=1)
                md += [f"## Committee {side.upper()} (forum {fid}): not public", f"Own decision: **{other}** (stated on the other copy).", ""]
                continue
            n = byid[fid]
            dec = replies(n, "Decision")[0]
            own = RX_OWN.search(dec["content"]["consistency_experiment"]).group(1)
            oth = RX_OTHER.search(dec["content"]["consistency_experiment"]).group(1)
            decision = {"pair_id": pair_id, "side": side, "forum": fid, "paper_number": n["number"], "public": True,
                        "own_decision": own, "other_recommendation": oth, "final_decision": dec["content"]["decision"],
                        "meta_review": dec["content"].get("comment"), "decision_date": ts(dec["tcdate"]),
                        "program_chairs_note": dec["content"]["consistency_experiment"]}
            json.dump(decision, open(os.path.join(sdir, "decision.json"), "w"), indent=1)
            sides[side] = decision
            pdf_src = os.path.join(RAW, "pdf", f"{fid}.pdf")
            if os.path.exists(pdf_src) and not os.path.exists(os.path.join(sdir, "paper.pdf")):
                try:
                    os.link(pdf_src, os.path.join(sdir, "paper.pdf"))
                except OSError:
                    shutil.copy(pdf_src, os.path.join(sdir, "paper.pdf"))
            # reviews, with initial and final versions
            revs = []
            for r in sorted(replies(n, "Official_Review"), key=lambda r: r["tcdate"]):
                edited = r["tmdate"] - r["tcdate"] > 3600_000  # edited more than an hour after posting
                rr = {"pair_id": pair_id, "side": side, "forum": fid, "review_id": r["id"], "reviewer": role(r["signatures"][0]),
                      "rating_final": leading_int(r["content"].get("rating")), "rating_final_label": r["content"].get("rating"),
                      "confidence_final": leading_int(r["content"].get("confidence")), "confidence_label": r["content"].get("confidence"),
                      "edited_after_posting": edited, "posted": ts(r["tcdate"]), "last_edited": ts(r["tmdate"]) if edited else None,
                      **{f: r["content"].get(f) for f in REVIEW_FIELDS}}
                revs.append(rr)
            with open(os.path.join(sdir, "reviews.jsonl"), "w") as f:
                for rr in revs:
                    f.write(json.dumps(rr) + "\n")
            review_rows += [{k: v for k, v in rr.items() if k not in REVIEW_FIELDS} |
                            {"len_main_review": len(rr.get("main_review") or ""), "time_spent_reviewing": rr.get("time_spent_reviewing")} for rr in revs]
            # discussion: author responses and reviewer / AC comments, threaded
            review_ids = {r["review_id"]: r["reviewer"] for r in revs}
            disc = []
            for cmt in sorted(replies(n, "Official_Comment") + replies(n, "Public_Comment"), key=lambda r: r["tcdate"]):
                disc.append({"id": cmt["id"], "replyto": cmt["replyto"], "replyto_role": review_ids.get(cmt["replyto"], "forum" if cmt["replyto"] == fid else "comment"),
                             "by": role(cmt["signatures"][0]), "date": ts(cmt["tcdate"]), "title": cmt["content"].get("title"),
                             "text": cmt["content"].get("comment"), "public_comment": cmt["invitation"].endswith("/Public_Comment")})
            with open(os.path.join(sdir, "discussion.jsonl"), "w") as f:
                for d in disc:
                    f.write(json.dumps(d) + "\n")
            eth = [{"id": e["id"], "by": role(e["signatures"][0]), "date": ts(e["tcdate"]), **e["content"]} for e in replies(n, "Ethics_Review")]
            if eth:
                with open(os.path.join(sdir, "ethics.jsonl"), "w") as f:
                    for e in eth:
                        f.write(json.dumps(e) + "\n")
            fin = [r["rating_final"] for r in revs]
            rec.update({f"forum_{side}": fid, f"number_{side}": n["number"], f"own_decision_{side}": own, f"n_reviews_{side}": len(revs),
                        f"n_reviews_edited_{side}": sum(r["edited_after_posting"] for r in revs),
                        f"mean_rating_{side}": round(float(np.mean(fin)), 3), f"min_rating_{side}": min(fin), f"max_rating_{side}": max(fin),
                        f"mean_confidence_{side}": round(float(np.mean([r["confidence_final"] for r in revs])), 3),
                        f"n_author_responses_{side}": sum(d["by"] == "Authors" for d in disc),
                        f"n_reviewer_comments_{side}": sum(d["by"].startswith("Reviewer") for d in disc),
                        f"n_ac_comments_{side}": sum(d["by"].startswith("Area_Chair") for d in disc)})
            copy_rows.append({"pair_id": pair_id, "side": side, "forum": fid, "paper_number": n["number"], "own_decision": own,
                              "other_recommendation": oth, "final_decision": dec["content"]["decision"], "n_reviews": len(revs),
                              "n_reviews_edited": rec[f"n_reviews_edited_{side}"], "mean_rating_final": rec[f"mean_rating_{side}"],
                              "len_meta_review": len(dec["content"].get("comment") or ""), "n_author_responses": rec[f"n_author_responses_{side}"],
                              "n_reviewer_comments": rec[f"n_reviewer_comments_{side}"], "n_ac_comments": rec[f"n_ac_comments_{side}"],
                              "n_ethics_reviews": len(eth)})
            # readable rendering
            md += [f"## Committee {side.upper()} (forum {fid}, paper {n['number']})", "",
                   f"Own decision: **{own}**. Other committee's recommendation: {oth}. Final decision: {dec['content']['decision']}.", "",
                   "| Reviewer | Rating | Confidence | Time spent (h) | Posted | Edited after posting |", "|---|---|---|---|---|---|"]
            for r in revs:
                md.append(f"| {r['reviewer']} | {int(r['rating_final'])} | {int(r['confidence_final'])} | {r.get('time_spent_reviewing') or ''} | {r['posted']} | {r['last_edited'] or 'no'} |")
            md += ["", f"Mean rating {rec[f'mean_rating_{side}']}. Ratings and text are the final versions; OpenReview does not expose earlier versions, so a rating change after the rebuttal shows only as an edit date and in the discussion.", ""]
            for r in revs:
                md += [f"### Review by {r['reviewer']} (rating {r['rating_final_label']}; confidence {r['confidence_label']}{'; edited ' + r['last_edited'] if r['last_edited'] else ''})", "",
                       f"**Summary.** {r.get('summary') or ''}", "", f"**Main review.** {r.get('main_review') or ''}", "",
                       f"**Limitations and societal impact.** {r.get('limitations_and_societal_impact') or ''}", ""]
                if r.get("ethical_concerns"):
                    md += [f"**Ethical concerns.** {r['ethical_concerns']}", ""]
            if disc:
                md += ["### Author responses and discussion", ""]
                for d in disc:
                    tgt = d["replyto_role"]
                    md += [f"**{d['by']}** ({d['date']}, replying to {tgt}){': ' + d['title'] if d.get('title') else ''}", "", d.get("text") or "", ""]
            if eth:
                md += ["### Ethics review", ""] + [json.dumps(e) for e in eth] + [""]
            md += ["### Meta-review (area chair, posted with the decision)", "", dec["content"].get("comment") or "", ""]
        rec["kind"] = kind_of(TIER[rec["own_decision_a"]], TIER[rec["own_decision_b"]])
        paper["kind"] = rec["kind"]
        json.dump(paper, open(os.path.join(pdir, "paper.json"), "w"), indent=1)
        open(os.path.join(pdir, "pair.md"), "w").write("\n".join(md))
        pair_rows.append(rec)

    pairs = pd.DataFrame(pair_rows)
    pairs.to_csv(os.path.join(OUT, "pairs.csv"), index=False)
    pd.DataFrame(copy_rows).to_csv(os.path.join(OUT, "copies.csv"), index=False)
    pd.DataFrame(review_rows).to_csv(os.path.join(OUT, "reviews.csv"), index=False)

    # reconciliation with the report's Table 1
    e = json.load(open(os.path.join(ROOT, "data", "experiments.json")))["neurips2021"]["table1"]["value"]
    lab = e["row_labels_original"][:4]
    rep = np.array(e["counts"])[:4, :4]
    report = collections.Counter()
    for i, a in enumerate(lab):
        for j, b in enumerate(lab):
            report[kind_of(a, b)] += int(rep[i, j])
    ours = collections.Counter(pairs.kind)
    order = ["oral", "spotlight", "poster", "reject"]
    kinds = [kind_of(a, b) for i, a in enumerate(order) for b in order[i:]]
    lines = ["# NeurIPS 2021 pairs against the report's Table 1", "",
             "Unordered pairs of the two committees' own decisions. Report: arXiv:2306.03262, Table 1 (recommendations after calibration), 764 decided papers. Public: pairs with at least one copy on OpenReview.", "",
             "| Pair of decisions | Report | Public | Difference |", "|---|---|---|---|"]
    lines += [f"| {k} | {report[k]} | {ours[k]} | {ours[k] - report[k]} |" for k in kinds]
    acc = {"oral", "spotlight", "poster"}
    both_acc = lambda cnt: sum(v for k, v in cnt.items() if all(x in acc for x in k.split("/")))
    split = lambda cnt: sum(v for k, v in cnt.items() if "/" in k and len({x in acc for x in k.split("/")}) == 2)
    lines += ["", f"Accepted by both: report {both_acc(report)}, public {both_acc(ours)}.",
              f"Split decisions: report {split(report)}, public {split(ours)}. A paper with one accept recommendation was accepted unless the other committee found a fatal flaw (the report's rule); the split pairs missing from the public record are those rejections, whose reviews are private.",
              f"Rejected by both: report {report['reject']}, public {ours['reject']} (authors who opted in; {int((~pairs.both_public).sum())} of them with only one copy public).",
              "", f"Pairs: {len(pairs)}; both copies public: {int(pairs.both_public.sum())}; reviews: {len(review_rows)}; reviews edited after posting: {sum(1 for r in review_rows if r['edited_after_posting'])}; title match equals the official pairing: yes."]
    open(os.path.join(OUT, "reconciliation.md"), "w").write("\n".join(lines) + "\n")
    print("\n".join(lines))

    readme = f"""# NeurIPS 2021 consistency experiment: the public pairs

Both committees' complete public records for every duplicated paper of the NeurIPS 2021 consistency
experiment (Beygelzimer, Dauphin, Liang and Wortman Vaughan, arXiv:2306.03262) that has at least one
copy on OpenReview. Source: OpenReview's API ({pull['api']}), pulled {pull['pulled'][:10]}; reviews and
comments are CC BY 4.0 under OpenReview's terms. Built by `scripts/build_neurips2021_pairs.py` from the raw
API responses in `data/raw/openreview/neurips2021/`, which are never edited.

Pairing: each copy's decision note carries a `consistency_experiment` field naming that committee's own
decision, the other committee's recommendation and the other copy's forum. The title match gives the
same pairs. Counts against the report's Table 1: `reconciliation.md`.

## Layout

- `pairs.csv`: one row per pair. `a` is the copy with the lower paper number; the record does not say which copy was the original. `kind` is the unordered pair of the committees' own decisions (`oral/poster`, `spotlight/reject`, `poster`, ...).
- `copies.csv`: one row per public committee copy.
- `reviews.csv`: one row per review, numeric fields and text lengths.
- `pairs/<pair_id>/paper.json`: title, abstract, authors, keywords, code link, prior-submission declaration where given, both forums, final decision.
- `pairs/<pair_id>/pair.md`: both committees' records side by side, readable.
- `pairs/<pair_id>/a|b/decision.json`: own decision, other committee's recommendation, final decision, meta-review text, the program chairs' note.
- `pairs/<pair_id>/a|b/reviews.jsonl`: every review, every field, as the forum shows it now; `edited_after_posting` and `last_edited` say whether the reviewer changed it more than an hour after posting (OpenReview's API returns no earlier versions, so the pre-rebuttal rating is not recoverable).
- `pairs/<pair_id>/a|b/discussion.jsonl`: author responses and reviewer, area-chair and public comments, threaded by `replyto`.
- `pairs/<pair_id>/a|b/ethics.jsonl`: ethics reviews where they exist.
- `pairs/<pair_id>/a|b/paper.pdf`: the submission as reviewed.

Not public, so absent: reviewer, area-chair and senior-area-chair identities; the reviewer–area-chair
discussion; the pairs rejected by both committees whose authors did not opt in; the four fatal-flaw
rejections; the reviews' earlier versions.

Counts: {len(pairs)} pairs, {int(pairs.both_public.sum())} with both copies public, {len(review_rows)} reviews.
"""
    open(os.path.join(OUT, "README.md"), "w").write(readme)


if __name__ == "__main__":
    main()
