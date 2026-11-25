# Project rules

## The paper is a submodule

`paper/` is its own repository (`Scaling-Laws-of-ML-Conference-Peer-Review-Manuscript`), the one
Overleaf syncs. Commit and push inside `paper/` first, then `git add paper` here and commit.
Overleaf edits arrive with `git -C paper pull`. The paper's figures are copies in `paper/figures/`:
redrawing one refreshes it; after adding a figure to `main.tex`, run `scripts/sync_paper_figures.py`.

## Tiers are separate: gold, silver, bronze (Rylan, 2026-10-18)

| Tier | Medal | Meaning | Code key |
|---|---|---|---|
| Best Papers | gold | the first three papers of the award ordering | `best` |
| Oral | silver | an Oral that is not one of the Best Papers | `oral` |
| Spotlight | bronze | a Spotlight, nothing higher | `spot` |
| Accepted | qualified, did not place | accepted with no award | `accept` |
| Rejected | did not qualify | rejected | `reject` |

Each paper has exactly one tier. No tier contains another.
"Spotlight" means Spotlight only; "Accepted" means accepted with no award.

A tier together with every tier above it is "X or Better", always written in full:
Oral or Better (`oral_or_better`), Spotlight or Better (`spot_or_better`),
Accepted or Better (`accept_or_better`, every accepted paper).

- Never use a bare tier name for an "or Better" set, in text, figures, code or docs.
- Never write "nested tiers", "merely accepted" or "each tier includes the tiers above it".
- Capitalised "Accepted" is only the tier. Lowercase "accept"/"accepted" is the decision, so
  "the papers the first review accepted" are Accepted or Better.
- A bare code key is the separate tier; a key ending in `_or_better` is the set.
- `src/peerreview/tiers.py` defines the tiers. `docs/terminology.md` is the full source of truth.
