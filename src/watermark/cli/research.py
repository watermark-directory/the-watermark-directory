from __future__ import annotations

import asyncio
from pathlib import Path

import typer
from rich.table import Table

from watermark.cli._base import (
    console,
    get_settings,
    research_app,
)


@research_app.command("run")
def research_run_cmd(
    topic: str = typer.Option("", "--topic", "-t", help="The investigation topic / question."),
    recipe: str = typer.Option(
        "issue-proposal",
        "--recipe",
        help="Research-agent recipe: issue-proposal | hypothesis-assessment | site-onboard.",
    ),
    hypothesis: str = typer.Option(
        "", "--hypothesis", help="Hypothesis id (required for the hypothesis-assessment recipe)."
    ),
    out: str = typer.Option("", "--out", help="Output dir (default: data/research/<slug>)."),
    max_turns: int = typer.Option(0, "--max-turns", help="Agent turn cap (0 = settings default)."),
    max_proposals: int = typer.Option(
        -1, "--max-proposals", help="Issue proposals to distill (-1 = settings default)."
    ),
    no_tools: bool = typer.Option(False, "--no-tools", help="Disable the BOSC data tools."),
) -> None:
    """Investigate over the corpus (read-only) and write findings + the recipe's output under
    data/research/. The default recipe distills issue proposals; --recipe hypothesis-assessment
    --hypothesis <id> assesses the active --site against a boom-origin hypothesis (candidate
    cells, for review). Never mutates source bytes."""
    from datetime import UTC, datetime

    from watermark.hypotheses import HYPOTHESES
    from watermark.research import RECIPES, run_research, run_slug, write_run

    settings = get_settings()
    if recipe not in RECIPES:
        raise typer.BadParameter(
            f"unknown recipe {recipe!r}; known: {sorted(RECIPES)}", param_hint="--recipe"
        )
    context: dict[str, str] = {}
    if recipe == "hypothesis-assessment":
        if hypothesis not in HYPOTHESES:
            raise typer.BadParameter(
                f"--hypothesis must be one of {sorted(HYPOTHESES)}", param_hint="--hypothesis"
            )
        context = {"hypothesis": hypothesis, "site": settings.site}
        if not topic:
            topic = f"assess {settings.site} x {hypothesis}"
    elif recipe == "site-onboard":
        context = {"site": settings.site}
        if not topic:
            topic = f"onboard {settings.site}"
    elif not topic:
        raise typer.BadParameter("the issue-proposal recipe needs --topic", param_hint="--topic")

    generated_at = datetime.now(UTC).isoformat(timespec="seconds")
    turns = max_turns or settings.research_max_turns
    n = max_proposals if max_proposals >= 0 else settings.research_max_proposals

    def emit(chunk: str) -> None:
        console.print(chunk, end="", markup=False, highlight=False)

    manifest = asyncio.run(
        run_research(
            topic,
            generated_at=generated_at,
            settings=settings,
            max_turns=turns,
            max_proposals=n,
            enable_tools=not no_tools,
            on_text=emit,
            recipe=RECIPES[recipe],
            context=context,
        )
    )
    console.print()  # newline after the streamed findings

    out_dir = Path(out) if out else settings.research_dir / run_slug(topic, generated_at)
    write_run(manifest, out_dir, settings=settings)

    console.print(f"\n[bold]Research run →[/] {out_dir}")
    prov = manifest.provenance
    footer: list[str] = []
    if prov.tools_used:
        footer.append("tools: " + ", ".join(prov.tools_used))
    if prov.num_turns:
        footer.append(f"{prov.num_turns} turns")
    if prov.cost_usd is not None:
        footer.append(f"${prov.cost_usd:.4f}")
    if footer:
        console.print(f"[dim]({' · '.join(footer)})[/]")

    if manifest.assessments:
        table = Table("site x hypothesis", "signal", "tag", "group", "cites")
        for a in manifest.assessments:
            table.add_row(
                f"{a.site} x {a.hypothesis}",
                a.signal or "—",
                a.tag,
                a.group or "—",
                str(len(a.citations)),
            )
        console.print(table)
        console.print(
            f"[dim]candidate cells under {out_dir}/assessments/ — review, then promote into "
            "data/hypotheses/ by hand (bosc hypotheses check before committing).[/]"
        )
    elif manifest.proposals:
        table = Table("proposed issue", "labels", "dedupe key")
        for pr in manifest.proposals:
            table.add_row(pr.title, ", ".join(pr.labels), pr.dedupe_key)
        console.print(table)
    else:
        console.print("[yellow]No issue proposals or assessment cells produced.[/]")

    if prov.is_error:
        raise typer.Exit(code=1)


@research_app.command("publish")
def research_publish_cmd(
    run: str = typer.Option(..., "--run", help="Run directory (contains manifest.yaml)."),
    existing: str = typer.Option(
        "",
        "--existing",
        help="JSON file of existing issues (gh issue list --json number,title,body).",
    ),
    out: str = typer.Option(
        "", "--out", help="Write the publish plan JSON here (default: <run>/publish-plan.json)."
    ),
    create_issues: bool = typer.Option(
        False,
        "--create-issues",
        help="Open each planned issue on GitHub via gh. Pass --existing to dedupe first.",
    ),
) -> None:
    """Build a publish plan from a research run: dedupe its proposals against existing
    issues and render the PR body. Add --create-issues to also open them on GitHub."""
    import json
    import subprocess
    from typing import Any

    from watermark.research import build_plan, load_manifest

    run_dir = Path(run)
    manifest = load_manifest(run_dir)
    issues: list[dict[str, Any]] = []
    if existing:
        loaded = json.loads(Path(existing).read_text(encoding="utf-8"))
        issues = loaded if isinstance(loaded, list) else []
    plan = build_plan(manifest, existing=issues, run_ref=run_dir.as_posix())
    out_path = Path(out) if out else run_dir / "publish-plan.json"
    out_path.write_text(json.dumps(plan.model_dump(), indent=2) + "\n", encoding="utf-8")
    console.print(
        f"[bold]Publish plan →[/] {out_path}  "
        f"({len(plan.issues)} to open, {len(plan.duplicates)} skipped)"
    )

    if create_issues:
        if not plan.issues:
            console.print("[yellow]No issues to open (all deduped or none proposed).[/]")
            return
        console.print()
        for iss in plan.issues:
            cmd = ["gh", "issue", "create", "--title", iss.title, "--body", iss.body]
            for label in iss.labels:
                cmd += ["--label", label]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            url = result.stdout.strip()
            console.print(f"  [green]opened[/] {url}")
