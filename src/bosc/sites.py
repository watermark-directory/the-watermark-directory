"""The BOSC network — the Python registry of watershed-point site profiles.

The data-tier peer of ``frontend/src/lib/sites.ts`` (Epic #308 / #323, Track 1): one
:class:`SiteProfile` per watershed point, holding every value that is specific to *that*
site. Lima is the live reference build; basin sites (Fort Wayne, Defiance, …) come online
incrementally and are populated by their onboarding issues (#235-#238), not here.

The active site is selected by ``BOSC_SITE`` (``bosc.config.Settings.site``, default
``"lima"``). :class:`~bosc.config.Settings` resolves the profile's *config knobs*
(the fields in :data:`PROFILE_SETTINGS_FIELDS`) into itself, so the existing ``settings.X``
consumers are unchanged; the deeper hydrology/grid/rsei constants are read by their modules
via :func:`active_profile`.

Per-**basin** data (the Maumee HUC-8 set, the curated mainstem gages) is shared across all
Maumee sites and stays in its modules; a profile only names its ``basin``.

This module imports nothing from :mod:`bosc.config` — ``active_profile`` duck-types the
``.site`` accessor — so the dependency runs one way (``config → sites``).
"""

from __future__ import annotations

from pathlib import PurePosixPath
from typing import TYPE_CHECKING, Literal, get_args, get_origin

from pydantic import BaseModel, ConfigDict

if TYPE_CHECKING:
    from bosc.config import Settings


