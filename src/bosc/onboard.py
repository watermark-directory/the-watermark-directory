"""Repeatable watershed-point onboarding (#326, Track 3 of #323).

`onboard_site` brings a registered site from nothing toward a "coming soon" build: it
scaffolds the per-site data dirs (with house-style READMEs), runs the portable reach
connectors for the active site's `SiteProfile` (NWIS-derived basin low-flows [shared],
NOAA Atlas-14 corridor DDF, SSURGO dominant HSG, NASA-POWER climatology), validates the
basin assimilative screen, and returns a report carrying a **blocking review checklist**.

It *proposes*; it never promotes. Flipping a site to `live`/`selectable` in
`frontend/src/lib/sites.ts` stays a separate, human, parity-gated edit.

Preconditions: the site's `SiteProfile` is already registered in `bosc.sites.SITES`
(authoring it is the first step — a code edit). Per-site point outputs (climatology, corridor
DDF) are slug-scoped via the profile so onboarding never clobbers Lima; basin-level outputs
(derived 7Q10, ECHO POTW inventory) are shared across Maumee sites by design.

The self-research first pass (Track 2, #247) is wired as the opt-in ``research`` step: the
discipline-bound agent investigates the new site and writes a proposal artifact under
``data/research/`` for human triage — see `docs/onboarding.md`.
"""

from __future__ import annotations

import asyncio
from collections.abc import Callable
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict

from bosc import rsei
from bosc.config import Settings, get_settings
from bosc.connectors import OfflineError
from bosc.economics import baseline as econ_baseline
from bosc.economics import energy as econ_energy
from bosc.grid import utility as grid_utility
from bosc.hydrology import basin, climate, drainage
from bosc.hydrology.connectors.nasa_power import fetch_climatology
from bosc.hydrology.connectors.ssurgo import dominant_hsg
from bosc.logging import get_logger
from bosc.sites import SiteProfile, active_profile, output_path_collisions

log = get_logger(__name__)

StepStatus = Literal["ok", "skipped", "dry-run", "error"]


class OnboardStep(BaseModel):
    """One step of an onboarding run + its outcome."""

    model_config = ConfigDict(extra="forbid")

    name: str
    status: StepStatus
    detail: str
    output_path: str | None = None  # data_dir-relative when a file was written


class OnboardReport(BaseModel):
    """The result of an onboarding run: what ran, what landed, and what to review."""

    model_config = ConfigDict(extra="forbid")

    slug: str
    place: str
    basin: str
    scaffolded_dirs: list[str]  # data_dir-relative
    steps: list[OnboardStep]
    review_checklist: list[str]


def _readme_body(place: str, slug: str, basin: str, purpose: str) -> str:
    """House-style README for a scaffolded per-site dir (source + gaps + regenerate)."""
    return (
        f"# {place} ({slug}) — {purpose}\n\n"
        f"Per-site onboarding tree for the {place} watershed point (basin: {basin}), "
        f"scaffolded by `bosc onboard {slug}` (#326). Values come from the portable reach "
        f"connectors keyed to this site's `SiteProfile` in `bosc.sites` — nothing here is "
        f"fabricated; regenerate, don't hand-edit.\n\n"
        "## Source\n\n"
        f"`bosc onboard {slug}` over the {place} `SiteProfile` (reach connectors: NWIS / "
        "NOAA Atlas-14 / SSURGO / NASA-POWER).\n\n"
        "## Known gaps & caveats\n\n"
        "- Onboarding seed — **review every value against a cited source before promotion** "
        "(`frontend/src/lib/sites.ts` `status`/`selectable`, parity-gated).\n"
        "- County/City parcel & zoning GIS is jurisdiction-specific and is **not** populated "
        "by the portable reach connectors — it needs a per-jurisdiction connector "
        "(see `docs/onboarding.md`).\n\n"
        "## Regenerate\n\n"
        f"`bosc onboard {slug}`  (or the per-connector commands: `derive-low-flows`, "
        "`nasa-power --write`, etc.)\n"
    )


