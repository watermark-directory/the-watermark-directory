from __future__ import annotations

import typer
from rich.table import Table

from bosc.cli._base import (
    SITES,
    console,
    sites_app,
)


@sites_app.command("list")
def sites_list() -> None:
    """List the registered site profiles (bosc.sites.SITES)."""
    table = Table("slug", "place", "basin")
    for slug, prof in SITES.items():
        table.add_row(slug, prof.place, prof.basin)
    console.print(table)


@sites_app.command("show")
def sites_show(
    slug: str = typer.Argument(..., help="Site slug to display."),
) -> None:
    """Print a site's resolved SiteProfile."""
    if slug not in SITES:
        raise typer.BadParameter(
            f"unknown site {slug!r}; known: {sorted(SITES)}", param_hint="slug"
        )
    prof = SITES[slug]
    table = Table("field", "value")
    for name in type(prof).model_fields:
        table.add_row(name, str(getattr(prof, name)))
    console.print(table)

    from bosc.catalog_sites import readiness

    r = readiness(slug)
    ready = "[green]ready[/]" if r.ready else f"[yellow]{len(r.missing)} missing[/]"
    console.print(
        f"\n[bold]Catalog readiness[/] — {r.present}/{r.total} datasets present · {ready}"
    )
    if r.missing:
        console.print(f"  [dim]missing:[/] {', '.join(r.missing)}")
    if r.stale:
        console.print(f"  [dim]stale:[/] {', '.join(r.stale)}")
    console.print(
        "  [dim](datasets derived from the catalog's per-site axis — `bosc catalog "
        f"list --site {slug}`)[/]"
    )


@sites_app.command("new")
def sites_new(
    slug: str = typer.Argument(..., help="New site slug (kebab-case)."),
    basin: str = typer.Option("maumee", "--basin", help="Basin slug (default: maumee)."),
) -> None:
    """Print a paste-ready SiteProfile stub for a new site (output relpaths pre-slug-scoped)."""
    from bosc.sites import scaffold_profile_src

    if slug in SITES:
        raise typer.BadParameter(f"site {slug!r} is already registered", param_hint="slug")
    # soft_wrap so the paste-ready stub isn't re-wrapped to the terminal width.
    console.print(
        scaffold_profile_src(slug, basin=basin), markup=False, highlight=False, soft_wrap=True
    )
