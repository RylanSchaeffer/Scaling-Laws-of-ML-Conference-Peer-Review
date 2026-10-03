"""Check paper/main.pdf against the layout rules of handoff §2: 4 to 6 pages of main
text (the author allowed a seventh on 2 October 2026), the main figure at the bottom of
page 1 or the top of page 2, and one large figure on every later page of the main text.

Usage: uv run python scripts/check_paper.py
"""

from __future__ import annotations

import os
import re

import pymupdf

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main() -> None:
    doc = pymupdf.open(os.path.join(ROOT, "paper", "main.pdf"))
    print(f"pages: {doc.page_count}")
    ref_page = None
    for i, page in enumerate(doc, 1):
        text = page.get_text()
        if ref_page is None and re.search(r"^References\s*$", text, re.M):
            ref_page = i
        H = page.rect.height
        # Figures are vector PDFs: locate them by their caption blocks.
        blocks = [b for b in page.get_text("blocks") if re.match(r"Figure \d:", b[4])]
        where = ", ".join(f"Fig {re.match(r'Figure (\d)', b[4]).group(1)} caption at y={b[1] / H:.2f}" for b in blocks)
        print(f"page {i}: {where or 'no figure caption'}")
    print(f"references start on page {ref_page}")


if __name__ == "__main__":
    main()