def scaffold_dirs(settings: Settings, *, dry_run: bool = False) -> tuple[list[str], list[str]]:
    """Create the per-site data dirs + a README in each (idempotent).

    Returns ``(dirs, readmes_to_write)`` as data_dir-relative paths; an existing README is
    left untouched. With ``dry_run`` nothing is created — it just reports what *would* land.
    """
    prof = active_profile(settings)
    slug = prof.slug
    targets: list[tuple[Path, str]] = [
        (settings.data_dir / "reference" / slug, "reference data"),
        (settings.data_dir / "extracted" / slug, "extractions"),
        (settings.data_dir / "reference" / "hydrology" / slug, "hydrology connector outputs"),
        (settings.data_dir / "reference" / "economics" / slug, "economics baseline outputs"),
        (settings.data_dir / "reference" / "eia" / slug, "energy / grid outputs"),
        (settings.data_dir / "reference" / "rsei" / slug, "RSEI toxics outputs"),
    ]
    dirs: list[str] = []
    written: list[str] = []
    for path, purpose in targets:
        if not dry_run:
            path.mkdir(parents=True, exist_ok=True)
        dirs.append(str(path.relative_to(settings.data_dir)))
        readme = path / "README.md"
        if not readme.is_file():
            if not dry_run:
                readme.write_text(
                    _readme_body(prof.place, slug, prof.basin, purpose), encoding="utf-8"
                )
            written.append(str(readme.relative_to(settings.data_dir)))
    return dirs, written


def _rel(settings: Settings, path: Path) -> str:
    """data_dir-relative string for a written output (falls back to the full path)."""
    try:
        return str(path.relative_to(settings.data_dir))
    except ValueError:
        return str(path)


def _run_step(name: str, fn: Callable[[], OnboardStep]) -> OnboardStep:
    """Run one connector step, turning the expected failure modes into a recorded status.

    A brand-new site has no committed fixtures, so an offline miss is a `dry-run` (naming the
    key to record), a missing input file is `skipped`, and anything else is a non-fatal
    `error` — onboarding always completes and reports.
    """
    try:
        return fn()
    except OfflineError as exc:  # any connector's offline miss (hydro + econ)
        return OnboardStep(name=name, status="dry-run", detail=f"offline — record fixture: {exc}")
    except FileNotFoundError as exc:
        return OnboardStep(name=name, status="skipped", detail=f"input missing: {exc}")
    except Exception as exc:  # report, never crash the run
        log.warning("onboard.step_failed", step=name, error=str(exc).splitlines()[0])
        return OnboardStep(name=name, status="error", detail=str(exc).splitlines()[0])


def _guard_output_paths(slug: str) -> None:
    """Refuse to onboard if this site's per-site outputs would overwrite another site's.

    The #326 design slug-scopes the point-specific outputs so onboarding never clobbers
    Lima; this is the guard for a profile that copied another site without re-scoping them.
    """
    clashes = output_path_collisions(slug)
    if clashes:
        detail = "; ".join(f"{field} collides with {others}" for field, others in clashes.items())
        raise ValueError(
            f"{slug}: per-site output paths are not unique ({detail}). Slug-scope "
            f"climatology_relpath/corridor_ddf_relpath (e.g. reference/hydrology/{slug}/…) in the "
            "SiteProfile so onboarding doesn't overwrite another site's committed data."
        )


