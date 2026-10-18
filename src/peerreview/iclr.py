"""ICLR public reviews: download, parse, variance decomposition, split-half replay.

Handoff §8.2 (steps 1 to 3), §8.3, §10.2 and §10.3.

Source
------
`papercopilot/paperlists` on GitHub, one JSON file per year,
https://raw.githubusercontent.com/papercopilot/paperlists/main/iclr/iclr{year}.json.
Each file is a JSON list with one record (dict) per OpenReview submission.
`download(year)` caches the file as data/raw/iclr{year}.json and does nothing if a
real file is already there. Some years (2025 and 2026 when this was written) are
stored with Git LFS: the raw URL then returns a ~130-byte pointer
("version https://git-lfs.github.com/spec/v1", "oid sha256:...", "size ...").
`download` detects the pointer, fetches the object from
https://media.githubusercontent.com/media/papercopilot/paperlists/main/iclr/iclr{year}.json,
and checks its SHA-256 and size against the pointer before it saves the file.

`load_papers()` parses every year into one DataFrame (one row per submission) and
caches it as data/processed/iclr_papers.csv.gz. Years 2017 to 2025 (YEARS_MAIN)
are required. 2026 (YEARS_EXTRA) is parsed if its file can be had, but it is not a
main-analysis year: the dump's values are exactly {0,2,4,6,8,10}, but the meaning
of each point is unverified (handoff §10.3, status U), and its ICC(1) (0.13 on
decided papers) is far below every other year (0.33 to 0.58), which suggests that
the 2026 scores differ in kind. A likely cause: after the OpenReview API leak of
27 November 2025, ICLR reverted every review text and score to its state at the
start of the discussion period and froze the discussion ("ICLR 2026 Response to
Security Incident", blog.iclr.cc/?p=1063, read from a search extract only). The
2026 scores are then pre-discussion scores, unlike the other years' final scores.
This is not verified against the dump itself.

Parsing rules (one per output column)
-------------------------------------
year        The year of the file the record came from.
paper_id    The record's `id` field (the OpenReview forum id). Records that repeat
            an (year, paper_id) pair are dropped after the first. In the dumps every
            repeat is an exact copy of a withdrawn or desk-rejected record: 3 extra
            records in 2024 (3 ids), 5 in 2025 (3 ids), 1 in 2026 (1 id). All are
            placeholders ("test", "xxx", "111", "Null2") except one real withdrawn
            2025 paper ("Worldcraft", 3 reviews).
track       The record's `track` field, stripped ('' if missing).
main_track  True iff track.lower() == 'main'. Every record in 2017 to 2026 has
            track 'main'.
status_raw  The record's `status` field, stripped, unchanged otherwise.
status      `normalise_status(status_raw)`. The label is lower-cased, a leading
            "ICLR <year>" and a leading "Conditional" are removed, and the first
            matching keyword rule below gives the status (rules in this order):
              desk_reject 'desk reject...' ('Desk Reject', 'Desk Rejected Submission').
              withdrawn   'withdraw...' ('Withdraw', 'Withdrawn Submission').
              reject      'reject...' or 'workshop' ('Reject'; 'Workshop' in 2017 and
                          2018, and 'Invite to Workshop Track': a rejection from the
                          conference track).
              oral        'oral', 'talk', 'top 5%' ('Oral'; 'Talk' in 2020; 'Top-5%'
                          in 2023, "notable top 5%", presented as orals; 'Accept
                          (Oral)', 'Accept (Talk)', 'Accept (notable-top-5%)';
                          'ICLR 2026 ConditionalOral').
              spotlight   'spotlight', 'top 25%' ('Spotlight'; 'Top-25%' in 2023;
                          'Accept (notable-top-25%)').
              poster      'poster', or a bare 'accept'/'accepted' with no tier
                          ('Poster'; 'Accept (Poster)'; 'Accept: poster';
                          'ICLR 2026 ConditionalPoster').
              other       anything else ('Active', 3 records in 2018).
            The dumps hold only the short labels ('Oral', 'Top-5%', ...); the
            OpenReview decision strings are matched too, so that an upstream
            relabelling cannot move accepted papers into 'other'.
            Conditional acceptances (15 records, 2026 only) count as accepted: with
            them the 2026 oral count is 224, the figure in handoff §10.4.
decided     status in {oral, spotlight, poster, reject}.
accepted    status in {oral, spotlight, poster}; False for every other status.
ratings     The per-review overall scores, in the order the record lists its
            reviewers, as numbers joined by ';' (integers without a decimal point;
            '' when the paper has no review). Score field: `recommendation` when
            the record has that key with a non-empty value, else `rating`. In the
            dumps `rating` is used in 2017 to 2021 and again in 2024 to 2026;
            `recommendation` only in 2022 and 2023 (the handoff's "from 2022" is
            true only for 2022 to 2023). `parse_scores` turns a value into numbers:
              * None or '' -> no scores; an int or float -> one score; a list ->
                one score per element (each element parsed as below).
              * A string is split on ';' (the dumps' separator), or on '|' when
                there is no ';'. A string with neither is split on ',' only when
                it holds no ':' (so a label such as "8: accept, good paper" stays
                one token).
              * Each token's score is its leading number (regex
                `^\\s*[-+]?\\d+(\\.\\d+)?`), so "6: marginally above" -> 6. A token
                without a leading number is dropped.
            In 2017 to 2026 every value is '' or ';'-joined integers, and the count
            of scores always equals the count of entries in `reviewers` and
            `confidence`.
n_reviews   Number of parsed scores.
mean_rating Mean of the parsed scores (NaN when n_reviews == 0). It agrees with
            the dumps' own `rating_avg` / `recommendation_avg` field.
citations   The record's `gs_citation` (Google Scholar count) as a float. -1 and
            None mean "not found" and become NaN. All 2026 records are -1.

Analyses (functions below)
--------------------------
`variance_decomposition` (§8.3): one-way random-effects ANOVA with unequal group
sizes on the individual scores of papers with >= 2 reviews:
  MSB = sum_i n_i (m_i - m)^2 / (k - 1),  MSW = sum_ij (y_ij - m_i)^2 / (N - k),
  n0 = (N - sum_i n_i^2 / N) / (k - 1),
  sigma_b^2 = (MSB - MSW) / n0,  sigma_w^2 = MSW,
  ICC(1) = sigma_b^2 / (sigma_b^2 + sigma_w^2).
The second estimate is the exact correlation between two distinct reviews of the
same paper, the paper drawn uniformly and the two reviews drawn uniformly from it
(`pair_correlation(weight='paper')`); `weight='pair'` gives every review pair equal
weight instead (as in counts of "review pairs").
`decision_threshold_logistic`: maximum-likelihood logistic regression of accepted
on the paper-mean score; the threshold is -a/b, with a delta-method SE.
`decision_threshold_binned`: acceptance rate in bins of the mean score (width
0.25, bins with >= 5 papers), made monotone by weighted isotonic regression (pool
adjacent violators), then the 0.5 crossing by linear interpolation between bin
means.
`split_half` (§8.2): see its docstring.
"""

