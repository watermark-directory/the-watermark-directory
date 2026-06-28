"""``watermark index`` — build or rebuild the LanceDB corpus retrieval store (#808)."""

from __future__ import annotations

from typing import Annotated

import typer

from watermark.cli._base import app, console, get_settings
from watermark.sites import SITES


@app.command("index")
def index_cmd(
    site: Annotated[
        str,
        typer.Option(
            "--site",
            help="Limit rebuild to one site slug (replaces that site's chunks only).",
        ),
    ] = "",
    collection: Annotated[
        str,
        typer.Option("--collection", help="Further filter to one collection name."),
    ] = "",
    no_documents: Annotated[
        bool, typer.Option("--no-documents", help="Skip source document indexing.")
    ] = False,
    no_reference: Annotated[
        bool, typer.Option("--no-reference", help="Skip reference data indexing.")
    ] = False,
    no_extracted: Annotated[
        bool, typer.Option("--no-extracted", help="Skip extracted YAML indexing.")
    ] = False,
) -> None:
    """Build or rebuild the LanceDB corpus retrieval store (data/cache/lancedb/).

    A full run (no flags) drops and recreates the index across all sites and content
    kinds. Use ``--site`` to replace one site's chunks without touching others.
    """
    from watermark.retrieval.embeddings import get_provider
    from watermark.retrieval.ingestion import (
        iter_document_chunks,
        iter_extracted_chunks,
        iter_reference_chunks,
    )
    from watermark.retrieval.store import Chunk, CorpusStore

    settings = get_settings()
    provider = get_provider(settings)
    store = CorpusStore(settings.lancedb_dir, provider)

    site_scope = site or ""
    site_list = [site_scope] if site_scope else list(SITES.keys())

    chunks: list[Chunk] = []

    if not no_documents:
        console.print("[dim]Indexing source documents…[/dim]")
        chunks.extend(iter_document_chunks(settings.documents_dir))

    if not no_reference:
        console.print("[dim]Indexing reference data…[/dim]")
        chunks.extend(iter_reference_chunks(settings.reference_dir))

    if not no_extracted:
        for slug in site_list:
            console.print(f"[dim]Indexing extracted artifacts for {slug!r}…[/dim]")
            chunks.extend(iter_extracted_chunks(settings.extracted_dir, site=slug))

    if collection:
        before = len(chunks)
        chunks = [c for c in chunks if c.collection == collection]
        console.print(
            f"[dim]Filtered to collection {collection!r}: {len(chunks)}/{before} chunks[/dim]"
        )

    if not chunks:
        console.print("[yellow]No content found to index.[/yellow]")
        raise typer.Exit(1)

    console.print(f"Embedding and indexing [bold]{len(chunks):,}[/bold] chunks…")
    if site_scope:
        store.update_site(site_scope, chunks)
    else:
        store.rebuild(chunks)

    console.print(f"[green]Index built:[/green] {len(chunks):,} chunks → {settings.lancedb_dir}")
