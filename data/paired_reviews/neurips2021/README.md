# NeurIPS 2021 consistency experiment: the public pairs

Both committees' complete public records for every duplicated paper of the NeurIPS 2021 consistency
experiment (Beygelzimer, Dauphin, Liang and Wortman Vaughan, arXiv:2306.03262) that has at least one
copy on OpenReview. Source: OpenReview's API (https://api.openreview.net), pulled 2026-10-14; reviews and
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

Counts: 309 pairs, 301 with both copies public, 2373 reviews.
