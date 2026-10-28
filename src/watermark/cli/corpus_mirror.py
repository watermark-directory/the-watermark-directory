"""``watermark corpus-mirror`` — project the BOSC corpus into yidam node format (#1561/#1562).

A thin wrapper over :func:`watermark.site.corpus_mirror.regenerate_mirror`: load the active
site's corpus and project it into ``.yidam/corpus/`` as yidam nodes. When the real ``yidam``
binary is installed it then runs ``graph-check`` and ``lint`` over what was written and, by
default, fails loudly if the graph gate is dirty. Per-site via ``--site``.

The reports come from the binary, not from Python — see :mod:`watermark.site.yidam_cli` for why
the replica was retired. Install it with ``mise run yidam-build``; without it the projection
still runs and simply reports nothing.
"""

from __future__ import annotations

from pathlib import Path

import typer

from watermark.cli._base import app, console, get_settings


@app.command("corpus-mirror")
def corpus_mirror(
    out: str | None = typer.Option(
        None,
        "--out",
        help="Corpus dir to write (default: <repo-root>/.yidam/corpus, what the yidam CLI reads).",
    ),
    check: bool = typer.Option(
        True,
        "--check/--no-check",
        help="Run the yidam reports after writing and fail on a dirty graph-check "
        "(needs the yidam binary; `mise run yidam-build`).",
    ),
    index: bool = typer.Option(
        False,
        "--index/--no-index",
        help="Also build the LanceDB vector index over the mirror (.yidam/index; yidam "
        "embed + index-build). Off by default — downloads the ~80 MB embedding model on "
        "first run and is rebuilt lazily by `yidam serve --mcp` regardless.",
    ),
    exports: bool = typer.Option(
        False,
        "--exports/--no-exports",
        help="Also render the downloadable graph exports (RDF Turtle + JSON-LD, GraphML) of the "
        "mirror into .yidam/exports/ (yidam export rdf|graphml). `watermark export` writes these "
        "into the bundle's exports/ automatically; this is the standalone inspection path.",
    ),
) -> None:
    """Project the corpus (entities, relationships, concepts, people, leads, hypotheses,
    [open] claims) into yidam corpus nodes under .yidam/corpus/ for the active site.

    The mirror is the bridge that lets ``yidam corpus-index`` / ``graph-check`` / ``serve --mcp``
    and the vector index read BOSC's corpus (Epic #1560). It's a git-ignored, regenerable
    artifact — re-run any time (`watermark --site <slug> corpus-mirror`), and every
    ``watermark export`` refreshes it; the committed corpus stays the source of truth. Every
    node is site-tagged and emits ≥1 outgoing link (the yidam graph rule); claim tags
    ([verified]/[inference]/[reference]/[open]) are preserved.
    """
    from watermark.site.corpus_mirror import default_corpus_dir, regenerate_mirror

    settings = get_settings()
    corpus_dir = Path(out) if out else default_corpus_dir(settings)

    regen = regenerate_mirror(settings, corpus_dir=corpus_dir, check=check)
    mirror = regen.mirror

    by_class = ", ".join(f"{cls} {n}" for cls, n in mirror.counts_by_class().items())
    console.print(
        f"[green]Mirrored[/] {settings.site} → {corpus_dir} — "
        f"{len(mirror.nodes)} nodes across {len(mirror.classes)} classes ([dim]{by_class}[/])."
    )
    if check and not regen.checked:
        console.print(
            "[yellow]reports skipped[/] — no usable yidam binary (absent, or too old to "
            "speak `--format json`). [dim]`mise run yidam-build` installs the pinned one "
            "(light build, ~20s); CI gates on it regardless.[/]"
        )
    elif regen.graph_check is not None:
        console.print(
            f"[dim]  {regen.graph_check.build.version}"
            f"@{regen.graph_check.build.commit} — {regen.graph_check.summary()}[/]"
        )
        if regen.lint is not None:
            regressions = regen.lint.regressions
            style = "yellow" if regressions else "dim"
            console.print(f"[{style}]  {regen.lint.summary()}[/]")
            for v in regressions[:10]:
                console.print(f"    [yellow]{v.node}[/] — {v.detail}")
            if len(regressions) > 10:
                console.print(f"    [dim]… and {len(regressions) - 10} more[/]")
        if not regen.graph_check.passed:
            for node, problems in regen.graph_check.nodes_with_issues:
                console.print(f"  [red]{node}[/]")
                for problem in problems:
                    console.print(f"    - {problem}")
            raise typer.Exit(code=1)
        console.print(f"[green]graph-check clean[/] — {len(mirror.nodes)} instances.")

    if exports:
        from watermark.site.graph_exports import (
            default_exports_dir,
            resolve_provenance,
            write_exports,
        )

        exports_dir = default_exports_dir(settings)
        written = write_exports(mirror, exports_dir, resolve_provenance(settings))
        listed = ", ".join(f"{e.fmt} → {e.filename}" for e in written)
        console.print(
            f"[green]Exported[/] the graph → {exports_dir} "
            f"[dim]({written[0].node_count} nodes / {written[0].edge_count} edges; {listed})[/]"
        )

    if index:
        from watermark.site.yidam_index import build_yidam_index

        console.print("[dim]  embedding nodes → LanceDB vector index (all-MiniLM-L6-v2)…[/]")
        built = build_yidam_index(settings, mirror=mirror)
        console.print(
            f"[green]Indexed[/] {built.nodes} nodes ({built.dimension}-dim) → {built.index_dir} "
            f"[dim](reconciled with the /ask embeddings; queryable via yidam serve --mcp)[/]"
        )


