"""In-process tools exposed to the research agent via an SDK MCP server.

Each tool is a thin, deterministic adapter over the pipeline so the agent can
inspect real data instead of guessing. Tools return the standard MCP content
shape (``{"content": [{"type": "text", "text": ...}]}``).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from claude_agent_sdk import create_sdk_mcp_server, tool

from watermark.config import get_settings
from watermark.models import Estimate, OPCSummary
from watermark.pipeline import analyze, ingest

SERVER_NAME = "watermark"


def _text(payload: str) -> dict[str, Any]:
    """Wrap a string in the MCP tool-result content shape."""
    return {"content": [{"type": "text", "text": payload}]}


# Read-side per-site resolution (#424). The extraction-reading tools resolve against the ACTIVE
# site's own committed corpus: the whole data/extracted/ tree for the corpus home (Lima), else the
# site's own subtree (data/extracted/<slug>/) — so a per-site run reads its own record, never
# another site's. The corpus + hydrology *reference* models (entities, timeline, the hydrology
# suite) are the Lima reference build; for another site they are NOT silently substituted — the
# tool returns an honest "no per-site X yet" notice (`_reference_only`). Resolving a non-home
# site's own entity/timeline/scenario equivalents is the remaining parity work this seam leaves.
_CORPUS_HOME = "lima"


def _is_corpus_home(settings: Any) -> bool:
    return bool(settings.site == _CORPUS_HOME)


def _site_extracted_root(settings: Any) -> Path:
    """The active site's extracted-corpus root: the whole tree for the corpus home, else the
    site's own subtree (data/extracted/<slug>/)."""
    root: Path = settings.extracted_dir
    return root if _is_corpus_home(settings) else root / str(settings.site)


def _site_scope_note(settings: Any) -> str:
    """A scope banner naming whose corpus a payload is (empty for the corpus home → zero drift)."""
    if _is_corpus_home(settings):
        return ""
    return (
        f"[scope] Reading site {settings.site!r}'s own committed corpus "
        f"(data/extracted/{settings.site}/).\n\n"
    )


def _scoped(payload: str) -> dict[str, Any]:
    """Wrap a data payload with the active-site scope note (empty for the corpus home, Lima)."""
    return _text(_site_scope_note(get_settings()) + payload)


def _reference_only(tool: str) -> dict[str, Any] | None:
    """Guard for the Lima-reference tools (entities/timeline/hydrology): off the corpus home they
    have no per-site equivalent yet, so return an honest notice instead of silently serving Lima's
    record (#424). Returns ``None`` on the corpus home (the caller proceeds normally)."""
    settings = get_settings()
    if _is_corpus_home(settings):
        return None
    return _text(
        f"[scope] No committed {tool} for site {settings.site!r} yet. This tool serves the "
        f"{_CORPUS_HOME!r} reference build, which is not substituted for another site (#424); "
        f"onboard {settings.site}'s corpus/scenario to populate it."
    )


def _resolve(filename: str | None, pattern: str = "*.yaml") -> Path | None:
    """Resolve an extraction within the ACTIVE SITE's extracted corpus (#424).

    The search root is the whole ``data/extracted`` tree for the corpus home (Lima), else the
    active site's own subtree. A ``filename`` may be a path relative to that root
    (``recorder/foo.yaml``) or a bare basename matched anywhere under it; with no filename, the
    first ``pattern`` match (recursive) is returned.
    """
    base = _site_extracted_root(get_settings())
    if not base.exists():
        return None
    if filename:
        direct = base / filename
        if direct.is_file():
            return direct
        name = Path(filename).name
        matches = sorted(p for p in base.rglob(name) if p.is_file())
        return matches[0] if matches else None
    matches = sorted(base.rglob(pattern))
    return matches[0] if matches else None