class SiteProfile(BaseModel):
    """Everything specific to one watershed-point site. Frozen — a fixed reference value."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    # --- Identity (mirrors sites.ts; ``basin`` is the shared-across-Maumee axis) ---------
    slug: str
    place: str
    basin: str

    # --- Config knobs resolved into Settings (see PROFILE_SETTINGS_FIELDS) ---------------
    nwis_sites: list[str]
    nasa_power_lat: float
    nasa_power_lon: float
    rsei_fips: str
    econ_fips: str
    eia861_utility_number: int
    eia_state: str
    # County/City GIS layer endpoints — per-site, jurisdiction-agnostic field names (the
    # connector code that reads them IS jurisdiction-specific: Lima = allen_gis.py/lima_gis.py).
    parcels_url: str
    zoning_url: str
    floodzone_url: str
    gnis_default_state: str
    hydro_utm_epsg: int
    lsc_default_ga: str

    # --- Stormwater design point + cited assumptions (hydrology/stormwater.py) -----------
    # The NOAA-Atlas-14 corridor point — distinct from the nasa_power loop centroid above.
    design_lat: float
    design_lon: float
    dominant_hsg: str
    hsg_citation: str
    pre_cover: str
    post_cover: str
    developed_pervious_cover: str
    noaa_fallback_24h_depth_in: dict[int, float]
    parcels_relpath: str  # relative to settings.data_dir
    footprint_relpath: str  # relative to settings.data_dir

    # --- Per-site onboard reach outputs (point-specific writes; relative to data_dir) ----
    # The point-specific connector outputs `bosc onboard` writes. Lima keeps its legacy
    # (un-slugged) filenames; a new site slug-scopes them so onboarding never clobbers Lima.
    # Basin/state/PJM/national outputs (derived 7Q10, ECHO POTW, consumer-energy is state-
    # but kept per-site for uniformity, ba-interchange, federal) — the shared ones are NOT here.
    # Hydrology (#326):
    climatology_relpath: str  # NASA-POWER climatology (hydrology/climate.py)
    corridor_ddf_relpath: str  # NOAA Atlas-14 corridor DDF (hydrology/drainage.py)
    # Economics (per-site by county FIPS / state / utility):
    baseline_relpath: str  # Census+QCEW county baseline (economics/baseline.py)
    rsei_relpath: str  # EPA RSEI county toxics inventory (rsei.py)
    consumer_energy_relpath: str  # EIA consumer energy prices (economics/energy.py)
    grid_relpath: str  # EIA-861 utility + grid profile (grid/utility.py)

    # --- Toxics corridor inference (hydrology/toxics.py) ---------------------------------
    toxic_corridor_bbox: tuple[float, float, float, float]  # lat_min, lat_max, lon_min, lon_max
    receiving_water_name: str

    # --- Water-balance routing fallback (hydrology/balance.py) ---------------------------
    plant_receiving: dict[str, tuple[str, str]]  # fid -> (receiving water, citation)
    abstraction_gage: str

    # --- Refill supply rivers (hydrology/refill.py) -------------------------------------
    # The site's two refill supply rivers (the model sums both, each passby-adjusted). Named
    # by role, not river: for Lima, primary = Auglaize (Fort Jennings), secondary = Ottawa.
    supply_gage_primary: str
    supply_gage_secondary: str
    passby_primary_cfs: float
    passby_secondary_cfs: float

    # --- Grid market (grid/market.py) ---------------------------------------------------
    lmp_usd_mwh: float
    lmp_citation: str

    # --- RSEI county (rsei.py) ----------------------------------------------------------
    county_name: str

    # --- Legacy SSG map default view (site/gismap.py) -----------------------------------
    map_view_lat: float
    map_view_lon: float
    map_view_zoom: int


# The config-knob fields a profile shares 1:1 with Settings; Settings fills any of these the
# caller did not set explicitly (env/dotenv/kwarg) from the active profile.
PROFILE_SETTINGS_FIELDS: tuple[str, ...] = (
    "nwis_sites",
    "nasa_power_lat",
    "nasa_power_lon",
    "rsei_fips",
    "econ_fips",
    "eia861_utility_number",
    "eia_state",
    "parcels_url",
    "zoning_url",
    "floodzone_url",
    "gnis_default_state",
    "hydro_utm_epsg",
    "lsc_default_ga",
)


# The live reference build. Every value reproduces the pre-#325 hardcoded default exactly —
# see tests/test_sites.py for the zero-drift golden snapshot.
_LIMA = SiteProfile(
    slug="lima",
    place="Lima",
    basin="maumee",
    # config knobs
    nwis_sites=["04187100", "04186500"],
    nasa_power_lat=40.74,
    nasa_power_lon=-84.11,
    rsei_fips="39003",
    econ_fips="39003",
    eia861_utility_number=14006,
    eia_state="OH",
    parcels_url=(
        "https://gis.allencountyohio.com/arcgis/rest/services/AGOL/AGOL_NonEditLayers/MapServer/1"
    ),
    zoning_url=(
        "https://colgis.cityhall.lima.oh.us/server/rest/services/"
        "CitywideMaps/Lima_Zoning/MapServer/6"
    ),
    floodzone_url=(
        "https://colgis.cityhall.lima.oh.us/server/rest/services/"
        "CitywideMaps/Lima_Zoning/MapServer/4"
    ),
    gnis_default_state="OH",
    hydro_utm_epsg=32617,
    lsc_default_ga="136",
    # stormwater
    design_lat=40.797,
    design_lon=-84.123,
    dominant_hsg="C",
    hsg_citation=(
        "Allen County, OH dominant hydrologic soil group C (NRCS soil survey; assumption)"
    ),
    pre_cover="cropland",
    post_cover="developed_campus",
    developed_pervious_cover="open_space",
    noaa_fallback_24h_depth_in={
        1: 2.11,
        2: 2.52,
        5: 3.10,
        10: 3.58,
        25: 4.25,
        50: 4.81,
        100: 5.39,
        200: 6.01,
        500: 6.88,
        1000: 7.59,
    },
    parcels_relpath="reference/periplus/bosc-parcels.geojson",
    footprint_relpath="extracted/plans/bosc-site-footprint.yaml",
    # per-site onboard reach outputs (Lima = legacy un-slugged paths)
    climatology_relpath="reference/hydrology/nasa-power-climatology.yaml",
    corridor_ddf_relpath="reference/hydrology/atlas14-corridor-ddf.yaml",
    baseline_relpath="reference/economics/baseline.yaml",
    rsei_relpath="reference/rsei/inventory.yaml",
    consumer_energy_relpath="reference/eia/consumer-energy.yaml",
    grid_relpath="reference/eia/grid-profile.yaml",
    # toxics
    toxic_corridor_bbox=(40.695, 40.725, -84.140, -84.105),
    receiving_water_name="Ottawa River",
    # balance
    plant_receiving={
        "watch-american-ii-wwtp": ("Dug Run", "Ohio EPA fact sheet 2PH00006 (American II WWTP)"),
        "watch-american-bath-wwtp": (
            "Pike Run",
            "Ohio EPA fact sheet 2PH00007 (American Bath WWTP)",
        ),
        "watch-shawnee-ii-wwtp": (
            "Ottawa River",
            "Ohio EPA fact sheet 2PK00002 (Shawnee II WWTP)",
        ),
    },
    abstraction_gage="04187100",
    # refill (primary = Auglaize @ Fort Jennings; secondary = Ottawa @ Lima)
    supply_gage_primary="04186500",
    supply_gage_secondary="04187100",
    passby_primary_cfs=2.5,
    passby_secondary_cfs=0.2,
    # grid
    lmp_usd_mwh=35.0,
    lmp_citation=(
        "PJM Data Miner 2 da_hrl_lmps, AEP zone ~2024 annual average ($/MWh); "
        "transcribed published figure - verify (regenerate via PJM Data Miner 2)"
    ),
    # rsei
    county_name="Allen County, OH",
    # map
    map_view_lat=40.792,
    map_view_lon=-84.122,
    map_view_zoom=14,
)


# The first cohort watershed point (#237): Findlay, OH on the Blanchard River (a Maumee
# tributary via the Auglaize). A *coming-soon* point — its watershed identity is sourced and
# cited below; the facility-specific model inputs (the development land-cover scenario, the
# toxics corridor, per-WWTP receiving waters, the refill supply gages + passby minimums) stay
# `TODO` until an actual data-center development site is identified — that's the data-center
# dimension onboard does not capture, and `bosc onboard findlay --check` tracks the gaps.
# Provenance tags inline: [verified] cited primary source; [inference] grounded reasoning;
# [reference] authoritative dataset; [open] genuinely unsourced (a known lift / pending a site).
_FINDLAY = SiteProfile(
    slug="findlay",
    place="Findlay",
    basin="maumee",  # [verified] Blanchard R. → Auglaize → Maumee → Lake Erie; HUC-8 04100008
    # config knobs
    nwis_sites=[
        "04189000",  # [verified] Blanchard River near Findlay OH (primary, active since 1990; 346 sq mi)
        "04188496",  # [verified] Eagle Creek above Findlay OH (water-quality super-gage; ~51 sq mi)
    ],
    nasa_power_lat=41.0428,  # [verified] Findlay city centroid (Census Gazetteer place 3927048)
    nasa_power_lon=-83.6422,
    rsei_fips="39063",  # [verified] Hancock County, OH
    econ_fips="39063",
    eia861_utility_number=14006,  # [verified] Ohio Power Co (AEP Ohio); no municipal electric utility
    eia_state="OH",
    # GIS (the known lift — a new jurisdiction needs its own connector; see docs/onboarding.md):
    parcels_url="TODO",  # [open] no public ArcGIS REST parcels — Hancock County is Beacon/Schneider-only; substitute = Ohio statewide parcels (geohio) filtered to 39063
    zoning_url=(  # [verified] City of Findlay hosted zoning FeatureServer (ArcGIS Online org XMr9uonP553LyU3o)
        "https://services6.arcgis.com/XMr9uonP553LyU3o/arcgis/rest/services/FindlayZoning/FeatureServer/0"
    ),
    floodzone_url="TODO",  # [open] no City flood REST service — source is FEMA NFHL S_FLD_HAZ_AR (needs its own connector)
    gnis_default_state="OH",
    hydro_utm_epsg=32617,  # [verified] UTM 17N (Findlay ~83.64degW; zone 17 spans 84-78degW)
    lsc_default_ga="136",  # [verified] Ohio 136th General Assembly (2025-2026); state-level, shared with Lima
    # stormwater (the Atlas-14 corridor point = city centroid; cover scenario pending a site)
    design_lat=41.0428,  # [verified] city centroid = NOAA Atlas-14 point
    design_lon=-83.6422,
    dominant_hsg="D",  # [inference] Great Black Swamp very-poorly-drained clays (Hoytville/Pewamo) → HSG D
    hsg_citation=(
        "Hancock County, OH (NRCS area OH063) dominant hydrologic soil group D — very-poorly-"
        "drained Great Black Swamp clays (Hoytville/Pewamo); NRCS Soil Survey of Hancock County "
        "2006 + Hoytville OSD; [inference] pending an SSURGO area-weighted confirmation"
    ),
    pre_cover="TODO",  # [open] development land-cover scenario — pending an identified site
    post_cover="TODO",
    developed_pervious_cover="TODO",
    noaa_fallback_24h_depth_in={  # [reference] NOAA Atlas-14 Vol 2 v3 (Ohio River Basin) PDS at 41.0428/-83.6422
        1: 2.04,
        2: 2.44,
        5: 3.01,
        10: 3.48,
        25: 4.14,
        50: 4.69,
        100: 5.26,
        200: 5.87,
        500: 6.72,
        1000: 7.42,
    },
    parcels_relpath="reference/findlay/bosc-parcels.geojson",  # [open] commit the site's own geometry
    footprint_relpath="extracted/findlay/bosc-site-footprint.yaml",  # [open] pending an identified site
    # per-site onboard reach outputs (slug-scoped — never clobber Lima)
    climatology_relpath="reference/hydrology/findlay/nasa-power-climatology.yaml",
    corridor_ddf_relpath="reference/hydrology/findlay/atlas14-corridor-ddf.yaml",
    baseline_relpath="reference/economics/findlay/baseline.yaml",
    rsei_relpath="reference/rsei/findlay/inventory.yaml",
    consumer_energy_relpath="reference/eia/findlay/consumer-energy.yaml",
    grid_relpath="reference/eia/findlay/grid-profile.yaml",
    # toxics (no identified industrial corridor yet)
    toxic_corridor_bbox=(
        0.0,
        0.0,
        0.0,
        0.0,
    ),  # [open] pending an identified corridor on the Blanchard
    receiving_water_name="Blanchard River",  # [verified]
    # balance (per-WWTP receiving waters pending the site's NPDES fact sheets)
    plant_receiving={},  # [open] pending Findlay-area WWTP NPDES fact sheets
    abstraction_gage="04189000",  # [inference] the primary Blanchard gage near Findlay
    # refill (the water-balance supply model is not yet designed for Findlay)
    supply_gage_primary="TODO",  # [open] refill supply gage — pending the site's water-balance model
    supply_gage_secondary="TODO",
    passby_primary_cfs=0.0,  # [open] in-stream passby minimums — pending the model
    passby_secondary_cfs=0.0,
    # grid (same PJM AEP zone as Lima — Ohio Power Co)
    lmp_usd_mwh=35.0,  # [inference] shared AEP-zone value with Lima (same utility/zone)
    lmp_citation=(
        "PJM AEP zone (Ohio Power Co) ~2024 annual average LMP ($/MWh) via PJM Data Miner 2 "
        "da_hrl_lmps; same zone as Lima — shared zone value, verify (regenerate via Data Miner 2)"
    ),
    # rsei
    county_name="Hancock County, OH",  # [verified]
    # map
    map_view_lat=41.0428,
    map_view_lon=-83.6422,
    map_view_zoom=13,
)


SITES: dict[str, SiteProfile] = {_LIMA.slug: _LIMA, _FINDLAY.slug: _FINDLAY}

# The per-site output relpaths `bosc onboard` writes. Each must be unique to its site so
# onboarding never overwrites another site's committed data — a profile that copies Lima
# without slug-scoping these would otherwise clobber Lima's files (#326 hardening).
PER_SITE_OUTPUT_FIELDS: tuple[str, ...] = (
    "climatology_relpath",
    "corridor_ddf_relpath",
    "baseline_relpath",
    "rsei_relpath",
    "consumer_energy_relpath",
    "grid_relpath",
)


def get_profile(slug: str) -> SiteProfile:
    """The :class:`SiteProfile` for ``slug``; raises ``KeyError`` if unknown."""
    return SITES[slug]


def active_profile(settings: Settings) -> SiteProfile:
    """The active site's profile, keyed by ``settings.site``."""
    return SITES[settings.site]


