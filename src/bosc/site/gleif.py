"""Render the GLEIF LEI resolution as a site page.

Publishes ``data/reference/gleif/lei-records.yaml`` (built by ``bosc lei``) as a
browsable "who owns whom" table for the corridor entity parents, cross-linked to the
RSEI inventory and the defense-contractor scan. The exact-LEI / no-fuzzy-match
discipline is stated up front so a row is never read as a guessed identity.
"""

from __future__ import annotations

from bosc.gleif import LeiInventory
from bosc.pipeline.entities import EntityGraph, normalize_name

_CAUTION = (
    '!!! note "Verified LEIs — exact lookups, self-reported relationships"\n'
    "    Every LEI here is **pinned and fetched by its exact 20-character ID**, not a "
    "fuzzy name match. A blank parent means GLEIF holds *no reported relationship "
    "record* — GLEIF parent links are self-reported, so absence is not proof of no "
    "parent. Entities whose correct legal entity is ambiguous are listed as "
    "unresolved leads, not pinned rows."
)


def _esc(text: str) -> str:
    return text.replace("|", "\\|").replace("\n", " ").strip()


def _in_graph(egraph: EntityGraph | None, *names: str | None) -> bool:
    if egraph is None:
        return False
    return any(n and egraph.get(normalize_name(n)) is not None for n in names)


def render_gleif(inv: LeiInventory, *, egraph: EntityGraph | None = None) -> str:
    """Render the LEI resolution to a markdown page."""
    recs = inv.records
    lines = [
        "# Corridor entity LEIs (GLEIF)",
        "",
        f"Verified **Legal Entity Identifier** records for **{len(recs)}** corridor / "
        "[RSEI](rsei.md) facility parent companies, resolved against the GLEIF "
        "registry — the global *who owns whom* directory. Built by `bosc lei`; see the "
        "[reference README](data/reference/gleif/README.md). Sits alongside the corpus "
        "[entity graph](entities.md) and the [defense contractors](defense-contractors.md) "
        "page.",
        "",
        _CAUTION,
        "",
        "## Resolved entities",
        "",
        "| Legal name | LEI | Jurisdiction | Status | Reg. | Legal address | Ultimate parent | In graph |",
        "|---|---|---|---|---|---|---|:-:|",
    ]
    for r in recs:
        addr = r.legal_address
        loc = (
            ", ".join(p for p in [addr.city, addr.region, addr.country] if p)
            if addr is not None
            else "—"
        )
        up = (
            f"{_esc(r.ultimate_parent.name)} (`{r.ultimate_parent.lei}`)"
            if r.ultimate_parent
            else (f"{_esc(r.direct_parent.name)} (direct)" if r.direct_parent else "—")
        )
        ig = "✓" if _in_graph(egraph, r.legal_name, r.watchlist_name) else "—"
        lines.append(
            f"| {_esc(r.legal_name)} | `{r.lei}` | {_esc(r.jurisdiction or '—')} "
            f"| {_esc(r.entity_status or '—')} | {_esc(r.registration_status or '—')} "
            f"| {_esc(loc)} | {up} | {ig} |"
        )
    lines.append("")

    # Notes (the watchlist's per-entity 'why it matters').
    noted = [r for r in recs if r.note]
    if noted:
        lines += ["## Why these entities", ""]
        lines += [f"- **{_esc(r.legal_name)}** — {_esc(r.note or '')}" for r in noted]
        lines.append("")

    if inv.leads:
        lines += [
            "## Unresolved leads",
            "",
            "Entities with no verified, unambiguous LEI pinned (omission over a wrong match).",
            "",
            "| Entity | Search term | Note |",
            "|---|---|---|",
        ]
        for lead in inv.leads:
            lines.append(
                f"| {_esc(lead.name)} | {_esc(lead.query or '—')} | {_esc(lead.note or '—')} |"
            )
        lines.append("")
    return "\n".join(lines)