@tool("list_documents", "List ingested source documents and their collections.", {})
async def list_documents(_args: dict[str, Any]) -> dict[str, Any]:
    # The raw source corpus (data/documents/) is not partitioned per site; off the corpus home
    # there is no per-site document tree, so don't hand back the home's documents (#424).
    if (note := _reference_only("source documents")) is not None:
        return note
    docs = ingest.discover()
    if not docs:
        return _text("No source documents found under data/documents.")
    lines = [
        f"- {d.doc_id}  [{d.collection or 'root'}]  {d.path.name}  ({d.size_bytes / 1e6:.1f} MB)"
        for d in docs
    ]
    return _scoped("\n".join(lines))


@tool("list_extractions", "List available structured extraction files.", {})
async def list_extractions(_args: dict[str, Any]) -> dict[str, Any]:
    settings = get_settings()
    base = _site_extracted_root(settings)
    files = sorted(base.rglob("*.yaml")) if base.exists() else []
    if not files:
        loc = "data/extracted" if _is_corpus_home(settings) else f"data/extracted/{settings.site}"
        return _text(f"No extractions found under {loc}.")
    # Show the path relative to the site root so the agent sees provenance (recorder/...).
    return _scoped("\n".join(f"- {f.relative_to(base)}" for f in files))


@tool(
    "read_extraction",
    "Read the raw text of an extraction file under data/extracted by name or "
    "collection-relative path (e.g. 'recorder/202511180011830-amazon-deed.deed.yaml').",
    {"filename": str},
)
async def read_extraction(args: dict[str, Any]) -> dict[str, Any]:
    path = _resolve(args["filename"])
    if path is None:
        return _text(f"Not found: {args['filename']}")
    return _text(path.read_text(encoding="utf-8"))


@tool(
    "reconcile_summary",
    "Run deterministic arithmetic reconciliation over a *.summary.opc.yaml file.",
    {"filename": str},
)
async def reconcile_summary(args: dict[str, Any]) -> dict[str, Any]:
    path = _resolve(args["filename"])
    if path is None:
        return _text(f"Not found: {args['filename']}")
    summary = OPCSummary.from_yaml(path)
    findings = analyze.reconcile(summary)
    return _text("\n".join(str(f) for f in findings))


@tool(
    "program_overview",
    "Structured overview of the OPC program: per-estimate totals, section subtotals, "
    "and reconciliation status (reads the summary extraction).",
    {},
)
async def program_overview(_args: dict[str, Any]) -> dict[str, Any]:
    path = _resolve(None, "*.summary.opc.yaml")
    if path is None:
        return _text("No *.summary.opc.yaml extraction found under data/extracted.")
    summary = OPCSummary.from_yaml(path)
    findings = analyze.reconcile(summary)
    passed = sum(1 for f in findings if f.ok)
    lines = [
        f"Source: {path.name}",
        f"Program construction total: {summary.construction_total():,}",
        f"Program grand total: {summary.grand_total():,}",
        f"Reconciliation: {passed}/{len(findings)} checks pass.",
        "",
    ]
    for se in summary.sub_estimates:
        secs = {k: v for k, v in se.section_subtotals.model_dump().items() if v is not None}
        lines.append(f"## {se.name} (pdf_page {se.pdf_page})")
        lines.append(f"   construction_subtotal={se.construction_subtotal:,} total={se.total:,}")
        lines.append("   sections: " + ", ".join(f"{k}={v:,}" for k, v in secs.items()))
    return _scoped("\n".join(lines))


@tool(
    "timeline",
    "Cross-document chronology: dated events (deed recordings, NPDES public "
    "notices/comment deadlines, OPC estimates) from every extraction, in order.",
    {},
)
async def timeline(_args: dict[str, Any]) -> dict[str, Any]:
    if (note := _reference_only("timeline")) is not None:
        return note
    from watermark.pipeline import timeline as timeline_stage

    events = timeline_stage.build_timeline()
    if not events:
        return _text("No dated events found under data/extracted.")
    lines = []
    for e in events:
        date = e.date or "(undated)"
        corrob = f" (+{len(e.also_sources)} corroborating)" if e.also_sources else ""
        lines.append(f"{date}  [{e.category}]  {e.title}  <{e.source}>{corrob}")
        if e.detail:
            lines.append(f"            {e.detail}")
    return _scoped("\n".join(lines))


