"""Add the values the study uses to data/venues.csv (columns N_used, acc_rate_used,
orals_used, used_note).

Rule: keep the handoff value unless a primary source checked on 2026-10-02 gives a
different value (docs/claims.md, "Contradictions"); count orals for the main track
only; fill a blank oral count from a primary source. Every override is listed below
with its reason, so each number in the paper traces to this file and docs/claims.md.

Usage: uv run python scripts/build_venues_used.py
"""

from __future__ import annotations

import pandas as pd

from peerreview.venues import VENUES_CSV

# (venue, year, denominator) -> overrides and the reason.
OVERRIDES = {
    ("NeurIPS", 2015, "submissions"): dict(orals=15, note="orals from the official schedule (handoff blank)"),
    ("NeurIPS", 2016, "submissions"): dict(orals=45, note="orals from the official schedule (handoff blank)"),
    ("NeurIPS", 2017, "submissions"): dict(acc=679 / 3240, note="rate 679/3,240 (rounding slip in handoff)"),
    ("NeurIPS", 2020, "submissions"): dict(N=9467, acc=1900 / 9467, note="N 9,467 full submissions (press release)"),
    ("NeurIPS", 2021, "submissions"): dict(acc=2334 / 9122, note="rate 2,334/9,122 (fact sheet)"),
    ("NeurIPS", 2022, "submissions"): dict(N=9634, acc=2671 / 9634, orals=184,
                                           note="N 9,634 full submissions (fact sheet), 2,671 main-track papers "
                                                "(proceedings), 184 main-track orals (fact sheet)"),
    ("NeurIPS", 2025, "submissions"): dict(orals=77, note="77 main-track orals (fact sheet's 87 includes D&B and Position)"),
    ("ICML", 2023, "submissions"): dict(acc=1828 / 6538, orals=155, note="1,828 accepted (PMLR); 155 orals (virtual site)"),
    ("ICML", 2024, "submissions"): dict(orals=129, note="129 main-track orals (144 includes 15 position)"),
    ("ICML", 2025, "submissions"): dict(orals=108, note="108 main-track orals (120 includes 12 position)"),
    ("ICLR", 2018, "submissions"): dict(acc=336 / 981, note="336 accepted incl. orals (official schedule); 32.0% counted posters only"),
    ("ICLR", 2021, "submissions"): dict(N=3014, acc=860 / 3014, note="N 3,014, 860 accepted (fact sheet)"),
    ("ICLR", 2022, "submissions"): dict(N=3391, acc=1095 / 3391, orals=55, note="N 3,391, 1,095 accepted, 55 orals (fact sheet)"),
    ("ICLR", 2023, "submissions"): dict(acc=1574 / 4938, note="rate 1,574/4,938 (rounding slip in handoff)"),
}


def main() -> None:
    v = pd.read_csv(VENUES_CSV, keep_default_na=False, na_values=[""])
    v["N_used"] = v["N"]
    v["acc_rate_used"] = v["acc_rate"]
    v["orals_used"] = v["orals"]
    v["used_note"] = "handoff values"
    for (venue, year, den), o in OVERRIDES.items():
        mask = (v.venue == venue) & (v.year == year) & (v.denominator == den)
        assert mask.sum() == 1, (venue, year, den)
        if "N" in o:
            v.loc[mask, "N_used"] = o["N"]
        if "acc" in o:
            v.loc[mask, "acc_rate_used"] = round(o["acc"], 5)
        if "orals" in o:
            v.loc[mask, "orals_used"] = o["orals"]
        v.loc[mask, "used_note"] = o["note"]
    v.loc[(v.venue == "NeurIPS") & (v.year == 2026), "used_note"] = "handoff values; no primary source yet (treat as unverified)"
    v.to_csv(VENUES_CSV, index=False)
    print(v[["venue", "year", "denominator", "N_used", "acc_rate_used", "orals_used", "used_note"]].to_string(index=False))


if __name__ == "__main__":
    main()
