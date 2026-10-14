# Run 1

Scope: the 50 pairs in which at least one committee recommended an oral or a spotlight, turns 1 to 50 of
`analysis/order.json`, one pair at a time. Prompt version 2. Model `claude-opus-5-5` through Claude Code
workflow agents (`scripts/workflows/stage2_reasons.js`).

Effort: turns 1 to 6 ran at effort `max` (5 to 10 minutes each, 2026-10-13 22:30 to 23:19 PDT). Turns 7 to 50
ran at effort `high` so that the pass could finish overnight; the back-fill and merge ran at effort `high` as well.
Nothing else changed between the two segments.

Result: 50 turns, 37 reasons, 4 merges, 33 reasons after merge, 466 ticks, every pair-reason judged (`derived/coverage.json`).
