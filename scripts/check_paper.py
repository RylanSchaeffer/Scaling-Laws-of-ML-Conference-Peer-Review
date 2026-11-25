"""Check paper/main.pdf: now the arXiv preprint, later an ICML 2027 position-paper submission.

The paper is first posted to arXiv with its current title and the author's name, then submitted
to ICML 2027's position-paper track. These rules hold for both, print PASS or FAIL, and make the
script exit 1 if one fails:
  - every page is US letter;
  - no "TODO" is left in the PDF.
These hold for the submission. By default they are listed as done or to do; with --submission
they print PASS or FAIL and count like the others:
  - the main body is at most 8 pages (9 with --camera-ready). It is everything before the first
    end-matter heading: AI Use Statement, Acknowledgements, Impact Statement or References;
  - the title starts with "Position:";
  - the main body has an "Alternative Views" section;
  - an AI Use Statement comes before the references;
  - the authors are anonymous ("Anonymous Authors" on page 1).
It then lists where each figure and table caption sits on the main-body pages.

Sources: https://icml.cc/Conferences/2027/CallForPositionPapers,
https://icml.cc/Conferences/2027/CallForPapers and https://icml.cc/Conferences/2027/AuthorInstructions.

Usage: uv run python scripts/check_paper.py [--submission] [--camera-ready] [--pdf PATH]
"""

from __future__ import annotations

import argparse
import os
import re
import sys

import pymupdf

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LETTER = (612, 792)  # US letter, in points
END_MATTER = re.compile(r"^(AI Use Statement|Acknowledgements|Acknowledgments|Impact Statement|References)$")
ALTERNATIVE_VIEWS = re.compile(r"^\d+\.?\s+Alternative Views$")
CAPTION = re.compile(r"^(Figure|Table) (\d+)[.:]")


def text_blocks(page) -> list[tuple[pymupdf.Rect, str]]:
    """The page's lines of text, without the running head, the page number and line numbers. A
    line that runs across the gutter is split into its two columns' parts, since PDF text
    extraction can join two columns' lines that share a baseline; a line with a span that
    crosses the middle of the page (a figure* or table* caption) stays whole."""
    H, mid = page.rect.height, page.rect.width / 2
    out = []
    for block in page.get_text("dict")["blocks"]:
        for line in block.get("lines", []):
            parts, part = [], []
            for span in line["spans"]:
                if part and part[-1]["bbox"][2] <= mid <= span["bbox"][0]:
                    parts.append(part)
                    part = []
                part.append(span)
            parts.append(part)
            for part in parts:
                text = " ".join(" ".join(s["text"] for s in part).split())
                rect = pymupdf.Rect(part[0]["bbox"])
                for s in part[1:]:
                    rect |= pymupdf.Rect(s["bbox"])
                if not text or re.fullmatch(r"[\d\s]+", text) or rect.y1 < 0.08 * H or rect.y0 > 0.94 * H:
                    continue
                out.append((rect, text))
    return out


def before(a: pymupdf.Rect, b: pymupdf.Rect, mid: float) -> bool:
    """Whether block a comes before block b in two-column reading order on the same page. A block
    that spans both columns (a figure* or table*) above b comes first."""
    a_col = 0 if a.x0 < mid else 1
    b_col = 0 if b.x0 < mid else 1
    if a.x0 < mid < a.x1 and a.y1 <= b.y0:
        return True
    return a_col < b_col or (a_col == b_col and a.y1 <= b.y0)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--submission", action="store_true",
                    help="also require the ICML 2027 position-paper submission rules")
    ap.add_argument("--camera-ready", action="store_true", help="allow the camera-ready 9 pages")
    ap.add_argument("--pdf", default=os.path.join(ROOT, "paper", "main.pdf"))
    args = ap.parse_args()
    limit = 9 if args.camera_ready else 8

    doc = pymupdf.open(args.pdf)
    pages = [text_blocks(p) for p in doc]
    always, submission = [], []  # (ok, message) pairs

    sizes = {(round(p.rect.width), round(p.rect.height)) for p in doc}
    always.append((sizes == {LETTER}, f"US letter pages (found {', '.join(f'{w}x{h}' for w, h in sorted(sizes))} pt)"))

    todo = [i + 1 for i, blocks in enumerate(pages) if any("TODO" in t for _, t in blocks)]
    always.append((not todo, "no TODO left" + (f" (pages {', '.join(map(str, todo))})" if todo else "")))

    # Where the main body ends: the first end-matter heading.
    end = next(((i, r, t) for i, blocks in enumerate(pages) for r, t in blocks if END_MATTER.match(t)), None)
    if end is None:
        body_pages = doc.page_count
        submission.append((False, f"main body at most {limit} pages: no AI Use Statement, Acknowledgements, "
                                  "Impact Statement or References heading found"))
    else:
        i, rect, heading = end
        mid = doc[i].rect.width / 2
        body_on_page = any(before(r, rect, mid) for r, t in pages[i] if (r, t) != (rect, heading))
        body_pages = i + 1 if body_on_page else i
        submission.append((body_pages <= limit,
                           f"main body is {body_pages} pages, limit {limit} (it ends at '{heading}' on page {i + 1})"))

    # The title: the largest type on page 1.
    spans = [s for b in doc[0].get_text("dict")["blocks"] for line in b.get("lines", []) for s in line["spans"]]
    largest = max(s["size"] for s in spans)
    title = " ".join(" ".join(s["text"] for s in spans if s["size"] == largest).split())
    submission.append((title.startswith("Position:"), f"title starts with \"Position:\" (title: {title})"))

    def heading_page(pattern: re.Pattern) -> int | None:
        return next((i for i, blocks in enumerate(pages) for _, t in blocks if pattern.match(t)), None)

    alt = heading_page(ALTERNATIVE_VIEWS)
    submission.append((alt is not None and alt < body_pages, "an Alternative Views section in the main body"
                       + (f" (page {alt + 1})" if alt is not None else "")))

    ai = heading_page(re.compile(r"^AI Use Statement$"))
    refs = heading_page(re.compile(r"^References$"))
    submission.append((ai is not None and (refs is None or ai <= refs), "an AI Use Statement before the references"))

    submission.append(("Anonymous Authors" in doc[0].get_text(), "anonymous authors (\"Anonymous Authors\" on page 1)"))

    required = always + (submission if args.submission else [])
    print(f"{args.pdf}: {doc.page_count} pages")
    for ok, message in required:
        print(f"{'PASS' if ok else 'FAIL'}  {message}")
    if not args.submission:
        print("\nFor the ICML 2027 submission (--submission requires these):")
        for ok, message in submission:
            print(f"  {'done ' if ok else 'to do'}  {message}")

    print("\nCaptions on the main-body pages (y: fraction of the page height from the top):")
    for i in range(min(body_pages, doc.page_count)):
        W, H = doc[i].rect.width, doc[i].rect.height
        found = []
        for r, t in pages[i]:
            m = CAPTION.match(t)
            if m:
                span = "both columns" if r.width > 0.6 * W else "one column"
                found.append(f"{m.group(1)} {m.group(2)} at y={r.y0 / H:.2f} ({span})")
        print(f"  page {i + 1}: {'; '.join(found) or 'none'}")

    sys.exit(1 if any(not ok for ok, _ in required) else 0)


if __name__ == "__main__":
    main()
