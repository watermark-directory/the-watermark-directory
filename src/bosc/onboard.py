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

The self-research first pass (Track 2, #247) is a documented seam, not wired here — see
`docs/onboarding.md`.
"""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict

from bosc.config import Settings, get_settings
from bosc.hydrology import basin, climate, drainage
from bosc.hydrology.connectors._cache import HydroOfflineError
from bosc.hydrology.connectors.nasa_power import fetch_climatology
from bosc.hydrology.connectors.ssurgo import dominant_hsg
from bosc.logging import get_logger
from bosc.sites import active_profile

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


def scaffold_dirs(settings: Settings) -> tuple[list[str], list[str]]:
    """Create the per-site data dirs + a README in each (idempotent).

    Returns ``(dirs, readmes_written)`` as data_dir-relative paths; an existing README is
    left untouched.
    """
    prof = active_profile(settings)
    slug = prof.slug
    targets: list[tuple[Path, str]] = [
        (settings.data_dir / "reference" / slug, "reference data"),
        (settings.data_dir / "extracted" / slug, "extractions"),
        (settings.data_dir / "reference" / "hydrology" / slug, "hydrology connector outputs"),
    ]
    dirs: list[str] = []
    written: list[str] = []
    for path, purpose in targets:
        path.mkdir(parents=True, exist_ok=True)
        dirs.append(str(path.relative_to(settings.data_dir)))
        readme = path / "README.md"
        if not readme.is_file():
            readme.write_text(_readme_body(prof.place, slug, prof.basin, purpose), encoding="utf-8")
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
    except HydroOfflineError as exc:
        return OnboardStep(name=name, status="dry-run", detail=f"offline — record fixture: {exc}")
    except FileNotFoundError as exc:
        return OnboardStep(name=name, status="skipped", detail=f"input missing: {exc}")
    except Exception as exc:  # report, never crash the run
        log.warning("onboard.step_failed", step=name, error=str(exc).splitlines()[0])
        return OnboardStep(name=name, status="error", detail=str(exc).splitlines()[0])


def onboard_site(*, settings: Settings | None = None) -> OnboardReport:
    """Onboard the active site (``settings.site``): scaffold + reach connectors + validation."""
    settings = settings or get_settings()
    prof = active_profile(settings)

    dirs, readmes = scaffold_dirs(settings)
    steps: list[OnboardStep] = [
        OnboardStep(
            name="scaffold",
            status="ok",
            detail=f"{len(dirs)} dirs; {len(readmes)} README(s) written",
        )
    ]

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

    return OnboardReport(
        slug=prof.slug,
        place=prof.place,
        basin=prof.basin,
        scaffolded_dirs=dirs,
        steps=steps,
        review_checklist=_review_checklist(prof.slug),
    )


def _review_checklist(slug: str) -> list[str]:
    """The blocking, human review gate before a site can be promoted."""
    return [
        "Every written reference value is reviewed against a cited source (no fabricated values).",
        "SSURGO dominant HSG matches the profile, or the SiteProfile is updated with a citation.",
        "basin-screen coverage is sane for this site's receiving waters.",
        "A per-jurisdiction County/City GIS connector exists (the known lift — see docs/onboarding.md).",
        "Self-research first pass run (doc seam; awaits #247 — not wired).",
        f"PROMOTION IS A SEPARATE MANUAL EDIT: flip status->live + selectable->true for {slug!r} in "
        "frontend/src/lib/sites.ts, parity-gated. onboard never auto-promotes; only one live build "
        "(/bosc) exists today.",
    ]
