"""Flatten Electionware "Precinct Results" PDFs (Allen County BOE) -> tidy CSV.

Reads the pdftotext -layout dumps of the per-precinct reports and emits one row per
(election, precinct, contest, choice) with the printed vote count (and VOTE %, when
the report prints it). This is the precinct-level long form of the countywide
summary; summed across precincts it reconciles to the summary totals (see
validate()).

NOTHING is computed or inferred: every number is copied verbatim from the PDF text
layer. The contest title is taken as the line(s) immediately preceding each
"Vote For N" marker, which distinguishes a contest ("For Mayor", "State Issue 1",
"Proposed Tax Levy ...") from the For/Against *choices* inside a levy. Write-in
labels that wrap across lines are stitched best-effort; their vote counts (almost
always 0 at precinct level) are still captured exactly. See README for caveats.
"""

from __future__ import annotations

import csv
import re
import sys
from pathlib import Path

# a data row ends in an integer vote count, optionally followed by a percentage
ROW = re.compile(r"^(?P<label>.*?\S)\s{2,}(?P<votes>-?[\d,]+)(?:\s+(?P<pct>-?[\d.]+%))?\s*$")
PRECINCT = re.compile(r"^(?P<code>\d{4})\s+(?P<name>[A-Za-z].*?)\s*$")
VOTE_FOR = re.compile(r"^\s*Vote For\s+\d+", re.I)
FURNITURE = re.compile(
    r"OFFICIAL RESULTS|OFFICIAL PRECINCT SUMMARY|Precinct Results Report|"
    r"Precinct Summary|Summary Results Report|Allen County|Page \d+ of|"
    r"^\s*\d{4} (General|Primary) Election|^\s*(November|May) \d|^\s*TOTAL( VOTE %)?\s*$|"
    r"^\s*VOTE %\s*$|Registered\s*$|Voter Turnout -\s*$|Ballots Cast -\s*$|Voters - Total"
)
# rows that are tallies/markers rather than a ballot choice (kept, but flagged)
NONCHOICE = {
    "Total Votes",
    "Total Votes Cast",
    "Write-In Totals",
    "Not Assigned",
    "Overvotes",
    "Undervotes",
    "Contest Totals",
}


def clean(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def parse(txt_path: Path, election: str, date: str) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    precinct_code = precinct_name = ""
    contest = ""
    title_buf: list[str] = []  # non-furniture lines since the last blank (-> contest title)
    pending_label = ""  # a wrapped choice label awaiting its value line

    for raw in txt_path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw.rstrip()
        s = line.strip()

        if not s:
            title_buf = []
            pending_label = ""
            continue
        if FURNITURE.search(line):
            continue

        mp = PRECINCT.match(line)
        if mp and not ROW.match(line):  # a precinct header, not a data row
            precinct_code = mp.group("code")
            precinct_name = clean(mp.group("name"))
            contest = ""
            title_buf = []
            pending_label = ""
            continue

        if s.upper() == "STATISTICS":
            contest = "STATISTICS"
            title_buf = []
            continue

        if VOTE_FOR.match(line):
            if title_buf:
                contest = clean(" ".join(title_buf))
            title_buf = []
            pending_label = ""
            continue

        m = ROW.match(line)
        if m:
            label = clean(m.group("label")) or pending_label
            pending_label = ""
            title_buf = []
            if not contest or not label:
                continue
            rows.append(
                {
                    "election": election,
                    "election_date": date,
                    "precinct_code": precinct_code,
                    "precinct_name": precinct_name,
                    "contest": contest,
                    "choice": label,
                    "votes": m.group("votes").replace(",", ""),
                    "vote_pct": m.group("pct") or "",
                    "row_type": "tally" if label in NONCHOICE else "choice",
                }
            )
            continue

        # non-furniture, non-data line: a contest-title fragment and/or a wrapped label
        title_buf.append(s)
        pending_label = clean((pending_label + " " + s).strip())

    return rows


FIELDS = [
    "election",
    "election_date",
    "precinct_code",
    "precinct_name",
    "contest",
    "choice",
    "votes",
    "vote_pct",
    "row_type",
]


def write_csv(rows: list[dict[str, str]], out: Path) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rows)


def validate(rows: list[dict[str, str]], summary_csv: Path) -> list[str]:
    """Cross-check: precinct vote sums per (contest, choice) vs the countywide summary.

    Returns a list of human-readable mismatch lines (empty == fully reconciles on
    the choices both files share).
    """
    from collections import defaultdict

    psum: dict[tuple[str, str], int] = defaultdict(int)
    for r in rows:
        if r["row_type"] == "choice":
            psum[(r["contest"], r["choice"])] += int(r["votes"])

    issues: list[str] = []
    if not summary_csv.is_file():
        return [f"(no summary to validate against: {summary_csv})"]
    with summary_csv.open(encoding="utf-8") as fh:
        checked = matched = 0
        for srow in csv.DictReader(fh):
            key = (clean(srow.get("contest", "")), clean(srow.get("choice", "")))
            stotal = srow.get("total", "").replace(",", "")
            if key not in psum or not stotal.isdigit():
                continue
            checked += 1
            if psum[key] == int(stotal):
                matched += 1
            else:
                issues.append(f"  {key[0]} / {key[1]}: precincts={psum[key]} summary={stotal}")
    issues.insert(0, f"reconciled {matched}/{checked} shared (contest, choice) totals")
    return issues


JOBS = [
    (
        "txt/2024_GEN_PRECINCT.txt",
        "2024 General Election",
        "2024-11-05",
        "results-csv/2024-general-summary.csv",
        "precincts-csv/2024-general-precincts.csv",
    ),
    (
        "txt/G2019_PRECINCT.txt",
        "2019 General Election",
        "2019-11-05",
        "results-csv/2019-general-summary.csv",
        "precincts-csv/2019-general-precincts.csv",
    ),
]


def main() -> int:
    base = Path(__file__).parent
    cache = base.parent.parent / "cache" / "allen-boe"  # data/cache/allen-boe (gitignored)
    rc = 0
    for txt, election, date, summary_rel, out_rel in JOBS:
        src = cache / txt
        if not src.is_file():
            print(f"!! missing {src} (regenerate with pdftotext -layout)")
            rc = 1
            continue
        rows = parse(src, election, date)
        write_csv(rows, base / out_rel)
        n_choice = sum(1 for r in rows if r["row_type"] == "choice")
        precincts = len({r["precinct_code"] for r in rows})
        contests = len({r["contest"] for r in rows})
        print(
            f"{election}: {len(rows)} rows ({n_choice} choices, {precincts} precincts, "
            f"{contests} contests) -> {out_rel}"
        )
        for line in validate(rows, base / summary_rel):
            print("   " + line)
    return rc


if __name__ == "__main__":
    sys.exit(main())