from __future__ import annotations

import hashlib
import json
import re
import urllib.request
import warnings
from collections.abc import Iterable, Sequence
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import special

ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = ROOT / "data" / "raw"
PROCESSED_DIR = ROOT / "data" / "processed"
CACHE_PATH = PROCESSED_DIR / "iclr_papers.csv.gz"

RAW_URL = "https://raw.githubusercontent.com/papercopilot/paperlists/main/iclr/iclr{year}.json"
LFS_URL = "https://media.githubusercontent.com/media/papercopilot/paperlists/main/iclr/iclr{year}.json"
LFS_HEADER = b"version https://git-lfs.github.com/spec/v1"

YEARS_MAIN: tuple[int, ...] = tuple(range(2017, 2026))
YEARS_EXTRA: tuple[int, ...] = (2026,)

# Score points per year, as observed in the dumps (handoff §10.3).
_INT10 = tuple(float(v) for v in range(1, 11))
SCALES: dict[int, tuple[float, ...]] = {
    2017: _INT10,
    2018: _INT10,
    2019: _INT10,
    2020: (1.0, 3.0, 6.0, 8.0),
    2021: _INT10,
    **{y: (1.0, 3.0, 5.0, 6.0, 8.0, 10.0) for y in range(2022, 2026)},
    2026: (0.0, 2.0, 4.0, 6.0, 8.0, 10.0),
}

