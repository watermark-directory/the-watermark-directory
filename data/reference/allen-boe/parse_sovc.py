"""Flatten the Allen County BOE 2026 Primary SOVC (wide cross-tab) -> tidy CSV.

The 2026 Primary has no per-precinct report — only the Statement of Votes Cast, a
wide cross-tab (precincts as rows, candidates as columns, two contests side by side
per page, headers scattered across several lines, 88 precincts split over 3 page
copies per contest). Plain -layout text can't be sliced reliably, so this reads
WORD COORDINATES from `pdftotext -bbox-layout` and reconstructs the table:

* value columns are right-aligned at consistent xMax -> cluster them;
* every contest block ends in 4 fixed tally columns
  (Total Votes Cast, Overvotes, Undervotes, Contest Total) -> use "Contest Total"
  as the contest boundary; the columns before the tail are candidates;
* the contest title sits in a band above each block.

Candidate column order in the SOVC differs from the summary, so candidate NAMES are
resolved by **sum-matching**: each candidate column's total across precincts is
matched to a candidate total in the committed 2026 summary CSV (which also validates
the extraction). Contests whose columns don't reconcile are reported, not guessed.

Numbers are copied verbatim from the PDF; nothing is computed or invented.
"""

from __future__ import annotations

import csv
import re
import sys
from collections import defaultdict
from pathlib import Path

WORD = re.compile(
    r'<word xMin="([\d.]+)" yMin="([\d.]+)" xMax="([\d.]+)" yMax="([\d.]+)">([^<]*)</word>'
)
INT = re.compile(r"-?[\d,]+")
PCODE = re.compile(r"0\d{3}")  # precinct codes 0001-0088 (NOT the banner year "2026")
TALLY_LABELS = {"total votes cast", "total votes", "overvotes", "undervotes", "contest total"}


class Word:
    __slots__ = ("t", "x0", "x1", "y", "y1")

    def __init__(self, x0: float, y: float, x1: float, y1: float, t: str) -> None:
        self.x0, self.y, self.x1, self.y1, self.t = x0, y, x1, y1, t


def page_words(page_xml: str) -> list[Word]:
    return [
        Word(float(a), float(b), float(c), float(d), t.strip())
        for a, b, c, d, t in WORD.findall(page_xml)
        if t.strip()
    ]


def cluster(vals: list[float], tol: float) -> list[float]:
    """Group sorted values within tol; return the max (right edge) of each group."""
    out: list[float] = []
    for v in sorted(vals):
        if out and v - out[-1] <= tol:
            out[-1] = max(out[-1], v)
        else:
            out.append(v)
    return out