def output_path_collisions(slug: str) -> dict[str, list[str]]:
    """Other registered sites that share ``slug``'s per-site output relpaths.

    Returns ``{field: [other_slug, …]}`` for each :data:`PER_SITE_OUTPUT_FIELDS` value
    another site also uses — empty when ``slug``'s outputs are safely unique.
    """
    prof = SITES[slug]
    clashes: dict[str, list[str]] = {}
    for field in PER_SITE_OUTPUT_FIELDS:
        value = getattr(prof, field)
        others = [s for s, p in SITES.items() if s != slug and getattr(p, field) == value]
        if others:
            clashes[field] = others
    return clashes


# --- Authoring tooling (scaffold a new profile + lint a draft) ------------------------------
# Geometry inputs a new site supplies itself (not connector outputs, so not in
# PER_SITE_OUTPUT_FIELDS, but still slug-scoped by the scaffold).
_GEOMETRY_RELPATH_FIELDS = ("parcels_relpath", "footprint_relpath")


def _slug_scope(relpath: str, slug: str) -> str:
    """Insert ``slug`` as a subdir before the filename (Lima's path -> a new site's)."""
    p = PurePosixPath(relpath)
    return str(p.parent / slug / p.name)


def _type_placeholder(annotation: object) -> str:
    """A constructible-but-obviously-empty literal for a field's type (scaffold TODO)."""
    origin = get_origin(annotation)
    if annotation is str:
        return '"TODO"'
    if annotation is bool:
        return "False"
    if annotation is int:
        return "0"
    if annotation is float:
        return "0.0"
    if origin is list:
        return '["TODO"]'
    if origin is tuple:
        n = len([a for a in get_args(annotation) if a is not Ellipsis])
        return "(" + ", ".join(["0.0"] * n) + ")"
    if origin is dict:
        return "{}"
    return "None"


