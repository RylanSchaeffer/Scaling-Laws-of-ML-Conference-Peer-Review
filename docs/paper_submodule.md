# The paper submodule

The manuscript lives in its own private repository,
`Scaling-Laws-of-ML-Conference-Peer-Review-Manuscript`, checked out here at `paper/`. Overleaf
syncs that repository alone, so it never pulls the data. With access to it, clone both with

```bash
git clone --recurse-submodules git@github.com:RylanSchaeffer/Scaling-Laws-of-ML-Conference-Peer-Review.git
```

Then, once per clone, make `git pull` and `git switch` update `paper/` too. Without this, a pull
that moves the `paper` pointer leaves `paper/` behind, and the next `git commit -a` moves the
pointer back:

```bash
git config submodule.recurse true
```

A checkout leaves `paper/` on a detached commit. Before editing there, put it on its branch:

```bash
git -C paper switch main && git -C paper pull --ff-only
```

- **Building.** `cd paper && tectonic main.tex`. `uv run python scripts/check_paper.py` checks the
  preprint and lists what the ICML 2027 submission still needs; with `--submission` it requires them.
- **Figures.** The paper includes its own copies in `paper/figures/`. Redrawing a figure that
  `main.tex` includes also refreshes its copy (`peerreview.plotting.save`). After adding a new
  figure to `main.tex`, run `uv run python scripts/sync_paper_figures.py` (`--check` only reports).
- **Committing.** Commit and push inside `paper/` first, then commit the new `paper` pointer in this
  repository: `git add paper`.
- **Overleaf edits.** Overleaf pushes to the manuscript repository. Bring them here with
  `git -C paper pull`, then commit the new `paper` pointer.
- **arXiv.** `uv run python scripts/make_arxiv_source.py` builds the source to upload: `main.tex`
  without comments, `main.bbl` (arXiv does not need `refs.bib`), the style files and the included
  figures, in `arxiv/` (ignored by git).

**Checking out a commit from before the switch** (when `paper/` held plain files) fails while the
submodule is checked out. Remove the checkout first (commit and push anything in `paper/` before),
then restore it on return. Nothing is downloaded again:

```bash
git submodule deinit -f paper && git switch --detach 53d7424
```

```bash
git switch main && git submodule update --init
```
