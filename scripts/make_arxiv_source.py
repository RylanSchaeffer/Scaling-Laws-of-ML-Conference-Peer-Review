"""Build the source to upload to arXiv from paper/: arxiv/source/ and arxiv/arxiv_source.tar.gz.

arXiv publishes the source of every version, so main.tex goes up without its comments (the
submission plan, the old abstract and the commented-out sections stay private). arXiv does not
need refs.bib: the bibliography goes up as main.bbl, which tectonic writes here. The bundle holds
main.tex, main.bbl, the local style files that main.tex loads (directly or through another local
style file) and the figures main.tex includes, nothing else.

Usage: uv run python scripts/make_arxiv_source.py [--tectonic PATH]
"""

from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAPER = os.path.join(ROOT, "paper")
OUT = os.path.join(ROOT, "arxiv")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sync_paper_figures import included  # noqa: E402


def first_comment(line: str) -> int:
    """Index of the % that starts the line's comment, or -1. A backslash escapes the next
    character, so \\% is a percent sign and \\\\% starts a comment."""
    i = 0
    while i < len(line):
        if line[i] == "\\":
            i += 2
            continue
        if line[i] == "%":
            return i
        i += 1
    return -1


def strip_comments(text: str) -> str:
    """Drop comment lines and trailing comments. A trailing comment that follows text directly
    keeps its bare %, which suppresses the end-of-line space as before. Runs of blank lines
    become one."""
    out = []
    for line in text.split("\n"):
        k = first_comment(line)
        if k == -1:
            out.append(line.rstrip())
        elif line[:k].strip():
            before = line[:k]
            out.append(before.rstrip() if before != before.rstrip() else before + "%")
        # else: a comment line, dropped
    res = []
    for line in out:
        if not (line == "" and res and res[-1] == ""):
            res.append(line)
    return "\n".join(res).strip("\n") + "\n"


def packages(text: str) -> set[str]:
    names = set()
    for group in re.findall(r"\\(?:usepackage|RequirePackage)\s*(?:\[[^\]]*\])?\s*\{([^}]+)\}", strip_comments(text)):
        names |= {n.strip() for n in group.split(",")}
    return names


def local_styles(tex: str) -> list[str]:
    """The .sty files in paper/ that main.tex loads, directly or through another of them."""
    available = {f[:-4] for f in os.listdir(PAPER) if f.endswith(".sty")}
    need, todo = set(), [tex]
    while todo:
        with open(todo.pop()) as f:
            for name in packages(f.read()) & available - need:
                need.add(name)
                todo.append(os.path.join(PAPER, name + ".sty"))
    return sorted(n + ".sty" for n in need)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--tectonic", default=shutil.which("tectonic") or "tectonic")
    args = ap.parse_args()

    tex = os.path.join(PAPER, "main.tex")
    with open(tex) as f:
        source = f.read()
    styles, figures = local_styles(tex), included(tex)

    # main.bbl, from a full build in a scratch copy (paper/ is left untouched).
    with tempfile.TemporaryDirectory() as tmp:
        shutil.copytree(PAPER, tmp, dirs_exist_ok=True, ignore=shutil.ignore_patterns(".git*"))
        run = subprocess.run([args.tectonic, "--keep-intermediates", "main.tex"], cwd=tmp,
                             capture_output=True, text=True)
        if run.returncode or not os.path.exists(os.path.join(tmp, "main.bbl")):
            sys.exit(f"tectonic failed:\n{run.stderr[-3000:]}")
        with open(os.path.join(tmp, "main.bbl")) as f:
            bbl = f.read()

    src = os.path.join(OUT, "source")
    shutil.rmtree(src, ignore_errors=True)
    os.makedirs(src)
    stripped = strip_comments(source)
    with open(os.path.join(src, "main.tex"), "w") as f:
        f.write(stripped)
    with open(os.path.join(src, "main.bbl"), "w") as f:
        f.write(bbl)
    for name in styles:
        shutil.copyfile(os.path.join(PAPER, name), os.path.join(src, name))
    for name in figures:
        dest = os.path.join(src, "figures", name)
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        shutil.copyfile(os.path.join(PAPER, "figures", name), dest)

    # Checks: nothing private or unfinished left, and every citation has its entry.
    problems = []
    if any(first_comment(line) not in (-1, len(line) - 1) for line in stripped.split("\n")):
        problems.append("a comment is left in main.tex")
    if "TODO" in stripped:
        problems.append("TODO in main.tex")
    if any(ord(c) > 127 for c in stripped + bbl):
        problems.append("non-ASCII characters (pdflatex may reject them)")
    cited = {k.strip() for g in re.findall(r"\\cite[a-zA-Z]*\*?(?:\[[^\]]*\])*\{([^}]+)\}", stripped) for k in g.split(",")}
    items = set(re.findall(r"\\bibitem\s*(?:\[.*?\]\s*)?\{([^}]+)\}", bbl, flags=re.S))
    if cited - items:
        problems.append(f"cited but not in main.bbl: {', '.join(sorted(cited - items))}")

    tarball = os.path.join(OUT, "arxiv_source.tar.gz")

    def clean(info: tarfile.TarInfo) -> tarfile.TarInfo:
        info.uid = info.gid = 0
        info.uname = info.gname = ""
        return info

    with tarfile.open(tarball, "w:gz") as tar:
        for name in sorted(["main.tex", "main.bbl", *styles, *(os.path.join("figures", n) for n in figures)]):
            tar.add(os.path.join(src, name), arcname=name, filter=clean)

    print(f"{tarball}: {os.path.getsize(tarball) / 1e3:.0f} kB")
    print(f"  main.tex ({len(source.splitlines()) - len(stripped.splitlines())} comment or blank lines removed), "
          f"main.bbl ({len(items)} entries for {len(cited)} cited keys), {', '.join(styles)}, "
          f"{len(figures)} figures")
    for p in problems:
        print(f"PROBLEM: {p}")
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main()