@tool(
    "entities",
    "Cross-document entity graph: parties resolved across deeds/NPDES (with kind, "
    "classification, roles, parcels) and the relationships between them.",
    {},
)
async def entities(_args: dict[str, Any]) -> dict[str, Any]:
    if (note := _reference_only("entities")) is not None:
        return note
    from watermark.pipeline import entities as entities_stage

    graph = entities_stage.build_entity_graph(
        enrich_parcels=True,
        enrich_lei=True,
        enrich_rsei=True,
        enrich_federal=True,
        enrich_subdivisions=True,
    )
    if not graph.entities:
        return _text("No entities found under data/extracted.")
    lines = ["ENTITIES:"]
    for ent in sorted(graph.entities.values(), key=lambda e: (e.kind, e.key)):
        roles = ", ".join(f"{r} x{n}" for r, n in ent.roles.most_common())
        sig = f" signals={sorted(ent.signals)}" if ent.signals else ""
        parcels = f" parcels={len(ent.parcels)}" if ent.parcels else ""
        lines.append(f"- {ent.display} [{ent.kind}/{ent.classification}] {roles}{parcels}{sig}")
    lines.append("\nRELATIONSHIPS:")
    for r in graph.relationships:
        src = graph.entities[r.src].display if r.src in graph.entities else r.src
        dst = graph.entities[r.dst].display if r.dst in graph.entities else r.dst
        when = f" ({r.date})" if r.date else ""
        ref = f" [{r.ref}]" if r.ref else ""
        lines.append(f"- {src} --{r.rel}--> {dst}{when}{ref}")
    return _scoped("\n".join(lines))


@tool(
    "hydrology_balance",
    "Tier-0 municipal water balance + low-flow assimilative screen: the WWTP "
    "discharges (cited design flows) routed to their receiving waters, each checked "
    "against the stream's cited 7Q10 low flow. Flags effluent-dominated streams.",
    {},
)
async def hydrology_balance(_args: dict[str, Any]) -> dict[str, Any]:
    if (note := _reference_only("hydrology_balance")) is not None:
        return note
    from watermark.pipeline import hydrology as hydro_stage

    balance, _checks, findings = hydro_stage.run_baseline()
    lines = ["WATER BALANCE (cfs; source in brackets):"]
    for n in balance.nodes:
        v = n.return_flow or n.inflow
        flow = str(v) if v else "—"
        recv = f" -> {n.node.receiving_water}" if n.node.receiving_water else ""
        lines.append(f"- [{n.node.role}] {n.node.name}{recv}: {flow}")
    lines.append("\nLOW-FLOW ASSIMILATIVE SCREEN (7Q10 dilution):")
    lines.extend(str(f) for f in findings)
    if not findings:
        lines.append("(no WWTP discharge had a cited receiving-water 7Q10)")
    if balance.warnings:
        lines.append("\nCaveats:")
        lines.extend(f"! {w}" for w in balance.warnings)
    return _scoped("\n".join(lines))


@tool(
    "stormwater_runoff",
    "Tier-0 pre- vs post-development design-storm runoff for the data-center campus: "
    "SCS curve-number method with live NOAA Atlas-14 rainfall. Reports the peak-flow "
    "and runoff-volume increase from paving the footprint (the detention deficit).",
    {},
)
async def stormwater_runoff(_args: dict[str, Any]) -> dict[str, Any]:
    if (note := _reference_only("stormwater_runoff")) is not None:
        return note
    from watermark.pipeline import hydrology as hydro_stage

    runoff, findings = hydro_stage.run_storm()
    lines = [
        f"{runoff.name}: {runoff.area.value:,.0f} ac footprint [{runoff.area.source}]",
        f"Design storm: {runoff.storm.return_period_yr}-yr 24-hr, "
        f"{runoff.storm.depth.value:.2f} in [{runoff.storm.depth.source}]",
        f"  pre-development  CN {runoff.pre.curve_number:.0f}: "
        f"peak {runoff.pre.peak_cfs:,.0f} cfs, {runoff.pre.volume_acft:,.0f} ac-ft",
        f"  post-development CN {runoff.post.curve_number:.0f}: "
        f"peak {runoff.post.peak_cfs:,.0f} cfs, {runoff.post.volume_acft:,.0f} ac-ft",
        "",
    ]
    lines.extend(str(f) for f in findings)
    lines.append("\n(Tier-0 SCS; HSG + land cover are cited assumptions, rainfall is live NOAA.)")
    return _scoped("\n".join(lines))