def onboard_site(
    *, settings: Settings | None = None, dry_run: bool = False, research: bool = False
) -> OnboardReport:
    """Onboard the active site (``settings.site``): scaffold + reach connectors + validation.

    With ``dry_run`` nothing is written — it resolves and reports the plan (steps + target
    output paths) so the first run on a cohort site can be previewed safely. With ``research``
    the discipline-bound agent (#247) runs a self-research first pass over the new site and
    writes a proposal artifact for human triage (a paid/online call; opt-in).
    """
    settings = settings or get_settings()
    prof = active_profile(settings)
    _guard_output_paths(prof.slug)  # before any write

    dirs, readmes = scaffold_dirs(settings, dry_run=dry_run)
    verb = "would create" if dry_run else "created"
    steps: list[OnboardStep] = [
        OnboardStep(
            name="scaffold",
            status="dry-run" if dry_run else "ok",
            detail=f"{verb} {len(dirs)} dir(s); {len(readmes)} README(s)",
        )
    ]
    steps += (
        _planned_steps(settings, prof, research)
        if dry_run
        else _executed_steps(settings, prof, research)
    )

    report = OnboardReport(
        slug=prof.slug,
        place=prof.place,
        basin=prof.basin,
        scaffolded_dirs=dirs,
        steps=steps,
        review_checklist=_review_checklist(prof.slug),
    )
    # Persist the gate as a living, checkable artifact (only if absent — preserve human checks).
    if not dry_run:
        doc = settings.data_dir / "extracted" / prof.slug / "ONBOARDING.md"
        if not doc.is_file():
            doc.parent.mkdir(parents=True, exist_ok=True)
            doc.write_text(render_onboarding_doc(report), encoding="utf-8")
    return report


def render_onboarding_doc(report: OnboardReport) -> str:
    """The living onboarding record: dimension coverage + the last run + the review gate."""
    rows = "\n".join(
        f"| {s.name} | {s.status} | {s.output_path or s.detail} |" for s in report.steps
    )
    gate = "\n".join(f"- [ ] {item}" for item in report.review_checklist)
    return (
        f"# Onboarding — {report.place} ({report.slug})\n\n"
        f"Living record for the {report.place} watershed point (basin: {report.basin}), "
        "scaffolded by `bosc onboard`. Check items as you complete them; the site is **not** "
        "promoted (`frontend/src/lib/sites.ts` `status`/`selectable`) until the gate is clear.\n\n"
        "## Dimension coverage\n\n"
        "- [x] **Hydrology** — onboard reach connectors (low-flows, corridor DDF, SSURGO HSG, climatology)\n"
        "- [x] **Economics** — county baseline, RSEI toxics, consumer energy, grid profile\n"
        "- [ ] **Data-center activity** — extracted permits/records + entity graph "
        "(corpus extraction; seed proposals via `bosc onboard --research`, #247)\n"
        "- [ ] **Per-jurisdiction GIS** — parcels/zoning connector (the known lift; see docs/onboarding.md)\n\n"
        "## Last onboard run\n\n"
        "| step | status | output |\n|---|---|---|\n" + rows + "\n\n"
        "## Review gate (blocking)\n\n" + gate + "\n"
    )


def _planned_steps(settings: Settings, prof: SiteProfile, research: bool) -> list[OnboardStep]:
    """The connector steps a real run *would* take — target paths, no side effects."""
    steps = [
        OnboardStep(
            name="derive-low-flows",
            status="dry-run",
            detail="basin-level (shared across Maumee sites)",
            output_path="reference/hydrology/low-flow-7q10.derived.yaml",
        ),
        OnboardStep(
            name="corridor-ddf",
            status="dry-run",
            detail="per-site",
            output_path=prof.corridor_ddf_relpath,
        ),
        OnboardStep(
            name="ssurgo-hsg",
            status="dry-run",
            detail=f"would read footprint {prof.footprint_relpath}",
        ),
        OnboardStep(
            name="climatology",
            status="dry-run",
            detail="per-site",
            output_path=prof.climatology_relpath,
        ),
        OnboardStep(name="basin-screen", status="dry-run", detail="validation (read-only)"),
        # economics dimension (per-site outputs)
        OnboardStep(
            name="econ-baseline",
            status="dry-run",
            detail="per-site (county FIPS)",
            output_path=prof.baseline_relpath,
        ),
        OnboardStep(
            name="rsei",
            status="dry-run",
            detail="per-site (county FIPS)",
            output_path=prof.rsei_relpath,
        ),
        OnboardStep(
            name="consumer-energy",
            status="dry-run",
            detail="per-site (state)",
            output_path=prof.consumer_energy_relpath,
        ),
        OnboardStep(
            name="grid-profile",
            status="dry-run",
            detail="per-site (utility; sparse without a documented facility)",
            output_path=prof.grid_relpath,
        ),
    ]
    if research:
        steps.append(
            OnboardStep(
                name="self-research",
                status="dry-run",
                detail="discipline-bound agent first pass (paid/online)",
                output_path=f"research/<{prof.slug}-run>/",
            )
        )
    return steps