def scaffold_profile_src(slug: str, *, basin: str = "maumee") -> str:
    """A paste-ready ``SiteProfile(...)`` stub for a new site (the #326 authoring aid).

    Identity + the per-site output relpaths are filled (the relpaths pre-slug-scoped, so the
    stub is collision-safe by construction); every other field is a typed ``TODO`` placeholder
    to replace from a cited source (see ``docs/onboarding.md``). Then ``bosc sites check`` flags
    anything still unfilled.
    """
    lima = SITES["lima"]
    lines: list[str] = [f'    "{slug}": SiteProfile(']
    for name, field in SiteProfile.model_fields.items():
        comment = ""
        if name == "slug":
            value = repr(slug)
        elif name == "basin":
            value = repr(basin)
            comment = "  # TODO: confirm the basin"
        elif name in PER_SITE_OUTPUT_FIELDS:
            value = repr(_slug_scope(getattr(lima, name), slug))  # pre-slug-scoped, collision-safe
        elif name in _GEOMETRY_RELPATH_FIELDS:
            stem = "reference" if name == "parcels_relpath" else "extracted"
            value = repr(f"{stem}/{slug}/{PurePosixPath(getattr(lima, name)).name}")
            comment = "  # TODO: commit the site's own geometry here"
        else:
            value = _type_placeholder(field.annotation)
            comment = "  # TODO"
        lines.append(f"        {name}={value},{comment}")
    lines.append("    ),")
    header = (
        f"# Paste into bosc.sites.SITES (the key must equal slug={slug!r}). Replace every TODO\n"
        "# with this site's value from a cited source — see the field guide in\n"
        "# docs/onboarding.md. The output relpaths are pre-slug-scoped (collision-safe);\n"
        f"# run `bosc onboard {slug} --check` to find anything still unfilled.\n"
    )
    return header + "\n".join(lines) + "\n"


