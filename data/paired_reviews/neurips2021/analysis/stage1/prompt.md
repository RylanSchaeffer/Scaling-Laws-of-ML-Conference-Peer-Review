# Stage 1 prompt, version 1 (2026-10-14)

You are analysing one paper from the NeurIPS 2021 consistency experiment. The paper was reviewed by two
independent committees, A and B, each with its own reviewers and area chair, who did not know of each
other. Your job is to explain, succinctly and with evidence, why the two committees reached the
recommendations they did, and in particular why one recommended more than the other.

## Inputs

All files are under `{pair_dir}`:

- `pair.md`: both committees' records side by side: every review (rating, confidence, time spent,
  summary, main review, limitations, and whether and when the reviewer edited it after posting), the
  author responses and discussion, and each committee's meta-review and own decision. Read all of it.
  Ratings and text are the final versions; OpenReview exposes no earlier version, so a score change
  after the rebuttal shows only as an edit date and in what reviewers say in the discussion.
- `paper.json`: title, abstract, authors, final decision, the kind of discrepancy.
- `a/` and `b/`: the same records as JSON lines (`reviews.jsonl`, `discussion.jsonl`, `decision.json`,
  `ethics.jsonl` where present) and two PDFs: `paper_submitted.pdf`, the anonymised version the
  reviewers saw, and `paper.pdf`, the version on the forum today (the camera-ready, for accepted
  papers). Use `paper_submitted.pdf` when you need to judge whether a reviewer's specific claim about
  the paper is right (a stated error, a missing baseline, a misread result); if it is missing, use
  `paper.pdf` and say so. Do not summarise the paper for its own sake.

Committee A's own decision: {own_a}. Committee B's own decision: {own_b}. Final decision: {final}.
Kind of discrepancy: {kind}. Ratings are NeurIPS's 1 to 10 scale (10 award quality, 7 accept,
5 borderline accept, 1 very strong reject); confidence 1 to 5.

## What to produce

Write two files and nothing else:

1. `{out_json}`: the JSON object described below. Every field is required; use null where there is
   nothing to say. Quote evidence by reviewer pseudonym (e.g. Reviewer_h23K) and, where it helps, a
   short phrase from the text.
2. `{out_md}`: your notes, at most 600 words: a verdict paragraph first, then one short paragraph per
   committee, then the issues one committee raised and the other did not. Plain prose, no headers
   beyond those three parts, no bullet lists longer than five items.

Be concrete and sceptical. A reviewer who gives a 9 with a two-line review and no engagement in
discussion is not evidence of quality; say so. A reviewer who gives a 3 for a specific, checkable
reason that the paper confirms is strong evidence; say so. Do not pad, do not hedge, do not write
"it is possible that". Where the two committees simply weighted the same facts differently, say that
plainly.

### JSON fields

```
{
  "pair_id": "{pair_id}",
  "prompt_version": 1,
  "kind": "{kind}",
  "committees": {
    "a": {
      "own_decision": "...",
      "ratings_final": [..], "confidences": [..], "reviews_edited_after_posting": ["Reviewer_..."],
      "outlier": {"present": true|false, "reviewer": "Reviewer_xxxx"|null, "direction": "champion"|"detractor"|null,
                  "basis": "principled"|"exuberant"|"inattentive"|"unclear"|null, "evidence": "..."},
      "inattentive_reviews": [{"reviewer": "...", "evidence": "..."}],
      "checkable_claims": [{"reviewer": "...", "claim": "...", "checked_against_paper": "correct"|"incorrect"|"not_checked", "evidence": "..."}],
      "rebuttal": {"scores_moved": "up"|"down"|"none"|"mixed"|"unknown", "by_whom": ["Reviewer_..."], "evidence": "edit dates and what reviewers said in discussion", "what_convinced_or_not": "..."},
      "ac": {"followed_reviews": "yes"|"partly"|"no", "evidence": "...", "meta_review_leans_on": "scores"|"a_specific_reviewer"|"own_reading"|"unclear"},
      "main_reasons_for_decision": ["...", "..."]
    },
    "b": { same structure }
  },
  "issues_only_a": ["..."], "issues_only_b": ["..."], "shared_issues": ["..."],
  "same_facts_weighted_differently": true|false,
  "verdict": "one paragraph: why one committee recommended more than the other (or why they agreed)",
  "candidate_reasons": ["short phrase", "short phrase"],
  "confidence": "high"|"medium"|"low",
  "evidence_pointers": ["Reviewer_xxxx final review", "Committee B meta-review", "paper Section 4.2"]
}
```

`candidate_reasons` are your own short names for the causes of the discrepancy, three to six words
each, in your words; a later stage will build a shared catalogue from them.
