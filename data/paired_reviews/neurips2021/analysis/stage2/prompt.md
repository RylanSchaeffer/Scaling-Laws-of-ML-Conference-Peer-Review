# Stage 2 prompt, version 1 (2026-10-14): the set of reasons, grown one pair at a time

Stage 1 produced, for each pair of committees, notes on why the two committees recommended what they
did (`analysis/stage1/<pair_id>.json` and `.md`). Stage 2 builds one shared set of reasons for the
discrepancies, one pair at a time, in a fixed order. You are one turn of that process.

## The set of reasons

`run_<k>/reasons.json` is a JSON list. Each entry:

```
{"id": "R07", "name": "at most eight words", "definition": "one sentence, general enough to apply to other pairs",
 "created_by_pair": "n21-048", "created_turn": 2, "exemplar": "one sentence of evidence from the creating pair"}
```

A reason is a **cause of the difference between the two committees' recommendations**, stated as a
mechanism, not a property of the paper. Examples of the right level: "one committee had a champion
reviewer whose high score rested on enthusiasm, not specifics"; "the committees weighted the same
novelty concern differently"; "one committee's reviewer made a checkable factual claim about the
paper that was wrong"; "the area chair overrode the reviewers' scores"; "the rebuttal persuaded one
committee and not the other"; "one committee's reviews were thin and its reviewers inattentive";
"one committee raised a substantive issue the other did not see". Wrong level: "the paper is about
causal inference"; "committee B gave lower scores".

## A turn

1. Read `reasons.json` (an empty list if the file does not exist) and the pair's stage 1 notes, the
   `.md` and the `.json`. Read the pair's own records under `pairs/<pair_id>/` only when the notes
   leave a judgement unclear.
2. For every existing reason, decide whether it applies to this pair, with one line of justification
   each way. Apply a reason when the mechanism it names is present in this pair, whether or not it
   is the main cause.
3. Decide whether this pair shows a cause that no existing reason covers. Prefer reuse: if an existing
   definition fits with a plain reading, use it. Add a reason only when none fits; give it the next
   id, a name, a one-sentence definition general enough for other pairs, and the exemplar from this
   pair. A pair may add more than one reason, and may apply several reasons.
4. Pairs whose committees agreed (kind without a slash) are judged the same way: reasons may apply
   to a divergence in scores or arguments short of a different recommendation; if nothing applies,
   apply nothing.
5. Write `run_<k>/turn_<nnn>.json`:

```
{"run": k, "turn": n, "pair_id": "...", "kind": "...", "prompt_version": 1,
 "reasons_before": ["R01", ...],
 "judgements": [{"id": "R01", "applies": true, "justification": "..."}, ...],   // one per reason in reasons_before
 "added": [{"id": "R08", "name": "...", "definition": "...", "justification": "why no existing reason covers this"}],
 "reasoning": "a short paragraph on how you decided",
 "reasons_after": ["R01", ...]}
```

6. Append the added reasons to `reasons.json` and write it back. Never edit or delete an existing
   entry. Edit no other file.

## Back-fill

A reason created at turn n was never judged for the pairs of turns 1 to n-1. The back-fill judge for
pair p (turn n) reads the final `reasons.json`, takes every reason with `created_turn > n`, and judges
each for pair p from its stage 1 notes, yes or no with one line of justification. It writes
`run_<k>/backfill_<pair_id>.json`:

```
{"run": k, "pair_id": "...", "turn": n, "prompt_version": 1,
 "judgements": [{"id": "R23", "applies": false, "justification": "..."}, ...]}
```

Back-fill creates no reasons.

## Merge

The merge judge reads the final `reasons.json` and names every pair of entries that are one
mechanism under two names. It writes `run_<k>/merges.json`:

```
{"run": k, "prompt_version": 1, "merges": [{"keep": "R03", "absorb": "R19", "why": "..."}], "reasoning": "..."}
```

Entries that overlap but name different mechanisms are not merged. The merge is applied afterwards by
a script, which ORs the judgements; nothing in `reasons.json` is deleted.