@app.command("corpus-peers")
def corpus_peers(
    workdir: str | None = typer.Option(
        None,
        "--workdir",
        help="Where each site's throwaway corpus root is projected, one subdir per site "
        "(default: a fresh temp dir). Must sit OUTSIDE the repository: the binary resolves its "
        "root upward and would report on the repository's own mirror instead.",
    ),
) -> None:
    """Run the yidam reports over every registered site's mirror and fail on a regression.

    The CI ``corpus`` job gates the reference build in the repo root. This holds each peer to
    a clean ``graph-check`` and zero error-severity lint findings, and every site to its
    enumerated ``verified-unsourced`` gaps (#2137). See :mod:`watermark.site.corpus_peers`.
    """
    from watermark.site import yidam_cli
    from watermark.site.corpus_peers import check_sites

    if not yidam_cli.usable():
        console.print(
            "[red]no usable yidam binary[/] — `mise run yidam-build` installs the pinned one."
        )
        raise typer.Exit(code=1)

    import tempfile

    base = Path(workdir) if workdir else Path(tempfile.mkdtemp(prefix="watermark-corpus-peers-"))
    verdicts = check_sites(base, base=get_settings())
    for v in verdicts:
        mark = "[green]ok[/]" if v.passed else "[red]FAIL[/]"
        console.print(f"{mark} {v.site} — {v.graph_check.summary()}")
        if not v.graph_check.passed:
            for node, problems in v.graph_check.nodes_with_issues:
                console.print(f"    [red]{node}[/] — {'; '.join(problems)}")
        for err in v.errors:
            console.print(f"    [red]error[/] {err.node} — {err.detail}")
        for node in v.unexpected_unsourced:
            console.print(
                f"    [red]verified-unsourced[/] {node} — a `\\[verified]` claim citing no "
                "registered source; cite it or demote it (the author's call)"
            )
        for node in v.stale_known:
            console.print(
                f"    [red]stale known gap[/] {node} — no longer fires; remove it from "
                "corpus_peers.KNOWN_UNSOURCED"
            )
    if not all(v.passed for v in verdicts):
        raise typer.Exit(code=1)
