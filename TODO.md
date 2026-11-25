# TODOs

Status, 2026-11-24: the preprint is submitted to arXiv (`submit/8424335`; CC BY 4.0; cs.LG,
cross-listed to cs.DL and cs.CY), waiting to be announced. Resume around 2026-12-08.

## When arXiv announces the paper

- [ ] Put the arXiv ID in the README: the badge (now "coming soon") and the citation.

## ICML 2027 position-paper version

The header of `paper/main.tex` lists these too. Check with
`uv run python scripts/check_paper.py --submission`.

- [ ] A title that starts with "Position:" and states the position.
- [ ] Write the Alternative Views section (commented out in `main.tex`, still a TODO).
- [ ] Anonymize: drop the `[preprint]` option and the GitHub link in "Code and data".
- [ ] Keep the main body to at most 8 pages (7 now). The AI Use Statement is done.
- [ ] Look up the submission deadline in the call for position papers. Do not mention ICML in
      the arXiv comments or anywhere public while the paper is under review.

## Optional

- [ ] Check the NeurIPS 2026 counts against the official fact sheet once it is out, probably in
      December (`data/venues.csv`, `data/spotlights.csv`: 30,709 submissions and 292 Spotlights
      come from secondary reports). Rerun the affected results if they change.
- [ ] Small fixes from the pre-arXiv audit:
  - the last appendix page holds only a few lines (Figure 7's float placement);
  - the Figure 6d caption should say that the integer 1-10, six-point and ICLR curves nearly coincide;
  - Section 2 could state the Best Papers' fitted exponent, 0.27 (95% CI -0.29 to 0.83), next to
    the $N^0$ it models.
- [ ] Delete the private `Scaling-Laws-of-ML-Conference-Peer-Review-Private` GitHub repository
      once its backup of the old, unscrubbed history is no longer needed.

## Notes

- A new arXiv version: rebuild the upload with `uv run python scripts/make_arxiv_source.py`
  (`arxiv/arxiv_source.tar.gz`). arXiv allows 2 submissions per calendar month per account.
- File uploads (arXiv, OpenReview) go through Claude in Chrome, which now works without help.