def _research_step(settings: Settings, prof: SiteProfile) -> OnboardStep:
    """Run the discipline-bound self-research first pass over the new site (#247 seam).

    A paid/online LLM call — skipped cleanly when there's no key or the run is offline. The
    agent proposes (a manifest under data/research/<slug>-<date>/ for human triage); it never
    promotes or writes to the corpus.
    """
    if settings.hydro_offline or not settings.anthropic_api_key:
        why = "offline" if settings.hydro_offline else "no ANTHROPIC_API_KEY"
        return OnboardStep(name="self-research", status="skipped", detail=why)

    from datetime import UTC, datetime

    from bosc.agent.client import ResearchAgent
    from bosc.research import run_research, run_slug, write_run

    generated_at = datetime.now(UTC).isoformat(timespec="seconds")
    topic = (
        f"onboard {prof.slug} ({prof.place}): data-center activity + receiving-water screen "
        "for a new watershed-point site"
    )
    agent = ResearchAgent(settings=settings, max_turns=settings.research_max_turns)
    manifest = asyncio.run(
        run_research(
            topic,
            generated_at=generated_at,
            settings=settings,
            agent=agent,
            max_proposals=settings.research_max_proposals,
        )
    )
    out_dir = settings.research_dir / run_slug(topic, generated_at)
    write_run(manifest, out_dir, settings=settings)
    return OnboardStep(
        name="self-research",
        status="ok",
        detail=f"{len(manifest.proposals)} proposal(s) — triage",
        output_path=_rel(settings, out_dir),
    )