def norm(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()


def parse_page(
    words: list[Word],
) -> list[tuple[str, str, int, tuple[str, ...], str, list[tuple[str, int]]]]:
    """Return [(precinct_code, precinct_name, contest_title, [(label, value), ...])].

    One entry per (precinct, contest) found on the page. ``label`` is the stitched
    column header (candidate name or tally label); ``value`` the integer cell.
    """
    prec = [w for w in words if PCODE.fullmatch(w.t) and w.x0 < 60]
    if not prec:
        return []
    row_ys = sorted(w.y for w in prec)
    first_row_y = row_ys[0]

    # numeric cells across precinct rows -> column right-edges (xMax)
    def row_words(y: float) -> list[Word]:
        return sorted((w for w in words if abs(w.y - y) < 4.0), key=lambda w: w.x0)

    col_x: list[float] = []
    for y in row_ys:
        for w in row_words(y):
            if w.x0 >= 60 and INT.fullmatch(w.t):
                col_x.append(w.x1)
    columns = cluster(col_x, 8.0)
    if not columns:
        return []

    def col_of(x1: float) -> int:
        return min(range(len(columns)), key=lambda i: abs(columns[i] - x1))

    # header region: words above the first precinct row, below the page banner
    header = [w for w in words if 53 < w.y < first_row_y - 2]
    # the "VOTE FOR n" and "n of n Precincts Reporting" sub-headers bracket the title;
    # drop any text line that contains those markers.
    drop_y = {
        round(w.y) for w in header if w.t in {"VOTE", "FOR"} or w.t in {"Precincts", "Reporting"}
    }

    def kept(w: Word) -> bool:
        return all(abs(w.y - dy) > 3 for dy in drop_y)

    title_top = min((w.y for w in header), default=first_row_y)
    # title band = top text line(s) above the VOTE FOR marker; labels = below it
    vote_for_y = min((w.y for w in header if w.t == "VOTE"), default=title_top + 8)
    title_words = [w for w in header if kept(w) and w.y < vote_for_y]
    label_words = [w for w in header if kept(w) and w.y > vote_for_y]

    # stitch a label per column from the label words (assign each to nearest column)
    by_col: dict[int, list[Word]] = defaultdict(list)
    for w in label_words:
        i = col_of(w.x1)
        if abs(columns[i] - w.x1) < 26:
            by_col[i].append(w)
    labels = [
        norm(" ".join(w.t for w in sorted(by_col.get(i, []), key=lambda w: (w.y, w.x0))))
        for i in range(len(columns))
    ]

    # group columns into contests by the "Contest Total" boundary
    groups: list[list[int]] = []
    g: list[int] = []
    for i, lab in enumerate(labels):
        g.append(i)
        if norm(lab).lower() == "contest total":
            groups.append(g)
            g = []
    if g:  # trailing columns with no Contest Total (e.g. STATISTICS) form a group
        groups.append(g)

    # title per contest = title-band words within that contest's column x-span,
    # stitched in reading order (line, then x). Separates side-by-side contests and
    # reassembles titles that wrap across lines.
    # non-overlapping x-bands, one per contest, split at the midpoint between adjacent
    # column groups — so an adjacent contest's leading "Dem"/"Rep" can't bleed in.
    bounds: list[tuple[float, float]] = []
    for gi, gr in enumerate(groups):
        lo = -1e9 if gi == 0 else (columns[groups[gi - 1][-1]] + columns[gr[0]]) / 2
        hi = 1e9 if gi == len(groups) - 1 else (columns[gr[-1]] + columns[groups[gi + 1][0]]) / 2
        bounds.append((lo, hi))

    def assign_group(x: float) -> int:
        for gi, (lo, hi) in enumerate(bounds):
            if lo <= x < hi:
                return gi
        return len(groups) - 1

    gtitle: dict[int, list[Word]] = defaultdict(list)
    for w in title_words:
        gtitle[assign_group(w.x0)].append(w)

    def title_for_idx(gi: int) -> str:
        ws = sorted(gtitle.get(gi, []), key=lambda w: (round(w.y / 4), w.x0))
        return norm(" ".join(w.t for w in ws))

    titles_by_group = [title_for_idx(gi) for gi in range(len(groups))]

    out: list[tuple[str, str, int, tuple[str, ...], str, list[tuple[str, int]]]] = []
    for y in row_ys:
        rw = row_words(y)
        code = next(w.t for w in rw if PCODE.fullmatch(w.t))
        # name = words between the code and the first numeric cell (e.g. "Delphos 1A")
        first_num_x = min((w.x0 for w in rw if w.x0 >= 60 and INT.fullmatch(w.t)), default=1e9)
        name_words = [
            w
            for w in rw
            if not PCODE.fullmatch(w.t) and w.x0 < first_num_x and not INT.fullmatch(w.t)
        ]
        name = norm(" ".join(w.t for w in name_words))
        cells: dict[int, int] = {}
        for w in rw:
            if w.x0 >= 60 and INT.fullmatch(w.t):
                cells[col_of(w.x1)] = int(w.t.replace(",", ""))
        for gi, group in enumerate(groups):
            title = titles_by_group[gi]
            pairs = [(labels[i], cells[i]) for i in group if i in cells]
            # stable cross-page key: the candidate-label set (column-local, far more
            # stable than the centered/wrapping titles, which drift between pages).
            ckey = tuple(sorted(lab for lab, _ in pairs if lab and lab.lower() not in TALLY_LABELS))
            if pairs and ckey:
                out.append((code, name, gi, ckey, title, pairs))
    return out


# ----- accumulate across pages, resolve names via the summary, validate -----


def summary_candidates(summary_csv: Path) -> dict[str, dict[str, int]]:
    """{contest -> {candidate: total}} from the committed 2026 summary CSV."""
    tally = {
        "overvotes",
        "undervotes",
        "contest totals",
        "total votes cast",
        "total votes",
        "write-in totals",
        "not assigned",
    }
    out: dict[str, dict[str, int]] = defaultdict(dict)
    for r in csv.DictReader(summary_csv.open(encoding="utf-8")):
        if r["section"] != "contest":
            continue
        choice = norm(r["choice"])
        total = r["total"].replace(",", "")
        if choice.lower() in tally or not total.isdigit():
            continue
        out[norm(r["contest"])][choice] = int(total)
    return out


def main() -> int:
    base = Path(__file__).parent
    cache = base.parent.parent / "cache" / "allen-boe"
    xml_path = cache / "txt" / "2026_PRIMARY_SOVC.bbox.xml"
    if not xml_path.is_file():
        print(f"!! missing {xml_path} (run: pdftotext -bbox-layout <SOVC.pdf>)")
        return 1
    pages = re.split(r"<page ", xml_path.read_text(encoding="utf-8"))[1:]

    # Accumulate by candidate-label set (stable across a contest's 3 precinct pages,
    # far more so than the centered/wrapping titles). Skip percent pages (cells carry %).
    acc: dict[tuple[tuple[str, ...], str], tuple[str, list[tuple[str, int]]]] = {}
    title_votes: dict[tuple[str, ...], dict[str, int]] = defaultdict(lambda: defaultdict(int))
    for pg in pages:
        words = page_words(pg)
        if any("%" in w.t for w in words if re.search(r"\d", w.t)):
            continue
        for code, name, _gi, ckey, title, pairs in parse_page(words):
            acc[(ckey, code)] = (name, pairs)
            if title:
                title_votes[ckey][title] += 1

    contests: dict[tuple[str, ...], list[tuple[str, str, list[tuple[str, int]]]]] = defaultdict(
        list
    )
    for (ckey, code), (name, pairs) in acc.items():
        contests[ckey].append((code, name, pairs))
    # display title per contest = the most frequent stitched title across its pages
    disp_title = {k: max(tv, key=lambda t: tv[t]) for k, tv in title_votes.items()}

    summ = summary_candidates(base / "results-csv" / "2026-primary-summary.csv")
    # match each accumulated contest to a summary contest by its candidate-total
    # MULTISET (the vote data), not by the unreliable SOVC title. Names then come
    # from the summary; the match is exact so it doubles as validation.
    sig_index: dict[tuple[int, ...], list[str]] = defaultdict(list)
    for cname, cand in summ.items():
        sig_index[tuple(sorted(cand.values()))].append(cname)

    rows: list[dict[str, str]] = []
    resolved = unresolved = 0
    used_summary: set[str] = set()
    for ckey, entries in contests.items():
        title = disp_title.get(ckey, "")
        cand_labels = []
        for _c, _n, pairs in entries:
            for lab, _v in pairs:
                if lab.lower() not in TALLY_LABELS and lab and lab not in cand_labels:
                    cand_labels.append(lab)
        colsum: dict[str, int] = defaultdict(int)
        for _c, _n, pairs in entries:
            for lab, v in pairs:
                if lab in cand_labels:
                    colsum[lab] += v
        sig = tuple(sorted(colsum.values()))
        candidates = [c for c in sig_index.get(sig, []) if c not in used_summary]
        contest_name, name_of = title, {}
        match = None
        if len(candidates) == 1:  # unique data match
            match = candidates[0]
        elif len(candidates) > 1:  # collision -> break the tie by title-token overlap
            tt = set(title.lower().split())
            ranked = sorted(
                candidates, key=lambda c: len(tt & set(c.lower().split())), reverse=True
            )
            if len(tt & set(ranked[0].lower().split())) > 0:
                match = ranked[0]
        if match is not None:  # resolve candidate names from the summary
            contest_name = match
            used_summary.add(contest_name)
            smap = dict(summ[contest_name])
            taken: set[str] = set()
            for lab in cand_labels:
                m = next((n for n, t in smap.items() if t == colsum[lab] and n not in taken), None)
                if m:
                    name_of[lab] = m
                    taken.add(m)
            resolved += 1
        else:
            unresolved += 1
        for code, name, pairs in entries:
            for lab, v in pairs:
                is_tally = lab.lower() in TALLY_LABELS
                rows.append(
                    {
                        "election": "2026 Primary Election",
                        "election_date": "2026-05-05",
                        "precinct_code": code,
                        "precinct_name": name,
                        "contest": contest_name,
                        "contest_resolved": "yes" if match is not None else "no",
                        "choice": name_of.get(lab, lab),
                        "choice_raw": lab,
                        "votes": str(v),
                        "row_type": "tally" if is_tally else "choice",
                        "name_resolved": "" if is_tally else ("yes" if lab in name_of else "no"),
                    }
                )

    out = base / "precincts-csv" / "2026-primary-precincts.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "election",
        "election_date",
        "precinct_code",
        "precinct_name",
        "contest",
        "contest_resolved",
        "choice",
        "choice_raw",
        "votes",
        "row_type",
        "name_resolved",
    ]
    with out.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)
    precincts = len({r["precinct_code"] for r in rows})
    print(
        f"2026 Primary SOVC: {len(rows)} rows, {precincts} precincts, "
        f"{len(contests)} contests -> {out.relative_to(base)}"
    )
    print(
        f"   matched to summary by candidate-total multiset: {resolved} contests resolved "
        f"(clean names, exact reconciliation), {unresolved} unresolved "
        "(central-committee / fragmented — raw labels retained, flagged)"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