class ReadinessFinding(BaseModel):
    """One issue a draft profile lints up before a live onboard run."""

    model_config = ConfigDict(extra="forbid")

    field: str
    kind: Literal["placeholder", "matches-lima"]
    detail: str


def _is_placeholder(value: object) -> bool:
    """True for the scaffold's unfilled sentinels (TODO / zeros / empties)."""
    if isinstance(value, str):
        return value == "" or "TODO" in value
    if isinstance(value, bool):
        return False
    if isinstance(value, (int, float)):
        return value == 0
    if isinstance(value, (list, tuple)):
        return len(value) == 0 or any(_is_placeholder(v) for v in value)
    if isinstance(value, dict):
        return len(value) == 0
    return value is None


def profile_readiness(slug: str) -> list[ReadinessFinding]:
    """Lint a non-Lima draft profile before onboarding: unfilled placeholders + copied values.

    Flags any field still a scaffold placeholder (``placeholder`` — must fix) and any field
    still equal to Lima's value (``matches-lima`` — verify; some, e.g. an Ohio site's
    ``eia_state``, legitimately match). Empty for Lima itself.
    """
    if slug == "lima":
        return []
    prof, lima = SITES[slug], SITES["lima"]
    findings: list[ReadinessFinding] = []
    for name in SiteProfile.model_fields:
        if name == "slug":
            continue
        value = getattr(prof, name)
        if _is_placeholder(value):
            findings.append(
                ReadinessFinding(
                    field=name, kind="placeholder", detail=f"still unfilled: {value!r}"
                )
            )
        elif value == getattr(lima, name):
            findings.append(
                ReadinessFinding(
                    field=name, kind="matches-lima", detail=f"== Lima's value: {value!r}"
                )
            )
    return findings