def _executed_steps(settings: Settings, prof: SiteProfile, research: bool) -> list[OnboardStep]:
    """Run the reach connectors for real, each resilient to an offline/missing-input miss."""
    steps: list[OnboardStep] = []

    # NWIS -> basin-derived 7Q10 (basin-level, SHARED across Maumee sites).
    def _low_flows() -> OnboardStep:
        path = basin.write_derived_low_flows(
            basin.derive_basin_low_flows(settings=settings), settings=settings
        )
        return OnboardStep(
            name="derive-low-flows",
            status="ok",
            detail="basin-level (shared across Maumee sites)",
            output_path=_rel(settings, path),
        )

    steps.append(_run_step("derive-low-flows", _low_flows))

    # NOAA Atlas-14 -> corridor DDF (per-site).
    def _ddf() -> OnboardStep:
        path = drainage.write_corridor_ddf(
            drainage.build_corridor_ddf(settings=settings), settings=settings
        )
        return OnboardStep(
            name="corridor-ddf", status="ok", detail="per-site", output_path=_rel(settings, path)
        )

    steps.append(_run_step("corridor-ddf", _ddf))

    # SSURGO dominant HSG over the footprint (inline; no committed output — a validation read).
    def _hsg() -> OnboardStep:
        survey = dominant_hsg(settings.data_dir / prof.footprint_relpath, settings=settings)
        match = (
            "matches profile"
            if survey.hsg_letter == prof.dominant_hsg
            else (
                f"DIFFERS from profile {prof.dominant_hsg!r} — update SiteProfile with a citation"
            )
        )
        return OnboardStep(
            name="ssurgo-hsg", status="ok", detail=f"HSG {survey.dominant_hsg}; {match}"
        )

    steps.append(_run_step("ssurgo-hsg", _hsg))

    # NASA-POWER climatology (per-site).
    def _climate() -> OnboardStep:
        path = climate.write_climatology(fetch_climatology(settings=settings), settings=settings)
        return OnboardStep(
            name="climatology", status="ok", detail="per-site", output_path=_rel(settings, path)
        )

    steps.append(_run_step("climatology", _climate))

    # basin-screen — validation only (read-only over the shared basin inventory).
    def _screen() -> OnboardStep:
        scr = basin.check_basin_assimilative(settings=settings)
        c = scr.coverage
        return OnboardStep(
            name="basin-screen",
            status="ok" if c.total else "skipped",
            detail=f"{c.screened}/{c.total} dischargers screened ({c.violations} violations, {c.tight} tight)",
        )

    steps.append(_run_step("basin-screen", _screen))

    # --- Economics dimension (per-site outputs; reads stay Lima-keyed until parity) ------
    # Census+QCEW county baseline (per county FIPS).
    def _baseline() -> OnboardStep:
        path = econ_baseline.write_baseline(
            econ_baseline.build_baseline(settings=settings), settings=settings
        )
        return OnboardStep(
            name="econ-baseline",
            status="ok",
            detail="per-site (county FIPS)",
            output_path=_rel(settings, Path(path)),
        )

    steps.append(_run_step("econ-baseline", _baseline))

    # EPA RSEI county toxics inventory (per county FIPS).
    def _rsei() -> OnboardStep:
        inv = rsei.build_inventory(settings)
        path = rsei.write_inventory(inv, rsei.inventory_path(settings).parent)
        return OnboardStep(
            name="rsei",
            status="ok",
            detail="per-site (county FIPS)",
            output_path=_rel(settings, path),
        )

    steps.append(_run_step("rsei", _rsei))

    # EIA consumer energy prices (per state).
    def _consumer_energy() -> OnboardStep:
        path = econ_energy.write_consumer_energy(
            econ_energy.build_consumer_energy(settings=settings), settings=settings
        )
        return OnboardStep(
            name="consumer-energy",
            status="ok",
            detail="per-site (state)",
            output_path=_rel(settings, Path(path)),
        )

    steps.append(_run_step("consumer-energy", _consumer_energy))

    # EIA-861 utility + grid profile (per utility; sparse without a documented facility load).
    def _grid() -> OnboardStep:
        path = grid_utility.write_grid_profile(
            grid_utility.derive_grid_profile(settings=settings), settings=settings
        )
        return OnboardStep(
            name="grid-profile",
            status="ok",
            detail="per-site (utility)",
            output_path=_rel(settings, Path(path)),
        )

    steps.append(_run_step("grid-profile", _grid))

    # Self-research first pass (#247) — opt-in; the discipline-bound agent proposes for triage.
    if research:
        steps.append(_run_step("self-research", lambda: _research_step(settings, prof)))
    return steps


def _review_checklist(slug: str) -> list[str]:
    """The blocking, human review gate before a site can be promoted."""
    return [
        "Every written reference value is reviewed against a cited source (no fabricated values).",
        "SSURGO dominant HSG matches the profile, or the SiteProfile is updated with a citation.",
        "basin-screen coverage is sane for this site's receiving waters.",
        "A per-jurisdiction County/City GIS connector exists (the known lift — see docs/onboarding.md).",
        "Self-research first pass reviewed (run with --research; triage data/research/<slug>-<date>/).",
        f"PROMOTION IS A SEPARATE MANUAL EDIT: flip status->live + selectable->true for {slug!r} in "
        "frontend/src/lib/sites.ts, parity-gated. onboard never auto-promotes; only one live build "
        "(/bosc) exists today.",
    ]