STATUSES = ("oral", "spotlight", "poster", "reject", "withdrawn", "desk_reject", "other")
DECIDED = frozenset({"oral", "spotlight", "poster", "reject"})
ACCEPTED = frozenset({"oral", "spotlight", "poster"})

# Ordered (status, pattern) rules; the first pattern that matches the lower-cased
# label wins. The order matters: "desk reject" before "reject", and every
# reject/withdraw rule before the accept tiers.
_STATUS_RULES: tuple[tuple[str, re.Pattern], ...] = (
    ("desk_reject", re.compile(r"\bdesk[\s_-]*reject")),
    ("withdrawn", re.compile(r"\bwithdr[ae]w")),
    ("reject", re.compile(r"\breject|\bworkshop\b")),
    ("oral", re.compile(r"\boral\b|\btalk\b|\btop[\s_-]*5\s*%")),
    ("spotlight", re.compile(r"\bspotlight\b|\btop[\s_-]*25\s*%")),
    ("poster", re.compile(r"\bposter\b|^accept(ed)?$")),
)

COLUMNS = (
    "year",
    "paper_id",
    "track",
    "status_raw",
    "status",
    "decided",
    "accepted",
    "main_track",
    "ratings",
    "n_reviews",
    "mean_rating",
    "citations",
)


def scale_label(year: int) -> str:
    """'1-10' for the integer scale, else the points joined by '/'."""
    pts = SCALES.get(year)
    if pts is None:
        return ""
    if pts == _INT10:
        return "1-10"
    return "/".join(f"{p:g}" for p in pts)


# ---------------------------------------------------------------------------
# Download
# ---------------------------------------------------------------------------


def _is_lfs_pointer(path: Path) -> bool:
    with open(path, "rb") as f:
        return f.read(len(LFS_HEADER)) == LFS_HEADER


def _fetch(url: str, timeout: float = 300.0) -> bytes:
    with urllib.request.urlopen(url, timeout=timeout) as r:
        return r.read()


def _parse_lfs_pointer(blob: bytes) -> tuple[str, int]:
    text = blob.decode("ascii", "replace")
    oid = re.search(r"oid sha256:([0-9a-f]{64})", text)
    size = re.search(r"size (\d+)", text)
    if not (oid and size):
        raise ValueError("malformed Git LFS pointer")
    return oid.group(1), int(size.group(1))


def download(year: int, raw_dir: Path | str = RAW_DIR, force: bool = False) -> Path:
    """Cache iclr{year}.json in raw_dir; skip if a real (non-pointer) file is there."""
    raw_dir = Path(raw_dir)
    path = raw_dir / f"iclr{year}.json"
    if path.exists() and not force and path.stat().st_size > 0 and not _is_lfs_pointer(path):
        return path
    raw_dir.mkdir(parents=True, exist_ok=True)
    blob = _fetch(RAW_URL.format(year=year))
    if blob.startswith(LFS_HEADER):
        oid, size = _parse_lfs_pointer(blob)
        blob = _fetch(LFS_URL.format(year=year))
        if len(blob) != size or hashlib.sha256(blob).hexdigest() != oid:
            raise OSError(f"ICLR {year}: Git LFS object does not match its pointer")
    tmp = path.with_suffix(".json.part")
    tmp.write_bytes(blob)
    tmp.replace(path)
    return path


def read_records(year: int, raw_dir: Path | str = RAW_DIR, fetch: bool = True) -> list[dict]:
    """The raw JSON list for one year (downloaded first if needed and fetch=True)."""
    path = Path(raw_dir) / f"iclr{year}.json"
    if fetch:
        path = download(year, raw_dir)
    with open(path) as f:
        data = json.load(f)
    if not isinstance(data, list):
        raise ValueError(f"ICLR {year}: expected a JSON list, got {type(data).__name__}")
    return data


# ---------------------------------------------------------------------------
# Parsing
# ---------------------------------------------------------------------------

_LEADING_NUMBER = re.compile(r"^\s*([-+]?\d+(?:\.\d+)?)")


def _token_score(tok) -> float | None:
    if tok is None or isinstance(tok, bool):
        return None
    if isinstance(tok, (int, float, np.integer, np.floating)):
        x = float(tok)
        return x if np.isfinite(x) else None
    m = _LEADING_NUMBER.match(str(tok))
    return float(m.group(1)) if m else None


