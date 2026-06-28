"""Site-profile data models for the BOSC network registry.

Split out of the former monolithic ``sites.py`` (#597). Re-exported by the package
:mod:`watermark.sites` ``__init__`` so ``watermark.sites.SiteProfile`` / ``SiteFacility`` /
``PROFILE_SETTINGS_FIELDS`` are unchanged for callers.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict

from watermark.connectors.gis_schema import GisFloodSchema, GisParcelSchema, GisZoningSchema


class SiteFacility(BaseModel):
    """A site's disclosed data-center facility power basis (air-permit-grounded).

    Present only for a site with an identified, documented facility (Lima, from Ohio EPA
    Air PTI P0138965). A site with no such facility leaves ``SiteProfile.facility = None`` —
    the grid stack then emits the per-site grid backdrop (utility / BA / state denominators)
    **without** fabricating a campus load share. Drives :func:`watermark.facility.power.derive_power_basis`.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    genset_count: int  # emergency gensets disclosed in the air permit
    genset_mw: float  # ekW each
    it_load_mw: float  # central IT load (N+1 backup ~= IT)
    it_load_low_mw: float  # low end of the N+1 range
    it_load_high_mw: float  # high end
    air_permit_citation: str  # the disclosing permit + committed extraction
    # Disclosed cooling/industrial blowdown discharge — the independent cross-check for the
    # cooling back-solve (:func:`watermark.hydrology.cooling.derive_cooling_basis`, method 2). Per-site
    # (#607): a site that doesn't disclose one leaves these None and the back-solve uses the
    # site's own power-derived consumptive as the high bound (no Lima FM-2 leak).
    blowdown_mgd: float | None = None
    blowdown_citation: str | None = None


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
    eia_state: str = "OH"  # the network is Ohio-dominant; only non-OH sites (Fort Wayne) override
    # County/City GIS layer endpoints — per-site. The connector code that reads them is now
    # jurisdiction-agnostic: the field names + encodings live in the gis_* schemas below (#237).
    parcels_url: str
    zoning_url: str
    floodzone_url: str
    gnis_default_state: str = "OH"  # only non-OH sites (Fort Wayne) override
    hydro_utm_epsg: int
    # Ohio LSC General Assembly (statusreport.lsc.ohio.gov is Ohio-only); "" disables the
    # connector for an out-of-state site (Fort Wayne). Ohio sites share the 136th GA.
    lsc_default_ga: str = "136"

    # --- GIS layer field-maps (jurisdiction schemas; #237) ------------------------------
    # The ArcGIS field names + value encodings the GIS connectors read, lifted off Lima/Allen
    # so a new jurisdiction is config, not a copied connector (mirrors the OPC Profile idiom).
    # Optional: ``None`` means "no connector for this layer here yet" — the connector/CLI then
    # refuses cleanly rather than querying another jurisdiction's fields. Read via
    # ``active_profile`` (NOT in PROFILE_SETTINGS_FIELDS — never bled into Settings).
    gis_parcel: GisParcelSchema | None = None
    gis_zoning: GisZoningSchema | None = None
    gis_flood: GisFloodSchema | None = None

    # --- Stormwater design point + cited assumptions (hydrology/stormwater.py) -----------
    # The NOAA-Atlas-14 corridor point — distinct from the nasa_power loop centroid above.
    design_lat: float
    design_lon: float
    corridor_name: str  # the Atlas-14 design-storm corridor label (drainage.py meta.subject)
    dominant_hsg: str
    hsg_citation: str
    pre_cover: str
    post_cover: str
    developed_pervious_cover: str
    noaa_fallback_24h_depth_in: dict[int, float]
    parcels_relpath: str  # relative to settings.data_dir
    footprint_relpath: str  # relative to settings.data_dir
    # The frozen external-corroboration corridor geometry dir (corridor.geojson +
    # corridor-centerline.geojson), relative to settings.data_dir — folded into the GIS
    # findings by site/gismap.merge_corridor_layer. ``None`` = no corridor layer for this
    # site (the merge then emits nothing rather than reading another site's geometry).
    corridor_geo_relpath: str | None = None

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

    # --- Grid / facility (grid/*.py, facility/power.py) ---------------------------------
    # The disclosed DC facility (None = no identified facility yet → grid backdrop only, no
    # fabricated campus load share). The serving-utility *identity* (name) is connector-sourced
    # (EIA-861); only its provenance is per-site: a corpus document for Lima, the EIA-861/PUCO
    # service-territory record for a site without corpus coverage.
    facility: SiteFacility | None = None
    serving_utility_citation: str
    # Default "reference" (EIA-861/PUCO service-territory record); only a corpus-grounded site
    # (Lima, from its air permit) overrides to "document".
    serving_utility_source: Literal["document", "connector", "reference", "assumption"] = (
        "reference"
    )

    # --- Grid market (grid/market.py) ---------------------------------------------------
    lmp_usd_mwh: float  # zonal day-ahead LMP fallback (connector-sourced when lmp_pnode_id is set)
    lmp_citation: str
    # The site's PJM pricing zone for the live LMP connector (grid/lmp.py, #121). When pinned,
    # the connector's zonal day-ahead mean overrides lmp_usd_mwh; 0/"" leaves the placeholder
    # (e.g. Bryan/AMP #411, Fort Wayne/I&M #361 — zones not yet pinned). AEP=8445784, ATSI=116013753.
    lmp_pnode_id: int = 0
    lmp_pnode_name: str = ""

    # --- Corpus scope — the content bundle's extracted-tree feeds (#762) -----------------
    # The ``data/extracted/**`` collection prefixes that hold THIS site's records. The bundle's
    # corpus-derived feeds (records/timeline/entities/relationships, via ``load_corpus`` +
    # ``load_records``) read only artifacts whose rel-path is under one of these prefixes, so a
    # non-Lima site never inherits Lima's deeds/permits/filings/meetings. A prefix is a path
    # segment, so it spans both a slug-named collection (``"fort-wayne"``) and a jurisdiction+site
    # hybrid (``"idem/fort-wayne"``). ``None`` = the whole extracted tree — Lima, the reference
    # build that owns the un-slugged Allen-County-OH collections (keeps its bundle byte-identical).
    corpus_relpaths: tuple[str, ...] | None = None

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
