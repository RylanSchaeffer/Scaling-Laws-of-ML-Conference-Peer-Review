"""Copy the figures the paper includes into the paper repository.

The paper is its own repository, the paper/ submodule, and that is the repository Overleaf
syncs. It keeps its own copies of the figure PDFs main.tex includes, in paper/figures/.
peerreview.plotting.save refreshes a copy whenever its figure is redrawn; this script also
adds the figures main.tex newly includes. With --check it changes nothing and exits 1 if a
copy is missing or differs from figures/.

Usage: uv run python scripts/sync_paper_figures.py [--check]
"""

from __future__ import annotations

import argparse
import filecmp
import os
import re
import shutil
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIG = os.path.join(ROOT, "figures")
PAPER = os.path.join(ROOT, "paper")
PAPER_FIG = os.path.join(PAPER, "figures")


def included(tex_path: str) -> list[str]:
    """File names of every \\includegraphics in main.tex, commented-out lines skipped."""
    names = set()
    with open(tex_path) as f:
        for line in f:
            line = re.sub(r"(?<!\\)%.*", "", line)
            for name in re.findall(r"\\includegraphics\s*(?:\[[^\]]*\])?\s*\{([^}]+)\}", line):
                names.add(name if os.path.splitext(name)[1] else name + ".pdf")
    return sorted(names)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--check", action="store_true",
                    help="change nothing; exit 1 if a copy is missing or differs from figures/")
    args = ap.parse_args()

    tex = os.path.join(PAPER, "main.tex")
    if not os.path.exists(tex):
        sys.exit("paper/main.tex not found: run  git submodule update --init")

    names = included(tex)
    problems, copied = [], []
    for name in names:
        src, dest = os.path.join(FIG, name), os.path.join(PAPER_FIG, name)
        if not os.path.exists(src):
            if os.path.exists(dest):
                print(f"{name}: only in paper/figures/ (not drawn by the scripts here)")
            else:
                print(f"{name}: main.tex includes it, but neither figures/ nor paper/figures/ has it")
                problems.append(name)
            continue
        if os.path.exists(dest) and filecmp.cmp(src, dest, shallow=False):
            continue
        if args.check:
            print(f"{name}: paper/figures/ copy is {'out of date' if os.path.exists(dest) else 'missing'}")
            problems.append(name)
        else:
            os.makedirs(PAPER_FIG, exist_ok=True)
            shutil.copyfile(src, dest)
            print(f"copied figures/{name} -> paper/figures/{name}")
            copied.append(name)

    if os.path.isdir(PAPER_FIG):
        for name in sorted(set(os.listdir(PAPER_FIG)) - set(names)):
            if not name.startswith("."):
                print(f"{name}: in paper/figures/, but main.tex no longer includes it")

    if copied:
        print("Commit inside paper/ first, then commit the new paper pointer in this repository.")
    if problems:
        sys.exit(1)
    if not copied:
        print(f"paper/figures/ matches figures/ for all {len(names)} figures main.tex includes")


if __name__ == "__main__":
    main()