def parse_scores(value) -> list[float]:
    """Per-review scores from a score field value (rules in the module docstring)."""
    if value is None:
        return []
    if isinstance(value, (list, tuple)):
        tokens = list(value)
    elif isinstance(value, (int, float, np.integer, np.floating)) and not isinstance(value, bool):
        tokens = [value]
    else:
        s = str(value).strip()
        if not s:
            return []
        if ";" in s:
            tokens = s.split(";")
        elif "|" in s:
            tokens = s.split("|")
        elif "," in s and ":" not in s:
            tokens = s.split(",")
        else:
            tokens = [s]
    out = []
    for t in tokens:
        x = _token_score(t)
        if x is not None:
            out.append(x)
    return out


def score_field(record: dict) -> str:
    """'recommendation' if the record carries a non-empty one, else 'rating'."""
    v = record.get("recommendation")
    if v is not None and str(v).strip() != "":
        return "recommendation"
    return "rating"


def normalise_status(raw) -> str:
    """Map a raw status label to one of STATUSES (rules in the module docstring)."""
    s = str(raw or "").strip().lower()
    s = re.sub(r"^iclr\s*\d{4}\s*", "", s)
    s = re.sub(r"^conditional\s*", "", s)
    for status, pattern in _STATUS_RULES:
        if pattern.search(s):
            return status
    return "other"


def _fmt(x: float) -> str:
    return str(int(x)) if float(x).is_integer() else f"{x:g}"


def _citations(v) -> float:
    try:
        x = float(v)
    except (TypeError, ValueError):
        return np.nan
    return x if np.isfinite(x) and x >= 0 else np.nan


def parse_record(rec: dict, year: int) -> dict:
    """One output row from one raw record."""
    scores = parse_scores(rec.get(score_field(rec)))
    track = str(rec.get("track") or "").strip()
    status_raw = str(rec.get("status") or "").strip()
    status = normalise_status(status_raw)
    return {
        "year": int(year),
        "paper_id": str(rec.get("id") or "").strip(),
        "track": track,
        "status_raw": status_raw,
        "status": status,
        "decided": status in DECIDED,
        "accepted": status in ACCEPTED,
        "main_track": track.lower() == "main",
        "ratings": ";".join(_fmt(x) for x in scores),
        "n_reviews": len(scores),
        "mean_rating": float(np.mean(scores)) if scores else np.nan,
        "citations": _citations(rec.get("gs_citation")),
    }


def parse_records(records: Iterable[dict], year: int) -> pd.DataFrame:
    """Parse one year's records and drop repeated (year, paper_id) rows."""
    df = pd.DataFrame([parse_record(r, year) for r in records], columns=list(COLUMNS))
    return df.drop_duplicates(subset=["year", "paper_id"], keep="first").reset_index(drop=True)


def parse_year(year: int, raw_dir: Path | str = RAW_DIR, fetch: bool = True) -> pd.DataFrame:
    return parse_records(read_records(year, raw_dir, fetch=fetch), year)


def write_cache(df: pd.DataFrame, path: Path | str = CACHE_PATH) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)


def read_cache(path: Path | str = CACHE_PATH) -> pd.DataFrame:
    """Read the processed CSV back with the same types it was written with."""
    df = pd.read_csv(
        path,
        dtype={"paper_id": str, "track": str, "status_raw": str, "status": str, "ratings": str},
        keep_default_na=False,
        na_values={"mean_rating": [""], "citations": [""]},
    )
    for c in ("decided", "accepted", "main_track"):
        if df[c].dtype != bool:
            df[c] = df[c].astype(str).str.lower().eq("true")
    return df[list(COLUMNS)]


def load_papers(
    years: Sequence[int] | None = None,
    refresh: bool = False,
    cache_path: Path | str = CACHE_PATH,
    raw_dir: Path | str = RAW_DIR,
) -> pd.DataFrame:
    """All years in one DataFrame, cached as CSV.

    years=None means YEARS_MAIN (required) plus YEARS_EXTRA (used if the file can
    be had). The cache is reused unless refresh=True or it lacks a required year.
    """
    required = tuple(YEARS_MAIN if years is None else years)
    optional = YEARS_EXTRA if years is None else ()
    cache_path = Path(cache_path)
    if cache_path.exists() and not refresh:
        df = read_cache(cache_path)
        if set(required) <= set(df["year"].unique()):
            keep = set(required) | set(optional)
            return df[df["year"].isin(keep)].reset_index(drop=True)
    frames = [parse_year(y, raw_dir) for y in required]
    for y in optional:
        try:
            frames.append(parse_year(y, raw_dir))
        except (OSError, ValueError) as e:  # network or file trouble: skip the extra year
            warnings.warn(f"ICLR {y} skipped: {e}")
    df = pd.concat(frames, ignore_index=True)
    write_cache(df, cache_path)
    return df