@tool(
    "hydrology_scenario",
    "Baseline vs data-center-buildout scenario: the campus cooling consumptive draw "
    "(an assumption knob) compared against the cited Ottawa River 7Q10 low flow. Shows "
    "how a data center stresses an already low-flow river.",
    {},
)
async def hydrology_scenario(_args: dict[str, Any]) -> dict[str, Any]:
    if (note := _reference_only("hydrology_scenario")) is not None:
        return note
    from watermark.pipeline import hydrology as hydro_stage

    base, build, delta = hydro_stage.run_scenarios()
    lines = [
        f"baseline: consumptive draw {base.consumptive_loss.value:.2f} cfs",
        f"buildout: cooling {build.scenario.cooling_demand.value:g} MGD x "
        f"{build.scenario.consumptive_fraction.value:g} consumptive "
        f"-> {build.consumptive_loss.value:.2f} cfs net basin loss",
        f"net new consumptive draw: {delta.consumptive_increase_cfs:.2f} cfs",
    ]
    if delta.multiple_of_7q10 is not None:
        lines.append(
            f"= {delta.multiple_of_7q10:g}x the Ottawa River 7Q10 ({delta.ottawa_7q10_cfs:g} cfs, cited)"
        )
    if build.ottawa_live is not None:
        lines.append(f"Ottawa live flow: {build.ottawa_live.value:.0f} cfs")
    lines.append(
        "\n(Cooling knobs are assumptions; Ottawa 7Q10 is document-cited. Tier-0 screening.)"
    )
    return _scoped("\n".join(lines))


@tool(
    "storm_plan_inventory",
    "Document-grounded drainage facts from the campus grading & storm plan (sheet "
    "1A-C-3104, 95% SPS): storm-structure rim-elevation relief, the conveyance "
    "inventory, and whether any on-site detention/retention storage is shown. Grounds "
    "the Tier-1 detention result in the real civil design.",
    {},
)
async def storm_plan_inventory(_args: dict[str, Any]) -> dict[str, Any]:
    if (note := _reference_only("storm_plan_inventory")) is not None:
        return note
    from watermark.hydrology import stormplan

    inv = stormplan.load_inventory()
    if inv is None:
        return _text("No storm-plan inventory yet (run `bosc storm-plan --refresh`).")
    lines = [
        f"{inv.sheet_id} {inv.discipline} ({inv.phase}, {inv.status})",
        f"graded relief {inv.rim_min.value:.1f}-{inv.rim_max.value:.1f} ft "
        f"over {inv.rim_labels} storm-structure rims",
        f"conveyance: {', '.join(inv.structure_types)}",
        f"features: {', '.join(inv.conveyance_features)}",
    ]
    lines += [str(f) for f in stormplan.storm_plan_findings(inv)]
    lines.append(
        "\n(Transcribed from the civil sheet; pipe connectivity/inverts are vector geometry "
        "with no schedule table, so a routable network is not fabricated.)"
    )
    return _scoped("\n".join(lines))


