from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import typer
import yaml
from rich.table import Table

from bosc.cli._base import console, get_settings, leads_app
from bosc.site import leads as leads_mod
from bosc.site.gh_leads import GithubLeadsError, fetch_site_issues, issue_to_lead, merge_leads
from bosc.sites import site_scoped_path


@leads_app.command("sync")
def leads_sync(
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        help="Show what would change without writing leads.yaml.",
    ),
    fixture: str | None = typer.Option(
        None,
        "--fixture",
        help="Path to a local JSON file (GitHub issues array) to use instead of the live API.",
    ),
) -> None:
    """Pull open GitHub issues tagged area:evidence + site:<slug> into leads.yaml.

    Issues with ``lead:kind:*`` and ``lead:status:*`` labels are mapped to
    :class:`~bosc.site.feeds.LeadItem`s and merged with any hand-curated entries
    (those with no ``issue`` field) that are preserved verbatim.
    """
    settings = get_settings()
    slug = settings.site
    store_path = site_scoped_path(settings.data_dir / "site" / "leads.yaml", slug, is_dir=False)

    existing = leads_mod.export_leads(store_path)

    if fixture:
        raw: list[dict[str, Any]] = json.loads(Path(fixture).read_text(encoding="utf-8"))
        from bosc.site.gh_leads import GithubIssue, _extract_labels

        gh_raw = [
            GithubIssue(
                number=item["number"],
                title=item["title"],
                body=item.get("body") or "",
                labels=_extract_labels(item.get("labels", [])),
                state=item["state"],
                html_url=item["html_url"],
            )
            for item in raw
        ]
    else:
        try:
            gh_raw = fetch_site_issues(slug, settings=settings)
        except GithubLeadsError as exc:
            console.print(f"[red]Error fetching GitHub issues:[/] {exc}")
            raise typer.Exit(1) from exc

    gh_items = [item for issue in gh_raw if (item := issue_to_lead(issue)) is not None]
    skipped = len(gh_raw) - len(gh_items)
    if skipped:
        console.print(f"[yellow]Skipped {skipped} issue(s) with missing/ambiguous labels.[/]")

    merged = merge_leads(gh_items, existing)

    existing_gh_ids = {item.issue for item in existing if item.issue is not None}
    new_gh_ids = {item.issue for item in gh_items}
    n_preserved = sum(1 for item in existing if item.issue is None)
    n_added = len(new_gh_ids - existing_gh_ids)
    n_removed = len(existing_gh_ids - new_gh_ids)
    n_updated = len(existing_gh_ids & new_gh_ids)

    table = Table("metric", "count")
    table.add_row("hand-curated (preserved)", str(n_preserved))
    table.add_row("GH-backed added/updated", str(n_added + n_updated))
    table.add_row("GH-backed removed (closed)", str(n_removed))
    table.add_row("total after merge", str(len(merged)))
    console.print(table)

    if dry_run:
        console.print("[dim]--dry-run: leads.yaml not written.[/]")
        return

    store_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {"leads": [item.model_dump(exclude_none=True) for item in merged]}
    store_path.write_text(
        yaml.safe_dump(payload, sort_keys=False, allow_unicode=True, width=100),
        encoding="utf-8",
    )
    console.print(f"[green]Wrote[/] {store_path} ({len(merged)} leads)")