def scores_list(df: pd.DataFrame) -> list[np.ndarray]:
    """Per-paper score arrays from the 'ratings' column."""
    return [np.array([float(t) for t in s.split(";")]) if s else np.empty(0) for s in df["ratings"]]


def padded_scores(df: pd.DataFrame) -> np.ndarray:
    """(papers x max reviews) array of scores, NaN-padded."""
    lists = scores_list(df)
    width = max((len(x) for x in lists), default=0)
    out = np.full((len(lists), width), np.nan)
    for i, x in enumerate(lists):
        out[i, : len(x)] = x
    return out


# ---------------------------------------------------------------------------
# Variance decomposition (§8.3)
# ---------------------------------------------------------------------------


def _suff_stats(groups: Sequence[np.ndarray]) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    n = np.array([len(g) for g in groups], float)
    S = np.array([np.sum(g) for g in groups], float)
    Q = np.array([np.sum(np.square(g)) for g in groups], float)
    return n, S, Q


def _anova_from_stats(n, S, Q, w=None) -> dict[str, float]:
    """One-way random-effects ANOVA from per-group sums; w = integer group multiplicities."""
    w = np.ones_like(n) if w is None else np.asarray(w, float)
    k = w.sum()
    N = (w * n).sum()
    T = (w * S).sum()
    ssb = (w * S**2 / n).sum() - T**2 / N
    ssw = (w * Q).sum() - (w * S**2 / n).sum()
    msb = ssb / (k - 1)
    msw = ssw / (N - k)
    n0 = (N - (w * n**2).sum() / N) / (k - 1)
    sb2 = (msb - msw) / n0
    return {
        "k": k,
        "N": N,
        "n0": n0,
        "msb": msb,
        "msw": msw,
        "var_between": sb2,
        "var_within": msw,
        "icc1": sb2 / (sb2 + msw),
    }


def anova_icc(groups: Sequence[np.ndarray]) -> dict[str, float]:
    """ICC(1) and variance components; groups with fewer than 2 values are ignored."""
    groups = [np.asarray(g, float) for g in groups if len(g) >= 2]
    if len(groups) < 2:
        raise ValueError("need at least two groups with two or more values")
    return _anova_from_stats(*_suff_stats(groups))


def bootstrap_icc(groups: Sequence[np.ndarray], n_boot: int = 200, seed: int = 0) -> np.ndarray:
    """ICC(1) over n_boot resamples of whole papers (with replacement)."""
    groups = [np.asarray(g, float) for g in groups if len(g) >= 2]
    n, S, Q = _suff_stats(groups)
    rng = np.random.default_rng(seed)
    k = len(groups)
    out = np.empty(n_boot)
    for b in range(n_boot):
        w = np.bincount(rng.integers(0, k, k), minlength=k)
        out[b] = _anova_from_stats(n, S, Q, w)["icc1"]
    return out


def pair_correlation(groups: Sequence[np.ndarray], weight: str = "paper") -> float:
    """Exact corr between two distinct reviews of the same paper.

    weight='paper': draw a paper uniformly, then an ordered pair of its reviews.
    weight='pair':  draw an ordered pair uniformly from all within-paper pairs.
    """
    groups = [np.asarray(g, float) for g in groups if len(g) >= 2]
    n, S, Q = _suff_stats(groups)
    pairs = n * (n - 1)
    if weight == "paper":
        w = np.full_like(n, 1.0 / len(n))
    elif weight == "pair":
        w = pairs / pairs.sum()
    else:
        raise ValueError(weight)
    m = (w * S / n).sum()
    var = (w * Q / n).sum() - m**2
    cov = (w * (S**2 - Q) / pairs).sum() - m**2
    return float(cov / var)