@tool(
    "sanitary_basis",
    "Document-cited sanitary design basis for the WWTPs: per-plant permitted average "
    "design flow and peak hydraulic capacity (so the wet-weather headroom = peak - avg), "
    "plus the I/I + SSO regulatory context (1996 federal consent decree; 2005 OEPA mandate "
    "to eliminate bypassing by 2015). Grounds the Tier-1 sanitary surcharge.",
    {},
)
async def sanitary_basis(_args: dict[str, Any]) -> dict[str, Any]:
    if (note := _reference_only("sanitary_basis")) is not None:
        return note
    from watermark.hydrology.sanitary import load_sanitary_basis

    basis = load_sanitary_basis()
    if basis is None:
        return _text(
            "No sanitary basis table found (data/reference/hydrology/sanitary-basis.yaml)."
        )
    lines = []
    for p in basis.plants:
        peak = f"{p.peak_capacity.value:g} MGD peak" if p.peak_capacity else "peak uncited"
        pf = f", {p.peaking_factor.value:g}x" if p.peaking_factor else ""
        head = f", headroom {p.headroom_mgd:g} MGD" if p.headroom_mgd is not None else ""
        lines.append(
            f"{p.plant} ({p.npdes or 'NPDES n/a'} -> {p.receiving_water}): "
            f"{p.avg_design_flow.value:g} MGD avg / {peak}{pf}{head}"
        )
    lines.append(f"Campus FM-2 industrial: {basis.campus_industrial.value:g} MGD (document)")
    lines.append(f"I/I remediation: ${basis.ii_remediation_musd.value:g}M; {basis.decree_note}")
    return _scoped("\n".join(lines))


@tool(
    "tier1_swmm",
    "Tier-1 EPA SWMM run: detention-basin sizing (the storage that holds the "
    "post-development peak to the pre-development rate) and sanitary wet-weather "
    "surcharge (storm-driven peak vs documented WWTP peak capacities). Needs the "
    "SWMM engine; reports clearly if unavailable.",
    {},
)
async def tier1_swmm(_args: dict[str, Any]) -> dict[str, Any]:
    if (note := _reference_only("tier1_swmm")) is not None:
        return note
    from watermark.hydrology.tier1 import run_tier1, tier1_findings

    result = run_tier1()
    if not result.available:
        return _text(result.note)
    lines = [str(f) for f in tier1_findings(result)]
    lines.append(
        "\n(Tier-1 EPA SWMM; footprint + plant capacities document-sourced, storm from NOAA; "
        "network/hydraulic params are assumptions.)"
    )
    return _scoped("\n".join(lines))


@tool(
    "retrieve_corpus",
    "Semantic search over the indexed source corpus (documents, reference data, extracted "
    "artifacts). Returns ranked chunks with text and provenance citations. Use to find "
    "relevant precedents from reference sites, or to discover source context that has not "
    "yet been extracted. Requires the index to be built first (watermark index).",
    {
        "query": str,
        "site": str,
        "collection": str,
        "doc_kind": str,
        "limit": int,
    },
)
async def retrieve_corpus(args: dict[str, Any]) -> dict[str, Any]:
    from watermark.retrieval.embeddings import get_provider
    from watermark.retrieval.store import CorpusStore

    settings = get_settings()
    store = CorpusStore(settings.lancedb_dir, get_provider(settings))

    if not store.exists:
        return _text(
            "[retrieval] Index not built. Run `watermark index` to build the corpus store "
            "before using retrieve_corpus."
        )

    query: str = args.get("query", "")
    if not query:
        return _text("[retrieval] query is required.")

    results = store.query(
        query,
        site=args.get("site") or None,
        collection=args.get("collection") or None,
        doc_kind=args.get("doc_kind") or None,
        limit=int(args.get("limit", 10)),
    )

    if not results:
        return _text("[retrieval] No results found for that query / filter combination.")

    lines = [f"[retrieval] {len(results)} result(s) for: {query!r}\n"]
    for i, r in enumerate(results, start=1):
        page_note = f" p.{r.page + 1}" if r.page >= 0 else ""
        site_note = f" [{r.site}]" if r.site else ""
        lines.append(
            f"--- {i}. {r.doc_kind}/{r.collection}/{r.source_path}{page_note}{site_note} "
            f"(score {r.score:.3f}) ---"
        )
        lines.append(r.text[:600])
        lines.append("")
    return _text("\n".join(lines))


_GH_REPO = "watermark-directory/the-watermark-directory"


