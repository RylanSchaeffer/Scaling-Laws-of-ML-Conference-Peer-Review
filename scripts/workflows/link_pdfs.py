"""Hard-link every pulled PDF (current and as-reviewed) into its pair folder; safe to run while agents read."""
import os, json, glob
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
R = os.path.join(ROOT, "data", "paired_reviews", "neurips2021", "pairs"); RAW = os.path.join(ROOT, "data", "raw", "openreview", "neurips2021")
n = 0
for pdir in glob.glob(f"{R}/n21-*"):
    paper = json.load(open(f"{pdir}/paper.json"))
    for side in "ab":
        fid = paper["forums"][side]
        for sub, name in (("pdf", "paper.pdf"), ("pdf_submitted", "paper_submitted.pdf")):
            dst, src = f"{pdir}/{side}/{name}", f"{RAW}/{sub}/{fid}.pdf"
            if not os.path.exists(dst) and os.path.exists(src):
                os.link(src, dst); n += 1
print("linked", n)