def decision_threshold_logistic(x, accepted) -> dict[str, float]:
    """Logistic regression of accepted on x; threshold = x where P(accept) = 1/2."""
    x = np.asarray(x, float)
    y = np.asarray(accepted, float)
    mu, sd = x.mean(), x.std()
    X = np.column_stack([np.ones_like(x), (x - mu) / sd])
    beta = np.zeros(2)
    for _ in range(200):
        p = special.expit(X @ beta)
        H = X.T @ (X * (p * (1 - p))[:, None])
        step = np.linalg.solve(H, X.T @ (y - p))
        beta += step
        if np.max(np.abs(step)) < 1e-12:
            break
    p = special.expit(X @ beta)
    cov = np.linalg.inv(X.T @ (X * (p * (1 - p))[:, None]))
    a, b = beta
    g = np.array([-1.0 / b, a / b**2])
    return {
        "threshold": float(mu + sd * (-a / b)),
        "threshold_se": float(sd * np.sqrt(g @ cov @ g)),
        "slope": float(b / sd),
    }


def _pava(y: np.ndarray, w: np.ndarray) -> np.ndarray:
    """Weighted isotonic (non-decreasing) regression by pool adjacent violators."""
    vals, wts, cnt = [], [], []
    for yi, wi in zip(y, w):
        vals.append(float(yi))
        wts.append(float(wi))
        cnt.append(1)
        while len(vals) > 1 and vals[-2] > vals[-1]:
            v2, w2, c2 = vals.pop(), wts.pop(), cnt.pop()
            v1, w1, c1 = vals.pop(), wts.pop(), cnt.pop()
            vals.append((v1 * w1 + v2 * w2) / (w1 + w2))
            wts.append(w1 + w2)
            cnt.append(c1 + c2)
    return np.repeat(vals, cnt)


def decision_threshold_binned(x, accepted, width: float = 0.25, min_count: int = 5) -> float:
    """0.5 crossing of the binned acceptance rate (isotonic, linear interpolation)."""
    x = np.asarray(x, float)
    y = np.asarray(accepted, float)
    b = np.floor(x / width + 1e-9).astype(int)
    tab = pd.DataFrame({"b": b, "x": x, "y": y}).groupby("b").agg(x=("x", "mean"), y=("y", "mean"), n=("y", "size"))
    tab = tab[tab["n"] >= min_count]
    if len(tab) < 2:
        return np.nan
    xs = tab["x"].to_numpy()
    r = _pava(tab["y"].to_numpy(), tab["n"].to_numpy())
    above = np.nonzero(r >= 0.5)[0]
    if len(above) == 0 or above[0] == 0:
        return np.nan
    j = above[0]
    if r[j] == 0.5:
        # A flat run exactly at 1/2: take the middle of the run.
        run = np.nonzero(r == 0.5)[0]
        return float(0.5 * (xs[run[0]] + xs[run[-1]]))
    return float(xs[j - 1] + (0.5 - r[j - 1]) * (xs[j] - xs[j - 1]) / (r[j] - r[j - 1]))


def mean_rule(x, accepted) -> dict[str, float]:
    """Compare the actual decisions with 'accept the top A by mean score'.

    A = number actually accepted. Ties at the cut are broken at random; the
    returned precision |Top_A(x) & accepted| / A is its exact expectation.
    """
    x = np.asarray(x, float)
    acc = np.asarray(accepted, bool)
    A = int(acc.sum())
    if A == 0:
        return {"cutoff": np.nan, "precision": np.nan}
    cut = np.sort(x)[::-1][A - 1]
    above = x > cut
    tied = x == cut
    need = A - int(above.sum())
    hits = acc[above].sum() + need * acc[tied].sum() / tied.sum()
    return {"cutoff": float(cut), "precision": float(hits / A)}