@tool(
    "report_novel_finding",
    "File a GitHub issue for context found in the source corpus that has no corresponding "
    "extraction. Use when retrieve_corpus surfaces something significant that is not yet in "
    "data/extracted/. Files the issue and returns immediately — do not pursue the finding "
    "inline.",
    {
        "title": str,
        "description": str,
        "source_citation": str,
        "site": str,
        "collection": str,
    },
)
async def report_novel_finding(args: dict[str, Any]) -> dict[str, Any]:
    import httpx

    settings = get_settings()
    title: str = args.get("title", "").strip()
    description: str = args.get("description", "").strip()
    source_citation: str = args.get("source_citation", "").strip()
    finding_site: str = args.get("site", "").strip()
    collection: str = args.get("collection", "").strip()

    if not title or not description:
        return _text("[report_novel_finding] title and description are required.")

    labels = ["type:gap", "area:evidence", "status:agent-proposed"]
    if finding_site:
        labels.append(f"site:{finding_site}")

    body_parts = [description]
    if source_citation:
        body_parts.append(f"\n**Source citation:** {source_citation}")
    if collection:
        body_parts.append(f"**Collection:** {collection}")
    body_parts.append(
        "\n_Filed automatically by the research agent (status:agent-proposed). "
        "Requires triage before any extraction work is scheduled._"
    )
    body = "\n".join(body_parts)

    if not settings.github_token:
        summary = (
            f"[report_novel_finding] No GITHUB_TOKEN — issue not filed.\n"
            f"Title: {title}\n"
            f"Labels: {', '.join(labels)}\n"
            f"Body:\n{body}"
        )
        return _text(summary)

    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {settings.github_token}",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    payload = {"title": title, "body": body, "labels": labels}

    try:
        resp = httpx.post(
            f"{settings.github_base_url}/repos/{_GH_REPO}/issues",
            json=payload,
            headers=headers,
            timeout=30.0,
        )
        if resp.status_code == 201:
            data = resp.json()
            return _text(f"[report_novel_finding] Filed as #{data['number']}: {data['html_url']}")
        return _text(
            f"[report_novel_finding] GitHub API returned {resp.status_code}: {resp.text[:200]}"
        )
    except Exception as exc:
        return _text(f"[report_novel_finding] Request failed: {exc}")


@tool(
    "reconcile_estimate",
    "Reconcile a generated estimate extraction (*.opc.yaml): line items -> section "
    "subtotals -> construction subtotal + markups -> total.",
    {"filename": str},
)
async def reconcile_estimate(args: dict[str, Any]) -> dict[str, Any]:
    path = _resolve(args["filename"], "*.opc.yaml")
    if path is None:
        return _text(f"Not found: {args['filename']}")
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        return _text(f"{path.name} is not valid YAML: {str(exc).splitlines()[0]}")
    if not isinstance(data, dict) or "estimate" not in data:
        return _text(f"{path.name} is not a generated estimate extraction (no 'estimate' block).")
    estimate = Estimate.model_validate(data["estimate"])
    findings = analyze.reconcile_estimate(estimate)
    if not findings:
        return _text(f"{path.name}: nothing to reconcile (no subtotals/total present).")
    return _text("\n".join(str(f) for f in findings))


# All tools, and the in-process MCP server that hosts them.
ALL_TOOLS = [
    list_documents,
    list_extractions,
    read_extraction,
    reconcile_summary,
    program_overview,
    reconcile_estimate,
    timeline,
    entities,
    hydrology_balance,
    stormwater_runoff,
    hydrology_scenario,
    storm_plan_inventory,
    sanitary_basis,
    tier1_swmm,
    retrieve_corpus,
    report_novel_finding,
]
ALLOWED_TOOL_NAMES = [f"mcp__{SERVER_NAME}__{t.name}" for t in ALL_TOOLS]


def build_server() -> Any:
    """Create the in-process SDK MCP server hosting BOSC's tools."""
    return create_sdk_mcp_server(name=SERVER_NAME, version="0.1.0", tools=ALL_TOOLS)
