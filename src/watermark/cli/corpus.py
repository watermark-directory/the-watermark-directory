"""``watermark corpus staleness`` — report which registers and watches have aged out (#2069 lesson).

A **report, not a gate**: it prints and, once its arguments validate, exits 0 whatever it finds — the
``mise run yidam-vendor-status`` precedent ("reports drift — a report, never a gate"). A bad
``--kind`` still raises ``typer.BadParameter`` like any other misuse; that is an invocation error,
not a finding. The reduction lives in :mod:`watermark.staleness`; this module only renders it.
"""

from __future__ import annotations

import json

import typer
from rich.table import Table

from watermark.cli._base import console, corpus_app, get_settings

_STANDING_STYLE = {
    "overdue": "bold red",
    "unknown": "bold yellow",
    "uncheckable": "dim cyan",
    "current": "green",
}


@corpus_app.command("staleness")
def corpus_staleness(
    kind: str = typer.Option(
        "",
        "--kind",
        help="Limit to one subject kind: register | watch. Default: both.",
    ),
    as_json: bool = typer.Option(
        False, "--json", help="Emit the whole report as JSON instead of tables."
    ),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Print every subject, including the current ones."
    ),
) -> None:
    """Which data-center registers and standing watches are past their declared cadence.

    Measures every subject on three **independently authored** axes — the date it claims for
    itself, the last commit touching its path, and a cadence declared somewhere else (the catalog
    entry for a register, a dated trigger for a watch) — because a check that parsed the register's
    own status line and compared it to nothing would only confirm that the file says what it says.

    Nothing unknowable is reported as fresh. A register with no catalog entry, a date that cannot be
    parsed, a cadence written in English, a watch with no top-level dated trigger: each reports
    **unknown**. ``on-demand`` and ``static`` report **uncheckable** and get their own section —
    a cadence that can never be overdue is a finding, not a pass.

    Exits 0 whatever it finds — it is a report. (An unsupported ``--kind`` is still rejected as a
    bad argument; that is misuse, not a finding.)
    """
    from watermark.staleness import build_report

    settings = get_settings()
    report = build_report(settings=settings)

    subjects = report.subjects
    if kind:
        if kind not in {"register", "watch"}:
            raise typer.BadParameter("--kind must be 'register' or 'watch'")
        subjects = [s for s in subjects if s.kind == kind]

    if as_json:
        print(
            json.dumps(
                {
                    "asof": report.asof.isoformat(),
                    "subjects": [s.model_dump(mode="json") for s in subjects],
                },
                indent=2,
            )
        )
        return

    console.print(f"[bold]corpus staleness[/] — as of {report.asof.isoformat()}\n")

    for order, heading in (
        ("overdue", "OVERDUE — past a declared cadence"),
        ("unknown", "UNKNOWN — nothing can say whether these are stale"),
    ):
        rows = [s for s in subjects if s.standing == order]
        if not rows:
            console.print(f"[green]none {order}[/]\n")
            continue
        table = Table(title=f"{heading}  ({len(rows)})", title_style=_STANDING_STYLE[order])
        table.add_column("kind")
        table.add_column("subject")
        table.add_column("age", justify="right")
        table.add_column("why")
        for s in sorted(rows, key=lambda s: (-(s.age_days or 0), s.relpath)):
            table.add_row(
                s.kind,
                s.relpath,
                f"{s.age_days}d" if s.age_days is not None else "—",
                "\n".join(f"· {r}" for r in s.reasons) or "—",
            )
        console.print(table)
        console.print()

    catalogless = [s for s in report.catalogless_registers if s in subjects]
    if catalogless:
        table = Table(
            title=f"REGISTERS WITH NO CATALOG ENTRY OF THEIR OWN  ({len(catalogless)})",
            title_style="bold yellow",
        )
        table.add_column("register")
        table.add_column("covered by")
        for s in sorted(catalogless, key=lambda s: s.relpath):
            table.add_row(
                s.relpath,
                f"template {s.catalog_id!r}" if s.catalog_id else "[bold red]nothing[/]",
            )
        console.print(table)
        console.print(
            "[dim]A slug-scoped template entry nominally matches these paths and shares one\n"
            "`last_refreshed` across every site it covers, so it cannot answer for any of them.[/]\n"
        )

    unchk = [s for s in report.uncheckable if s in subjects]
    if unchk:
        cadences = sorted({s.cadence or "?" for s in unchk})
        console.print(
            f"[cyan]UNCHECKABLE BY DECLARATION[/] — {len(unchk)} subject(s) declare "
            f"{', '.join(repr(c) for c in cadences)}, which can never be overdue.\n"
            "[dim]Either that is a deliberate terminal state, or these need real cadences. It is\n"
            "not a passing check and this report will not present it as one.[/]\n"
        )
        for s in sorted(unchk, key=lambda s: s.relpath):
            console.print(f"  [dim]{s.cadence:<10}[/] {s.relpath}")
        console.print()

    divergent = [s for s in report.divergent if s in subjects]
    if divergent:
        console.print("[yellow]STATED DATE BEHIND ITS OWN FILE[/] [dim](advisory)[/]")
        for s in divergent:
            console.print(f"  {s.relpath}\n    [dim]{s.divergence}[/]")
        console.print()

    if verbose:
        current = [s for s in subjects if s.standing == "current"]
        console.print(f"[green]CURRENT[/] ({len(current)})")
        for s in sorted(current, key=lambda s: s.relpath):
            console.print(f"  [dim]{s.age_days}d[/] {s.relpath}")
        console.print()

    counts = {k: len([s for s in subjects if s.standing == k]) for k in _STANDING_STYLE}
    console.print(
        "  ".join(f"[{_STANDING_STYLE[k]}]{k} {v}[/]" for k, v in counts.items())
        + f"   of {len(subjects)} subject(s)"
    )
    console.print("[dim]A report, not a gate — findings never change this command's exit code.[/]")