def variance_decomposition(df: pd.DataFrame, n_boot: int = 200, seed: int = 0) -> dict[str, float]:
    """§8.3 summary for one year's papers (pass the decided main-track rows)."""
    df = df[df["n_reviews"] >= 1]
    groups = scores_list(df)
    multi = [g for g in groups if len(g) >= 2]
    an = anova_icc(multi)
    boot = bootstrap_icc(multi, n_boot=n_boot, seed=seed)
    allv = np.concatenate(groups)
    m = df["mean_rating"].to_numpy()
    acc = df["accepted"].to_numpy(bool)
    st = df["status"].to_numpy()
    logit = decision_threshold_logistic(m, acc)
    rule = mean_rule(m, acc)
    out = {
        "n_papers": len(df),
        "n_papers_anova": int(an["k"]),
        "n_scores": int(len(allv)),
        "n_accepted": int(acc.sum()),
        "accept_rate": float(acc.mean()),
        "mean_reviews": float(df["n_reviews"].mean()),
        "share_ge3_reviews": float((df["n_reviews"] >= 3).mean()),
        "share_ge4_reviews": float((df["n_reviews"] >= 4).mean()),
        "mean_score": float(allv.mean()),
        "sd_score": float(allv.std(ddof=1)),
        "sd_between": float(np.sqrt(max(an["var_between"], 0.0))),
        "sd_within": float(np.sqrt(an["var_within"])),
        "n0": float(an["n0"]),
        "icc1": float(an["icc1"]),
        "icc1_se": float(boot.std(ddof=1)),
        "pair_corr": pair_correlation(multi, "paper"),
        "pair_corr_pooled": pair_correlation(multi, "pair"),
        "mean_paper_avg": float(m.mean()),
        "sd_paper_avg": float(m.std(ddof=1)),
        "mean_avg_accepted": float(m[acc].mean()),
        "sd_avg_accepted": float(m[acc].std(ddof=1)),
        "mean_avg_rejected": float(m[~acc].mean()),
        "sd_avg_rejected": float(m[~acc].std(ddof=1)),
    }
    for s in ("oral", "spotlight", "poster"):
        sel = st == s
        out[f"n_{s}"] = int(sel.sum())
        out[f"mean_avg_{s}"] = float(m[sel].mean()) if sel.any() else np.nan
    out.update(
        threshold_logit=logit["threshold"],
        threshold_logit_se=logit["threshold_se"],
        logit_slope=logit["slope"],
        threshold_binned=decision_threshold_binned(m, acc),
        cutoff_topA=rule["cutoff"],
        mean_rule_precision=rule["precision"],
    )
    return out


# ---------------------------------------------------------------------------
# Split-half replay (§8.2 steps 1 to 3)
# ---------------------------------------------------------------------------

SPLIT_METRICS = (
    "inconsistent",
    "precision",
    "ovl_top10",
    "ovl_top30",
    "ovl_top3",
    "corr_halves",
    "prec_vs_actual",
    "n_ge_cut_A",
    "n_ge_cut_top10",
    "n_ge_cut_top30",
    "n_ge_cut_top3",
)


def _top_mask(x: np.ndarray, K: int, rng: np.random.Generator, eps: float) -> np.ndarray:
    """Row-wise boolean mask of the K largest entries, ties broken uniformly at random.

    eps must be below half the smallest gap between distinct values, so the
    jitter reorders tied entries only.
    """
    j = x + eps * rng.random(x.shape)
    idx = np.argpartition(-j, K - 1, axis=1)[:, :K]
    mask = np.zeros(x.shape, bool)
    np.put_along_axis(mask, idx, True, axis=1)
    return mask


def _kth_largest(x: np.ndarray, K: int) -> np.ndarray:
    n = x.shape[1]
    return np.partition(x, n - K, axis=1)[:, n - K]


def _rowcorr(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    a = a - a.mean(axis=1, keepdims=True)
    b = b - b.mean(axis=1, keepdims=True)
    return (a * b).sum(1) / np.sqrt((a * a).sum(1) * (b * b).sum(1))


def split_half_draws(
    scores: np.ndarray,
    accepted: np.ndarray,
    n_splits: int = 200,
    seed: int = 0,
    A: int | None = None,
    Ks: Sequence[int] = (10, 30),
    extra_Ks: Sequence[int] = (3,),
    chunk: int = 20,
) -> dict[str, np.ndarray]:
    """Per-split metrics for papers with >= 4 reviews.

    scores: (papers x width) NaN-padded score array; every row needs >= 4 scores.
    In each split every paper's reviews are put in a uniformly random order; the
    first two form half 1 and the next two half 2 (extras are dropped). Each half
    accepts its top A papers by half mean (A defaults to accepted.sum()), ties
    broken uniformly at random, and likewise picks its top K for each K in Ks and extra_Ks. The
    tie-breaks of extra_Ks (3: the Best Papers' size) come from a second generator, so adding them
    leaves every other draw unchanged.
    Returned per split:
      inconsistent   share of papers accepted by exactly one half
      precision      |Acc1 & Acc2| / A
      ovl_top{K}     |Top_K(half 1) & Top_K(half 2)| / K
      corr_halves    Pearson corr of the two half means (before tie-breaking)
      prec_vs_actual |Acc1 & actually accepted| / A
      n_ge_cut_A     papers whose half-1 mean is >= half 1's A-th largest mean
      n_ge_cut_top{K} the same at the K-th largest mean. Values far above A or K
                     mean that the cut falls in a large tie block, so random
                     tie-breaking decides most of the selection.
    """
    scores = np.asarray(scores, float)
    accepted = np.asarray(accepted, bool)
    valid = ~np.isnan(scores)
    if (valid.sum(1) < 4).any():
        raise ValueError("every paper needs at least four scores")
    n, width = scores.shape
    A = int(accepted.sum()) if A is None else int(A)
    if not 1 <= A < n:
        raise ValueError("need 1 <= A < number of papers")
    rng = np.random.default_rng(seed)
    rng_x = np.random.default_rng([seed, 1])  # tie-breaks for extra_Ks only
    out = {m: [] for m in ("inconsistent", "precision", "corr_halves", "prec_vs_actual", "n_ge_cut_A")}
    out.update({f"ovl_top{K}": [] for K in (*Ks, *extra_Ks)})
    out.update({f"n_ge_cut_top{K}": [] for K in (*Ks, *extra_Ks)})
    filled = np.where(valid, scores, 0.0)
    for start in range(0, n_splits, chunk):
        S = min(chunk, n_splits - start)
        keys = rng.random((S, n, width))
        keys[:, ~valid] = 2.0  # padding sorts last
        idx = np.argsort(keys, axis=2)[:, :, :4]
        vals = np.take_along_axis(np.broadcast_to(filled, (S, n, width)), idx, axis=2)
        h1 = vals[..., :2].mean(-1)
        h2 = vals[..., 2:4].mean(-1)
        u = np.unique(np.concatenate([h1.ravel(), h2.ravel()]))
        eps = 0.25 * (np.diff(u).min() if len(u) > 1 else 1.0)
        a1 = _top_mask(h1, A, rng, eps)
        a2 = _top_mask(h2, A, rng, eps)
        out["inconsistent"].append((a1 ^ a2).mean(1))
        out["precision"].append((a1 & a2).sum(1) / A)
        out["prec_vs_actual"].append((a1 & accepted[None, :]).sum(1) / A)
        out["corr_halves"].append(_rowcorr(h1, h2))
        out["n_ge_cut_A"].append((h1 >= _kth_largest(h1, A)[:, None]).sum(1))
        for K, g in [(K, rng) for K in Ks] + [(K, rng_x) for K in extra_Ks]:
            if K < n:
                t1 = _top_mask(h1, K, g, eps)
                t2 = _top_mask(h2, K, g, eps)
                out[f"ovl_top{K}"].append((t1 & t2).sum(1) / K)
                out[f"n_ge_cut_top{K}"].append((h1 >= _kth_largest(h1, K)[:, None]).sum(1))
            else:
                out[f"ovl_top{K}"].append(np.full(S, np.nan))
                out[f"n_ge_cut_top{K}"].append(np.full(S, np.nan))
    return {k: np.concatenate(v) for k, v in out.items()}


def split_half(df: pd.DataFrame, n_splits: int = 200, seed: int = 0, min_reviews: int = 4) -> dict[str, float]:
    """§8.2 replay for one year's decided main-track rows; mean and SD over splits."""
    kept = df[df["n_reviews"] >= min_reviews]
    acc = kept["accepted"].to_numpy(bool)
    draws = split_half_draws(padded_scores(kept), acc, n_splits=n_splits, seed=seed)
    r = pair_correlation(scores_list(kept), "paper")
    out = {
        "n_decided": len(df),
        "n_kept": len(kept),
        "A": int(acc.sum()),
        "accept_rate_kept": float(acc.mean()),
        "accept_rate_decided": float(df["accepted"].mean()),
        "n_splits": n_splits,
        "pair_corr_kept": r,
        "sb_pred_corr_halves": 2 * r / (1 + r),
    }
    for k in SPLIT_METRICS:
        v = draws[k]
        out[f"{k}_mean"] = float(np.mean(v))
        out[f"{k}_sd"] = float(np.std(v, ddof=1))
    return out
