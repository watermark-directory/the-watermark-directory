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
``.site`` accessor — so the dependency runs one way (``config → sites``). The GIS field-map
*models* come from :mod:`bosc.connectors.gis_schema` (a pure-pydantic leaf under the neutral
connectors package, deliberately *not* ``bosc.hydrology.connectors``, which would close a
``config → sites → connectors → config`` loop); the schema *instances* live here with the
profiles, where site-specific values belong.
"""

from __future__ import annotations

from pathlib import PurePosixPath
from typing import TYPE_CHECKING, Literal, get_args, get_origin

from pydantic import BaseModel, ConfigDict

from bosc.connectors.gis_schema import (
    GisCitedZoningMeta,
    GisDefenseConfig,
    GisDefenseMeta,
    GisFloodSchema,
    GisMeta,
    GisParcelSchema,
    GisZoningSchema,
)

if TYPE_CHECKING:
    from bosc.config import Settings


class SiteFacility(BaseModel):
    """A site's disclosed data-center facility power basis (air-permit-grounded).

    Present only for a site with an identified, documented facility (Lima, from Ohio EPA
    Air PTI P0138965). A site with no such facility leaves ``SiteProfile.facility = None`` —
    the grid stack then emits the per-site grid backdrop (utility / BA / state denominators)
    **without** fabricating a campus load share. Drives :func:`bosc.facility.power.derive_power_basis`.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    genset_count: int  # emergency gensets disclosed in the air permit
    genset_mw: float  # ekW each
    it_load_mw: float  # central IT load (N+1 backup ~= IT)
    it_load_low_mw: float  # low end of the N+1 range
    it_load_high_mw: float  # high end
    air_permit_citation: str  # the disclosing permit + committed extraction


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
    # County/City GIS layer endpoints — per-site. The connector code that reads them is now
    # jurisdiction-agnostic: the field names + encodings live in the gis_* schemas below (#237).
    parcels_url: str
    zoning_url: str
    floodzone_url: str
    gnis_default_state: str
    hydro_utm_epsg: int
    lsc_default_ga: str

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
    serving_utility_source: Literal["document", "connector", "reference", "assumption"]

    # --- Grid market (grid/market.py) ---------------------------------------------------
    lmp_usd_mwh: float  # zonal day-ahead LMP fallback (connector-sourced when lmp_pnode_id is set)
    lmp_citation: str
    # The site's PJM pricing zone for the live LMP connector (grid/lmp.py, #121). When pinned,
    # the connector's zonal day-ahead mean overrides lmp_usd_mwh; 0/"" leaves the placeholder
    # (e.g. Bryan/AMP #411, Fort Wayne/I&M #361 — zones not yet pinned). AEP=8445784, ATSI=116013753.
    lmp_pnode_id: int = 0
    lmp_pnode_name: str = ""

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


# --- GIS field-map schema constants (#237) -------------------------------------------------
# Lima's schemas reproduce the pre-#237 hardcoded field names / encodings / write-meta prose
# exactly (zero-drift): the connector emits the identical request params, so the committed
# fixtures replay and the committed reference YAML stays byte-identical. See tests/test_sites.py
# for the schema golden + param-stability tests. NATIONAL_NFHL_FLOOD_SCHEMA / FINDLAY_* are
# defined just below, from a live FeatureServer metadata read (never fabricated field names).

# Allen County, OH parcel/CAMA layer (was allen_gis._OUT_FIELDS + the inline write-meta).
LIMA_PARCEL_SCHEMA = GisParcelSchema(
    connector="allen_gis",
    reference_dir="allen-gis",
    page_size=1000,
    out_fields=(
        "PARCEL_NO",
        "OWNNAM1",
        "OWNNAM2",
        "DEEDOWN",
        "HOUSENO",
        "ST_DIR",
        "STREET",
        "ST_DESC",
        "OWNADR1",
        "OWNADR2",
        "OWNST",
        "OWNZIP",
        "LNDUSECD",
        "ACRES",
        "MKTLNDVAL",
        "MKTIMPVAL",
        "MKTTOTVAL",
        "CAUVVAL",
        "TAXDIST",
        "SCHOOL",
        "NBRHCODE",
        "DATE",
        "SALEAMT",
        "VAL_SAL",
    ),
    id_field="PARCEL_NO",
    owner_field="OWNNAM1",
    owner_2_field="OWNNAM2",
    deeded_owner_field="DEEDOWN",
    situs_fields=("HOUSENO", "ST_DIR", "STREET", "ST_DESC"),
    owner_addr_fields=("OWNADR1", "OWNADR2"),
    land_use_field="LNDUSECD",
    acres_field="ACRES",
    market_land_field="MKTLNDVAL",
    market_improvement_field="MKTIMPVAL",
    market_total_field="MKTTOTVAL",
    cauv_field="CAUVVAL",
    tax_district_field="TAXDIST",
    school_field="SCHOOL",
    neighborhood_field="NBRHCODE",
    sale_date_field="DATE",
    sale_amount_field="SALEAMT",
    valid_sale_field="VAL_SAL",
    id_normalize="dashless",
    date_decode="mmddyyyy",
    deed_id_regex=r"\b\d{2}-\d{4}-\d{2}-\d{3}\.\d{3}\b",
    meta=GisMeta(
        subject="Allen County, Ohio parcels (CAMA)",
        source="Allen County GIS — ArcGIS REST, Current Parcels (AGOL_NonEditLayers/1)",
        source_url="https://gis.allencountyohio.com/arcgis/rest/services/AGOL/AGOL_NonEditLayers/MapServer/1",
        caveats=(
            "Values are verbatim from the county GIS; null means the service had no value.",
            "Market values are the auditor's appraised values, not sale prices.",
            "last_sale_date is decoded from the GIS M(M)DDYYYY integer; verify against the deed.",
        ),
    ),
    defense=GisDefenseConfig(
        owner_scan_fields=("OWNNAM1", "DEEDOWN", "OWNNAM2"),
        enclave_owner="UNITED STATES",
        enclave_tax_district="L35",
        meta=GisDefenseMeta(
            subject="Allen County, Ohio defense-industry land scan",
            source="Allen County GIS — ArcGIS REST, Current Parcels (AGOL_NonEditLayers/1)",
            source_url="https://gis.allencountyohio.com/arcgis/rest/services/AGOL/AGOL_NonEditLayers/MapServer/1",
            scan="Owner-name match of the curated DoD-prime seed list "
            "(data/entities/profiles/defense-contractors.yaml) against the CAMA "
            "owner / deeded-owner / second-owner fields.",
            finding="No Allen County parcel is owned by a DoD prime in its own name. "
            "The local defense footprint is the federally-held JSMC reservation below.",
            army_controlled_note="[inference] the UNITED STATES-owned cluster in tax "
            "district L35 on Buckeye/Reed Rd is the Joint Systems Manufacturing Center "
            "(Lima Army Tank Plant; 1151 Buckeye Rd), operated by General Dynamics Land "
            "Systems. Ownership is verbatim from the GIS; the JSMC identification is an "
            "analyst inference — verify against the deed/lease before relying on it.",
            caveats=(
                "Values are verbatim from the county GIS; null means the service had no value.",
                "A pattern match is a lead to verify, not a classification or accusation.",
            ),
        ),
    ),
)

# City of Lima, OH zoning layer (was lima_gis zoning fields + the inline write-meta/finding).
LIMA_ZONING_SCHEMA = GisZoningSchema(
    connector="lima_gis",
    reference_dir="lima-gis",
    page_size=10000,
    object_id_field="OBJECTID",
    parcel_field="PARCEL_NO",
    zoning_field="ZONING",
    http_method="POST",
    id_normalize="dashless",
    meta=GisMeta(
        subject="City of Lima, Ohio zoning districts (catalog)",
        source="City of Lima GIS — ArcGIS REST, CitywideMaps/Lima_Zoning, layer 6 'Current Lima Zoning'",
        source_url=(
            "https://colgis.cityhall.lima.oh.us/server/rest/services/"
            "CitywideMaps/Lima_Zoning/MapServer/6"
        ),
        caveats=(
            "Values are verbatim from the City of Lima GIS.",
            "Coverage is Lima CITY LIMITS ONLY; unincorporated Allen County parcels "
            "(e.g. the American Township corridor) are not in this layer.",
            "polygon_count counts zoning polygons, not distinct parcels (a parcel may "
            "carry more than one polygon).",
        ),
    ),
    cited_meta=GisCitedZoningMeta(
        subject="City of Lima zoning for cited corpus parcels (jurisdiction scan)",
        source="City of Lima GIS — ArcGIS REST, CitywideMaps/Lima_Zoning, layer 6, "
        "joined by PARCEL_NO to corpus-cited parcel ids",
        finding_lead="fall within the City of Lima zoning jurisdiction",
        in_city_finding=".",
        out_of_city_finding=" — the corridor (data-center campus + JSMC) sits in American/county "
        "townships, so it is NOT subject to the City of Lima zoning code. Allen County "
        "GIS publishes no county/township zoning layer (only Tax and School districts), "
        "so land-use authority here is township/county, not GIS-mapped.",
        caveats=(
            "Coverage is Lima CITY LIMITS ONLY; in_city=false is a verified outside-"
            "city result, not a missing lookup.",
            "Parcel ids are scanned from data/extracted; normalized to the dashless "
            "PARCEL_NO the GIS join uses.",
        ),
    ),
)

# FEMA DFIRM floodzone layer as served by the City of Lima GIS (was lima_gis flood fields).
LIMA_FLOOD_SCHEMA = GisFloodSchema(
    connector="lima_gis_flood",
    reference_dir="lima-gis",
    page_size=10000,
    object_id_field="OBJECTID",
    fld_zone_field="FLD_ZONE",
    zone_subtype_field="ZONE_SUBTY",
    sfha_field="SFHA_TF",
    static_bfe_field="STATIC_BFE",
    dfirm_id_field="DFIRM_ID",
    source_cit_field="SOURCE_CIT",
    http_method="POST",
    bfe_sentinel=-9999.0,
    sfha_true_value="T",
    meta=GisMeta(
        subject="FEMA flood-hazard zones over Allen County (DFIRM panel 39003C)",
        source="City of Lima GIS — ArcGIS REST, CitywideMaps/Lima_Zoning, layer 4 'Floodzone' (FEMA DFIRM)",
        source_url=(
            "https://colgis.cityhall.lima.oh.us/server/rest/services/"
            "CitywideMaps/Lima_Zoning/MapServer/4"
        ),
        caveats=(
            "Values are verbatim from the FEMA DFIRM served by the City of Lima GIS.",
            "Only Special Flood Hazard Areas (1%-annual-chance: A/AE incl. floodway, AO) "
            "are mapped here; areas outside the SFHA carry no polygon.",
            "A site's flood zone is a SPATIAL question (no PARCEL_NO on this layer) — use "
            "footprint_floodzones() / bosc floodzone --footprint.",
        ),
    ),
)

# The national FEMA NFHL flood layer (S_FLD_HAZ_AR) — the shared, any-US-site flood field-map.
# A site without a local flood REST service points its floodzone_url at this MapServer layer
# and references this schema (overriding reference_dir per site). Field names confirmed from the
# layer metadata 2026-06-19 (they match the FEMA DFIRM standard). Lima keeps its own City-served
# DFIRM schema for zero-drift; it is NOT migrated onto NFHL here (that would change request params).
NATIONAL_NFHL_FLOOD_SCHEMA = GisFloodSchema(
    connector="nfhl_flood",
    reference_dir="nfhl",
    page_size=2000,
    object_id_field="OBJECTID",
    fld_zone_field="FLD_ZONE",
    zone_subtype_field="ZONE_SUBTY",
    sfha_field="SFHA_TF",
    static_bfe_field="STATIC_BFE",
    dfirm_id_field="DFIRM_ID",
    source_cit_field="SOURCE_CIT",
    http_method="POST",
    bfe_sentinel=-9999.0,
    sfha_true_value="T",
    meta=GisMeta(
        subject="FEMA flood-hazard zones (National Flood Hazard Layer, S_FLD_HAZ_AR)",
        source="FEMA NFHL — ArcGIS REST, public/NFHL/MapServer/28 'Flood Hazard Zones'",
        source_url="https://hazards.fema.gov/arcgis/rest/services/public/NFHL/MapServer/28",
        caveats=(
            "Values are verbatim from the FEMA National Flood Hazard Layer (NFHL).",
            "Only Special Flood Hazard Areas (1%-annual-chance: A/AE incl. floodway, AO) "
            "are mapped; areas outside the SFHA carry no polygon.",
            "A site's flood zone is a SPATIAL question (no parcel id on this layer) — use "
            "footprint_floodzones() / bosc floodzone --footprint.",
            "Field names confirmed from the NFHL layer-28 metadata (2026-06-19).",
        ),
    ),
)

# City of Findlay, OH zoning — a hosted ArcGIS Online FeatureServer. Field names confirmed live
# from the layer-0 metadata 2026-06-19: it is POLYGON-ONLY (no parcel-id field), so the district
# catalog is supported but per-parcel zoning joins are not (cited_meta=None).
FINDLAY_ZONING_SCHEMA = GisZoningSchema(
    connector="findlay_gis",
    reference_dir="findlay-gis",
    page_size=2000,
    object_id_field="FID",
    parcel_field=None,  # polygon-only layer — no parcel id to join on
    zoning_field="Zoning",  # current district label (Category = coarse group; OLDZONING = prior)
    http_method="POST",
    id_normalize="dashless",
    meta=GisMeta(
        subject="City of Findlay, Ohio zoning districts (catalog)",
        source="City of Findlay GIS — ArcGIS Online hosted FeatureServer 'FindlayZoning' "
        "(org XMr9uonP553LyU3o), layer 0",
        source_url=(
            "https://services6.arcgis.com/XMr9uonP553LyU3o/arcgis/rest/services/"
            "FindlayZoning/FeatureServer/0"
        ),
        caveats=(
            "Values are verbatim from the City of Findlay hosted zoning FeatureServer.",
            "Polygon-only layer (no parcel id): the district catalog is supported; per-parcel "
            "zoning joins are not.",
            "Field names confirmed from the layer-0 metadata (2026-06-19).",
        ),
    ),
)


# The OGRIP "Ohio Statewide Parcels Public View" — the shared parcel substitute for any Ohio
# watershed point whose county has no public parcel ArcGIS REST of its own (#237 Findlay follow-up).
# It is one statewide layer, so each site filters it to its county via `query_scope` (e.g.
# `County='Hancock'`), with a site-scoped `reference_dir`, exactly like NATIONAL_NFHL_FLOOD_SCHEMA.
# It is a deliberately PARTIAL fit: the public view is owner-name-redacted (owner appears only
# inside the mailing label, so owner_field is empty and owner searches refuse cleanly), land use is
# a "<code>: <label>" string (decoded leading_int), and there are no market/CAUV/sale/tax fields.
# What it does give, cleanly: the parcel id, situs address, land use code, acreage, and geometry —
# i.e. the parcel catalog + the resolve-to-parcel funnel. Field names confirmed from the live
# layer-0 metadata + a Hancock sample (2026-06-20). Never run an owner/defense scan against it.
OHIO_STATEWIDE_PARCEL_SCHEMA = GisParcelSchema(
    connector="ohio_parcels",
    reference_dir="ohio-parcels",  # per-site override (e.g. "findlay-gis")
    page_size=2000,
    out_fields=(
        "OBJECTID",
        "County",
        "LocalParcelID",
        "StateParcelID",
        "StateLUC",
        "SitusAddressAll",
        "MailAddressAll",
        "LandArea",
    ),
    id_field="LocalParcelID",  # the county-local parcel number (dashless digits)
    owner_field="",  # owner-redacted in the public view (only embedded in the mailing label)
    owner_2_field="",
    deeded_owner_field="",
    situs_fields=("SitusAddressAll",),  # a single pre-assembled situs string
    owner_addr_fields=("MailAddressAll",),  # the mailing label (recipient + city + zip)
    land_use_field="StateLUC",
    acres_field="LandArea",
    market_land_field="",  # absent in this layer -> None (never fabricated)
    market_improvement_field="",
    market_total_field="",
    cauv_field="",
    tax_district_field="",
    school_field="",
    neighborhood_field="",
    sale_date_field="",
    sale_amount_field="",
    valid_sale_field="",
    id_normalize="dashless",
    date_decode="none",
    land_use_decode="leading_int",  # "511: Res-Custom Code" -> 511
    query_scope="",  # set per site (e.g. "County='Hancock'") — base is unscoped (never queried bare)
    deed_id_regex=r"\b\d{12}\b",  # Hancock LocalParcelID is 12 dashless digits (stored; no corpus scan)
    meta=GisMeta(
        subject="Ohio statewide parcels (OGRIP public view), scoped per county",
        source="OGRIP — Ohio Statewide Parcels Public View (owner ogrip_agol), FeatureServer layer 0",
        source_url=(
            "https://services2.arcgis.com/MlJ0G8iWUyC7jAmu/arcgis/rest/services/"
            "OhioStatewidePacels_full_view/FeatureServer/0"
        ),
        caveats=(
            "OGRIP statewide compilation of county parcels; currency varies by county (CurrentTo).",
            "The public view is owner-name-redacted: no owner field (only the mailing label in "
            "MailAddressAll); no market/CAUV value, sale, or tax-district fields.",
            "Land use is a '<code>: <label>' string (StateLUC); the numeric code is parsed out.",
            "Field names confirmed from the live layer-0 metadata + a Hancock sample (2026-06-20).",
        ),
    ),
)


# Putnam County, OH parcels (Ottawa watershed point; #420). Putnam self-hosts a valid-cert ArcGIS
# (`putnamcountygis.com`) whose `Parcels` layer carries owner AND auditor CAMA values on one layer —
# the full fit Findlay's owner-redacted OGRIP substitute can't give. Field names confirmed from the
# live layer-0 `?f=json` + samples (2026-06-21). Notes: OWNER holds the whole owner string (no
# separate second/deeded-owner field); OWNERC/OWNERD are the property situs (an owner may mail to a
# different state — verified against a parcel whose mailing city is The Woodlands, TX); MAILC/MAILD
# are the owner's mailing address; the populated land-use code lives in CLASS_1 (the `Class` field is
# 0/unused here); LANDVALUE/BLDGVALUE are the auditor's land/building values with no combined-total
# field; SALEDATE is a MM-DD-YY string (date_decode="mmddyy"). No CAUV/school/neighborhood/tax-
# district/valid-sale fields on this layer (they stay absent → None, never fabricated); CAUV + the
# full appraisal split live on the separate LandUseParcels CAMA layer, not joined here.
PUTNAM_PARCEL_SCHEMA = GisParcelSchema(
    connector="putnam_gis",
    reference_dir="ottawa-gis",
    page_size=1000,
    out_fields=(
        "PIN",
        "OWNER",
        "OWNERC",
        "OWNERD",
        "MAILC",
        "MAILD",
        "CLASS_1",
        "ACRESOWNED",
        "LANDVALUE",
        "BLDGVALUE",
        "SALEDATE",
        "PURPRI",
    ),
    id_field="PIN",  # 12-digit zero-padded parcel id string (PARCELNUM is the same digits as a float)
    owner_field="OWNER",
    owner_2_field="",  # no separate second-owner field (OWNER carries the full string)
    deeded_owner_field="",  # no separate deeded-owner field
    situs_fields=("OWNERC", "OWNERD"),  # the property situs (location + city/state/zip)
    owner_addr_fields=(
        "MAILC",
        "MAILD",
    ),  # the owner's mailing address (may be out of county/state)
    land_use_field="CLASS_1",  # the populated 3-digit Ohio use code (`Class` is 0/unused here)
    acres_field="ACRESOWNED",
    market_land_field="LANDVALUE",
    market_improvement_field="BLDGVALUE",
    market_total_field="",  # no combined-total field on this layer (never summed/fabricated)
    cauv_field="",  # CAUV lives on the separate LandUseParcels CAMA layer, not joined here
    tax_district_field="",
    school_field="",
    neighborhood_field="",
    sale_date_field="SALEDATE",  # MM-DD-YY string
    sale_amount_field="PURPRI",
    valid_sale_field="",  # PURCOD is a conveyance-type code, not a validity flag — left unmapped
    id_normalize="dashless",
    date_decode="mmddyy",
    deed_id_regex=r"\b\d{12}\b",  # 12 dashless digits (no Putnam corpus scan; pattern for parity)
    meta=GisMeta(
        subject="Putnam County, Ohio parcels (CAMA)",
        source="Putnam County GIS — ArcGIS REST, Parcels/Parcels layer 0 (auditor CAMA + geometry)",
        source_url="https://putnamcountygis.com/arcgis/rest/services/Parcels/Parcels/MapServer/0",
        caveats=(
            "Values are verbatim from the county GIS; null means the service had no value.",
            "Market values are the auditor's land/building appraised values; this layer has no "
            "combined total field, so market_total_value is always null (never summed here).",
            "Land use is the auditor's 3-digit Ohio use code in CLASS_1; the `Class` field is "
            "0/unused in this layer.",
            "OWNERC/OWNERD are the property situs; MAILC/MAILD the owner's (possibly out-of-state) "
            "mailing address.",
            "last_sale_date is decoded from the MM-DD-YY string with the standard %y century pivot "
            "(69-99 -> 1900s, 00-68 -> 2000s); verify the century against the deed near the pivot.",
            "Field names confirmed from the live layer-0 metadata + samples (2026-06-21).",
        ),
    ),
)


# Lucas County, OH parcels (Toledo watershed point; #384). Lucas County's AREIS is the richest GIS
# in the network: a full, valid-cert, self-hosted ArcGIS (lcaudgis.co.lucas.oh.us). The owner-bearing
# CAMA lives on AREIS_Web_Map_MIL1/MapServer layer 38 ("Parcels Land Use Classification"): one polygon
# layer carrying PARID + OWNER + PROPERTY_ADDRESS (situs) + MAILING_ADDRESS + LUC (use code) + ZONING
# + TAXDIST. This is the network's first owner-bearing parcel layer wired from a county's own REST
# (Putnam has owner+value but is a different host; Findlay/Bryan are OGRIP owner-redacted substitutes).
# Field names confirmed from the live layer-38 `?f=json` + Waterville-area samples (2026-06-21).
# NOTE: the auditor's appraised values (APRLAND/APRBLDG/APRTOT) are NOT on this layer — they live on
# layer 83 ("Land Values"), joined by PARID. The single-layer connector can't join, so market values
# stay null here; the PARID value-join is a tracked follow-up (the network's first multi-layer parcel
# connector). No sale-date/amount or CAUV fields on layer 38 either (absent -> None, never fabricated).
LUCAS_AREIS_PARCEL_SCHEMA = GisParcelSchema(
    connector="lucas_areis",
    reference_dir="toledo-gis",
    page_size=2000,
    out_fields=(
        "PARID",
        "OWNER",
        "PROPERTY_ADDRESS",
        "MAILING_ADDRESS",
        "LUC",
        "ACREAGE",
        "TAXDIST",
    ),
    id_field="PARID",  # AREIS parcel id (plain digits, e.g. "3850130")
    owner_field="OWNER",
    owner_2_field="",  # no separate second-owner field on this layer
    deeded_owner_field="",
    situs_fields=(
        "PROPERTY_ADDRESS",
    ),  # a single pre-assembled situs string ("... , WATERVILLE OH 43566")
    owner_addr_fields=("MAILING_ADDRESS",),  # the pre-assembled owner mailing address
    land_use_field="LUC",  # the auditor's land-use code (bare numeric string, e.g. "550")
    acres_field="ACREAGE",
    market_land_field="",  # appraised values are on layer 83 (PARID join) — deferred follow-up
    market_improvement_field="",
    market_total_field="",
    cauv_field="",  # CAUV split is a separate AREIS layer, not joined here
    tax_district_field="TAXDIST",
    school_field="",
    neighborhood_field="",
    sale_date_field="",  # no sale date/amount on the land-use-classification layer
    sale_amount_field="",
    valid_sale_field="",
    id_normalize="dashless",  # PARID is plain digits; dashless tolerates a dotted/dashed input form
    date_decode="none",
    land_use_decode="int",  # bare numeric LUC code
    deed_id_regex=r"\b\d{7}\b",  # AREIS PARID is ~7 digits (no Toledo corpus scan; pattern for parity)
    meta=GisMeta(
        subject="Lucas County, Ohio parcels (AREIS CAMA — land-use classification)",
        source="Lucas County Auditor AREIS — ArcGIS REST, AREIS_Web_Map_MIL1/MapServer layer 38 "
        "('Parcels Land Use Classification')",
        source_url=(
            "https://lcaudgis.co.lucas.oh.us/gisaudserver/rest/services/"
            "AREIS_Web_Map_MIL1/MapServer/38"
        ),
        caveats=(
            "Values are verbatim from the county AREIS; null means the service had no value.",
            "Appraised values (APRLAND/APRBLDG/APRTOT) are NOT on this layer — they live on AREIS "
            "layer 83 (PARID join), so market_*_value is always null here (never fabricated).",
            "PROPERTY_ADDRESS is the situs; MAILING_ADDRESS the owner's mailing address; both are "
            "pre-assembled single strings.",
            "LUC is the auditor's numeric land-use code; CLASS (R/C/E/...) is the coarse use group.",
            "Field names confirmed from the live layer-38 metadata + samples (2026-06-21).",
        ),
    ),
)


# City of Toledo / Lucas County zoning (#384): the AREIS Parcel_Zoning layer — a PARCEL-level zoning
# catalog (PARID + ZONING), so unlike Findlay's polygon-only layer it supports the per-parcel join.
LUCAS_ZONING_SCHEMA = GisZoningSchema(
    connector="lucas_zoning",
    reference_dir="toledo-gis",
    page_size=2000,
    object_id_field="OBJECTID",
    parcel_field="PARID",  # parcel-level layer (supports zoning_for_parcel, unlike Findlay)
    zoning_field="ZONING",
    http_method="GET",
    id_normalize="dashless",
    meta=GisMeta(
        subject="Lucas County / City of Toledo zoning districts (catalog)",
        source="Lucas County Auditor AREIS — ArcGIS REST, LandUse_Zoning/Parcel_Zoning/MapServer "
        "layer 0 ('Parcels Zoning')",
        source_url=(
            "https://lcaudgis.co.lucas.oh.us/gisaudserver/rest/services/"
            "LandUse_Zoning/Parcel_Zoning/MapServer/0"
        ),
        caveats=(
            "Values are verbatim from the county AREIS Parcel_Zoning layer.",
            "ZONING is the parcel-level district code (a jurisdiction prefix + district, e.g. "
            "'17-R3'); coverage is county-wide across Lucas jurisdictions, not Toledo city-only.",
            "polygon_count counts zoning polygons, not distinct parcels.",
            "Field names confirmed from the live layer metadata + samples (2026-06-21).",
        ),
    ),
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
    # GIS field-maps (Allen County parcels + City of Lima zoning/floodzone)
    gis_parcel=LIMA_PARCEL_SCHEMA,
    gis_zoning=LIMA_ZONING_SCHEMA,
    gis_flood=LIMA_FLOOD_SCHEMA,
    # stormwater
    design_lat=40.797,
    design_lon=-84.123,
    corridor_name="Cole St / Bluelick corridor",
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
    # grid / facility (the disclosed Lima campus; serving-utility provenance = the corpus)
    facility=SiteFacility(
        genset_count=114,
        genset_mw=2.75,  # ekW each, per the air permit
        it_load_mw=275.0,  # midpoint of the 250-300 MW estimate (IT ~= backup at N+1)
        it_load_low_mw=250.0,
        it_load_high_mw=300.0,
        air_permit_citation=(
            "OEPA Air PTI P0138965 (Facility 0302022054), committed "
            "data/extracted/permits/4132514.epa.yaml (final, 2026-05-28): "
            "114 hall gensets x 2.75 ekW = ~313 MW backup; IT ~250-300 MW (N+1). "
            "Per-engine ekW from the draft public notice (3987141/3987144); engine "
            "size CBI-redacted in the final permit under an Ohio EPA trade-secret grant "
            "(OAC 3745-49-03, 2025-10-08; data/extracted/permits/3859883.epa.yaml)."
        ),
    ),
    serving_utility_source="document",
    serving_utility_citation=(
        "relator data appendix (data/extracted/legal/select-committee-2026/relator-testimony/"
        "bosc-data-appendix-2026-06-01.md): the 25 MW threshold 'matches the AEP Ohio tariff'; "
        "corroborated by Allen County commissioners' minutes (local AEP 3-phase service, "
        "Res #974-25). Formal confirmation: EIA-861 service territory / PUCO map."
    ),
    # grid
    lmp_usd_mwh=45.81,  # connector-sourced AEP-zone 2025 day-ahead annual mean (#121)
    lmp_citation=(
        "PJM Data Miner 2 da_hrl_lmps, AEP zone (pnode 8445784), 2025 day-ahead annual mean "
        "$45.81/MWh (8760 h); connector-sourced 2026-06-21 (bosc lmp)"
    ),
    lmp_pnode_id=8445784,
    lmp_pnode_name="AEP",
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
    # GIS — schema-driven (#237): the field-maps live in gis_parcel/gis_zoning/gis_flood below.
    parcels_url=(  # [reference] Hancock County has no county parcel REST (Beacon/Schneider-only);
        # substitute = the OGRIP Ohio statewide parcels public view, scoped to County='Hancock'
        "https://services2.arcgis.com/MlJ0G8iWUyC7jAmu/arcgis/rest/services/"
        "OhioStatewidePacels_full_view/FeatureServer/0"
    ),
    zoning_url=(  # [verified] City of Findlay hosted zoning FeatureServer (ArcGIS Online org XMr9uonP553LyU3o)
        "https://services6.arcgis.com/XMr9uonP553LyU3o/arcgis/rest/services/FindlayZoning/FeatureServer/0"
    ),
    floodzone_url=(  # [verified] FEMA NFHL S_FLD_HAZ_AR (national layer 28) — confirmed 2026-06-19
        "https://hazards.fema.gov/arcgis/rest/services/public/NFHL/MapServer/28"
    ),
    # GIS field-maps: parcels = the OGRIP statewide layer scoped to Hancock (FIPS 39063) — a partial
    # owner-redacted catalog (no owner/value/sale; see OHIO_STATEWIDE_PARCEL_SCHEMA); zoning = the
    # verified City FeatureServer (polygon-only catalog); flood = the shared national NFHL layer.
    gis_parcel=OHIO_STATEWIDE_PARCEL_SCHEMA.model_copy(
        update={"reference_dir": "findlay-gis", "query_scope": "County='Hancock'"}
    ),
    gis_zoning=FINDLAY_ZONING_SCHEMA,
    gis_flood=NATIONAL_NFHL_FLOOD_SCHEMA.model_copy(update={"reference_dir": "findlay-gis"}),
    gnis_default_state="OH",
    hydro_utm_epsg=32617,  # [verified] UTM 17N (Findlay ~83.64degW; zone 17 spans 84-78degW)
    lsc_default_ga="136",  # [verified] Ohio 136th General Assembly (2025-2026); state-level, shared with Lima
    # stormwater (the Atlas-14 corridor point = city centroid; cover scenario pending a site)
    design_lat=41.0428,  # [verified] city centroid = NOAA Atlas-14 point
    design_lon=-83.6422,
    corridor_name="Blanchard River corridor",  # [inference] the receiving-water design corridor
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
    # grid / facility (no identified data-center facility → grid backdrop only, no campus share)
    facility=None,  # [open] the data-center dimension onboard doesn't capture (no disclosed facility)
    serving_utility_source="reference",  # not corpus-grounded — EIA-861/PUCO record
    serving_utility_citation=(  # [reference] not Lima's corpus
        "EIA-861 service-territory file (Ohio Power Co #14006) + PUCO certified-territory map; "
        "AEP Ohio serving Findlay corroborated by the City of Findlay (AEP smart-meter notice)"
    ),
    # grid (same PJM AEP zone as Lima — Ohio Power Co)
    lmp_usd_mwh=45.81,  # connector-sourced AEP-zone 2025 day-ahead annual mean (same zone as Lima)
    lmp_citation=(
        "PJM Data Miner 2 da_hrl_lmps, AEP zone (pnode 8445784), 2025 day-ahead annual mean "
        "$45.81/MWh (8760 h); connector-sourced 2026-06-21 (bosc lmp) — same AEP zone as Lima"
    ),
    lmp_pnode_id=8445784,
    lmp_pnode_name="AEP",
    # rsei
    county_name="Hancock County, OH",  # [verified]
    # map
    map_view_lat=41.0428,
    map_view_lon=-83.6422,
    map_view_zoom=13,
)


# The marquee Maumee comparison node (#235): Fort Wayne, IN — the basin's largest discharger
# (Fort Wayne WWTP 74.0 MGD → Baldwin Ditch → Maumee mainstem; ~4x Lima; ECHO effluent
# [violation]). A *coming-soon* point. The first **out-of-state** site, so it exercises the
# per-site axis across a jurisdiction boundary: Indiana FIPS/state/utility, a UTM-16 reach, the
# national NFHL for flood, and the Ohio-only LSC connector falling away. Geography is sourced +
# cited below; the data-center dimension and facility-specific model inputs stay `[open]` until a
# site is identified (NE Indiana is an active boom region — discovery work, `--research` + corpus).
_FORT_WAYNE = SiteProfile(
    slug="fort-wayne",
    place="Fort Wayne",
    basin="maumee",  # [verified] St. Joseph + St. Marys form the Maumee at Fort Wayne; HUC-8 04100005
    # config knobs
    nwis_sites=[
        "04182900",  # [verified] Maumee River at Fort Wayne IN (mainstem, the receiving reach)
        "04180500",  # [verified] St. Joseph River near Fort Wayne IN (north fork of the Maumee)
        "04182000",  # [verified] St. Marys River near Fort Wayne IN (south fork of the Maumee)
    ],
    nasa_power_lat=41.0891,  # [verified] Fort Wayne city centroid (Census 2023 Gazetteer place 1825000)
    nasa_power_lon=-85.1439,
    rsei_fips="18003",  # [verified] Allen County, IN
    econ_fips="18003",
    eia861_utility_number=9324,  # [verified] Indiana Michigan Power Co (AEP subsidiary); EIA-860 via EIA API
    eia_state="IN",
    # GIS — schema-driven (#237): flood = the shared national NFHL; parcels/zoning discovered in
    # a follow-up live metadata read (Allen County IN GIS + City of Fort Wayne GIS).
    parcels_url="TODO",  # [open] pending the Allen County, IN GIS REST endpoint discovery
    zoning_url="TODO",  # [open] pending the City of Fort Wayne GIS REST endpoint discovery
    floodzone_url=(  # [verified] FEMA NFHL S_FLD_HAZ_AR (national layer 28)
        "https://hazards.fema.gov/arcgis/rest/services/public/NFHL/MapServer/28"
    ),
    gis_parcel=None,  # [open] pending Allen County, IN parcel-layer discovery
    gis_zoning=None,  # [open] pending City of Fort Wayne zoning-layer discovery
    gis_flood=NATIONAL_NFHL_FLOOD_SCHEMA.model_copy(update={"reference_dir": "fort-wayne-gis"}),
    gnis_default_state="IN",
    hydro_utm_epsg=32616,  # [verified] UTM 16N (Fort Wayne ~85.14 degW; zone 16 spans 90-84 degW)
    lsc_default_ga="",  # [n/a] the LSC connector is Ohio-only (statusreport.lsc.ohio.gov); FW is in Indiana
    # stormwater (the Atlas-14 corridor point = city centroid; cover scenario pending a site)
    design_lat=41.0891,  # [verified] city centroid = NOAA Atlas-14 point
    design_lon=-85.1439,
    corridor_name="Maumee headwaters corridor",  # [inference] the St. Joseph/St. Marys → Maumee reach
    dominant_hsg="C",  # [inference] Allen County IN — Blount/Glynwood till + Pewamo lake-plain clays → HSG C
    hsg_citation=(
        "Allen County, IN dominant hydrologic soil group C — Blount/Glynwood till and Pewamo "
        "lake-plain clays of the upper Maumee (NRCS Soil Survey of Allen County, IN); [inference] "
        "pending an SSURGO area-weighted confirmation (onboard SSURGO step needs a footprint)"
    ),
    pre_cover="TODO",  # [open] development land-cover scenario — pending an identified site
    post_cover="TODO",
    developed_pervious_cover="TODO",
    noaa_fallback_24h_depth_in={  # [reference] NOAA Atlas-14 Vol 2 (Ohio River Basin) PDS at 41.0891/-85.1439
        1: 2.18,
        2: 2.61,
        5: 3.26,
        10: 3.78,
        25: 4.51,
        50: 5.11,
        100: 5.73,
        200: 6.39,
        500: 7.30,
        1000: 8.04,
    },
    parcels_relpath="reference/fort-wayne/bosc-parcels.geojson",  # [open] commit the site's own geometry
    footprint_relpath="extracted/fort-wayne/bosc-site-footprint.yaml",  # [open] pending an identified site
    # per-site onboard reach outputs (slug-scoped — never clobber Lima/Findlay)
    climatology_relpath="reference/hydrology/fort-wayne/nasa-power-climatology.yaml",
    corridor_ddf_relpath="reference/hydrology/fort-wayne/atlas14-corridor-ddf.yaml",
    baseline_relpath="reference/economics/fort-wayne/baseline.yaml",
    rsei_relpath="reference/rsei/fort-wayne/inventory.yaml",
    consumer_energy_relpath="reference/eia/fort-wayne/consumer-energy.yaml",
    grid_relpath="reference/eia/fort-wayne/grid-profile.yaml",
    # toxics (no identified industrial corridor yet)
    toxic_corridor_bbox=(0.0, 0.0, 0.0, 0.0),  # [open] pending an identified corridor on the Maumee
    receiving_water_name="Maumee River",  # [verified: ECHO] FW WWTP IN0032191 → Baldwin Ditch → Maumee
    # balance (per-WWTP receiving waters pending the site's NPDES fact sheets)
    plant_receiving={},  # [open] pending Fort Wayne-area WWTP NPDES fact sheets
    abstraction_gage="04182900",  # [inference] the Maumee-at-Fort-Wayne mainstem gage
    # refill (the water-balance supply model is not yet designed for Fort Wayne)
    supply_gage_primary="TODO",  # [open] refill supply gage — pending the site's water-balance model
    supply_gage_secondary="TODO",
    passby_primary_cfs=0.0,  # [open] in-stream passby minimums — pending the model
    passby_secondary_cfs=0.0,
    # grid / facility (no identified data-center facility → grid backdrop only, no campus share)
    facility=None,  # [open] the data-center dimension onboarding doesn't capture (no disclosed facility)
    serving_utility_source="reference",  # not corpus-grounded — EIA-861/IURC record
    serving_utility_citation=(  # [reference] not corpus
        "EIA-861 service-territory file (Indiana Michigan Power Co #9324, an AEP subsidiary) + "
        "Indiana IURC certified-territory; I&M serves the Fort Wayne area"
    ),
    # grid: Indiana Michigan Power (I&M) settles in PJM's AEP zone — PJM has no separate I&M zone
    # (the 23 ZONE pnodes carry no I&M), so Fort Wayne's zonal LMP IS the AEP zone (#361, verified
    # 2026-06-21 against the live PJM Data Miner 2 zone list). Same AEP pnode/fixture as Lima.
    lmp_usd_mwh=45.81,  # connector-sourced AEP-zone 2025 day-ahead annual mean (I&M is in the AEP zone)
    lmp_citation=(
        "PJM Data Miner 2 da_hrl_lmps, AEP zone (pnode 8445784), 2025 day-ahead annual mean "
        "$45.81/MWh (8760 h); connector-sourced 2026-06-21 (bosc lmp) — I&M settles in the PJM AEP zone"
    ),
    lmp_pnode_id=8445784,
    lmp_pnode_name="AEP",
    # rsei
    county_name="Allen County, IN",  # [verified]
    # map
    map_view_lat=41.0891,
    map_view_lon=-85.1439,
    map_view_zoom=12,
)


# The small-stream headwaters comparator: Van Wert, OH — the Auglaize-subbasin point. Unlike
# the mainstem comparators (Defiance 12 MGD, Fort Wayne 74 MGD), Van Wert's WWTP is a 4.0 MGD
# plant discharging to a *small tributary* (Town Creek → Little Auglaize → Auglaize → Maumee),
# so the dilution denominator is tiny — the effluent-dominance end of the basin spectrum. A
# *coming-soon* point; an Ohio site (AEP Ohio / PJM AEP zone, the Ohio LSC connector applies),
# so the cross-state connector axis is not re-exercised. Geography is sourced + cited below; the
# data-center dimension and facility-specific model inputs stay `[open]` until a site is
# identified (Van Wert-area discovery is `--research` + corpus follow-up).
_VAN_WERT = SiteProfile(
    slug="van-wert",
    place="Van Wert",
    basin="maumee",  # [verified] Town Creek → Little Auglaize → Auglaize → Maumee; HUC-8 04100007
    # config knobs
    nwis_sites=[
        "04191000",  # [verified] Town Creek near Van Wert OH (the WWTP receiving reach; HUC 04100007)
        "04191003",  # [verified] Stripe Creek near Van Wert OH (adjacent Little Auglaize tributary)
    ],
    nasa_power_lat=40.8696,  # [verified] Van Wert city centroid (OSM admin boundary; Census place 45891)
    nasa_power_lon=-84.5829,
    rsei_fips="39161",  # [verified] Van Wert County, OH
    econ_fips="39161",
    eia861_utility_number=14006,  # [verified] Ohio Power Co (AEP Ohio); the Van Wert County AEP aggregation
    eia_state="OH",
    # GIS — schema-driven (#237): flood = the shared national NFHL; parcels/zoning discovered in
    # a follow-up live metadata read (Van Wert County GIS + City of Van Wert GIS).
    parcels_url="TODO",  # [open] pending the Van Wert County, OH GIS REST endpoint discovery
    zoning_url="TODO",  # [open] pending the City of Van Wert GIS REST endpoint discovery
    floodzone_url=(  # [verified] FEMA NFHL S_FLD_HAZ_AR (national layer 28)
        "https://hazards.fema.gov/arcgis/rest/services/public/NFHL/MapServer/28"
    ),
    gis_parcel=None,  # [open] pending Van Wert County, OH parcel-layer discovery
    gis_zoning=None,  # [open] pending City of Van Wert zoning-layer discovery
    gis_flood=NATIONAL_NFHL_FLOOD_SCHEMA.model_copy(update={"reference_dir": "van-wert-gis"}),
    gnis_default_state="OH",
    hydro_utm_epsg=32616,  # [verified] UTM 16N (Van Wert ~84.58 degW; zone 16 spans 90-84 degW)
    lsc_default_ga="136",  # [verified] Ohio 136th General Assembly (2025-2026); state-level, shared with Lima
    # stormwater (the Atlas-14 corridor point = city centroid; cover scenario pending a site)
    design_lat=40.8696,  # [verified] city centroid = NOAA Atlas-14 point
    design_lon=-84.5829,
    corridor_name="Town Creek / Little Auglaize corridor",  # [inference] the receiving-water reach
    dominant_hsg="D",  # [inference] Van Wert lake-plain Black Swamp clays (Paulding/Latty/Hoytville) → HSG D
    hsg_citation=(
        "Van Wert County, OH dominant hydrologic soil group D — very-poorly-drained Great Black "
        "Swamp lake-plain clays (Paulding/Latty/Hoytville; NRCS Soil Survey of Van Wert County); "
        "[inference] pending an SSURGO area-weighted confirmation (onboard SSURGO step needs a footprint)"
    ),
    pre_cover="TODO",  # [open] development land-cover scenario — pending an identified site
    post_cover="TODO",
    developed_pervious_cover="TODO",
    noaa_fallback_24h_depth_in={  # [reference] NOAA Atlas-14 Vol 2 (Ohio River Basin) PDS at 40.8696/-84.5829
        1: 2.13,
        2: 2.56,
        5: 3.15,
        10: 3.64,
        25: 4.33,
        50: 4.89,
        100: 5.48,
        200: 6.10,
        500: 6.98,
        1000: 7.68,
    },
    parcels_relpath="reference/van-wert/bosc-parcels.geojson",  # [open] commit the site's own geometry
    footprint_relpath="extracted/van-wert/bosc-site-footprint.yaml",  # [open] pending an identified site
    # per-site onboard reach outputs (slug-scoped — never clobber Lima/Findlay/Fort Wayne)
    climatology_relpath="reference/hydrology/van-wert/nasa-power-climatology.yaml",
    corridor_ddf_relpath="reference/hydrology/van-wert/atlas14-corridor-ddf.yaml",
    baseline_relpath="reference/economics/van-wert/baseline.yaml",
    rsei_relpath="reference/rsei/van-wert/inventory.yaml",
    consumer_energy_relpath="reference/eia/van-wert/consumer-energy.yaml",
    grid_relpath="reference/eia/van-wert/grid-profile.yaml",
    # toxics (no identified industrial corridor yet)
    toxic_corridor_bbox=(0.0, 0.0, 0.0, 0.0),  # [open] pending an identified corridor on Town Creek
    receiving_water_name="Town Creek",  # [verified] Ohio EPA NPDES 2PD00006/OH0027910 → Town Creek (RM 13.87)
    # balance (per-WWTP receiving waters pending the site's NPDES fact sheets)
    plant_receiving={},  # [open] pending Van Wert-area WWTP NPDES fact sheets
    abstraction_gage="04191000",  # [inference] the Town Creek near Van Wert receiving-reach gage
    # refill (the water-balance supply model is not yet designed for Van Wert)
    supply_gage_primary="TODO",  # [open] refill supply gage — pending the site's water-balance model
    supply_gage_secondary="TODO",
    passby_primary_cfs=0.0,  # [open] in-stream passby minimums — pending the model
    passby_secondary_cfs=0.0,
    # grid / facility (no identified data-center facility → grid backdrop only, no campus share)
    facility=None,  # [open] the data-center dimension onboarding doesn't capture (no disclosed facility)
    serving_utility_source="reference",  # not corpus-grounded — EIA-861/PUCO record
    serving_utility_citation=(  # [reference] not corpus
        "EIA-861 service-territory file (Ohio Power Co #14006) + PUCO certified-territory; AEP Ohio "
        "serving the City of Van Wert corroborated by the Van Wert County AEP Ohio electric-aggregation program"
    ),
    # grid (same PJM AEP zone as Lima/Findlay — Ohio Power Co)
    lmp_usd_mwh=45.81,  # connector-sourced AEP-zone 2025 day-ahead annual mean (same zone as Lima)
    lmp_citation=(
        "PJM Data Miner 2 da_hrl_lmps, AEP zone (pnode 8445784), 2025 day-ahead annual mean "
        "$45.81/MWh (8760 h); connector-sourced 2026-06-21 (bosc lmp) — same AEP zone as Lima"
    ),
    lmp_pnode_id=8445784,
    lmp_pnode_name="AEP",
    # rsei
    county_name="Van Wert County, OH",  # [verified]
    # map
    map_view_lat=40.8696,
    map_view_lon=-84.5829,
    map_view_zoom=13,
)


# The tidal/lake comparator: Toledo, OH — the Lower Maumee at Lake Erie (#236). Where Lima
# discharges to tiny tributaries and Fort Wayne to the headwaters, the Lucas Co WRRF (22.5 MGD,
# NPDES OH0034223) discharges to the **tidal lower Maumee** at the lake — a fundamentally
# different dilution regime (the "is Lima's tributary siting the outlier?" contrast). A
# *coming-soon* point. The first Ohio site **not on AEP**: Toledo Edison (FirstEnergy, EIA
# #18997) in PJM's **ATSI** zone — so it exercises the grid connector across a utility/holding-
# company/market-zone boundary the AEP sites (Lima/Findlay/Van Wert) never do, while staying in
# Ohio (PUCO, the Ohio LSC). Geography is sourced + cited; the data-center dimension and
# facility-specific model inputs stay `[open]` until a site is identified.
_TOLEDO = SiteProfile(
    slug="toledo",
    place="Toledo",
    basin="maumee",  # [verified] Lower Maumee → Lake Erie; HUC-8 04100009 (Lucas Co WRRF discharge)
    # config knobs
    nwis_sites=[
        "04193500",  # [verified] Maumee River at Waterville OH (mainstem, long record — the basin 7Q10 ref)
        "04193990",  # [verified] Maumee River at Anthony Wayne Bridge, Toledo OH (the tidal lower reach)
    ],
    nasa_power_lat=41.6529,  # [verified] Toledo city centroid (OSM admin boundary; Lucas County)
    nasa_power_lon=-83.5378,
    rsei_fips="39095",  # [verified] Lucas County, OH
    econ_fips="39095",
    eia861_utility_number=18997,  # [verified] The Toledo Edison Co (FirstEnergy); EIA-861 2024 States sheet
    eia_state="OH",
    # GIS — schema-driven (#237): flood = the shared national NFHL; parcels/zoning discovered in
    # a follow-up live metadata read (Lucas County GIS / AREIS + City of Toledo GIS).
    # GIS — schema-driven (#237 / #384). Lucas County's AREIS is the richest GIS in the network:
    # parcels = the owner-bearing AREIS land-use-classification layer (38); zoning = the parcel-level
    # AREIS Parcel_Zoning layer; flood = the shared national NFHL. The appraised-value PARID join
    # (AREIS layer 83) is a tracked follow-up — market values stay null until then.
    parcels_url=(  # [verified] Lucas County Auditor AREIS — layer 38 (owner + land-use CAMA)
        "https://lcaudgis.co.lucas.oh.us/gisaudserver/rest/services/AREIS_Web_Map_MIL1/MapServer/38"
    ),
    zoning_url=(  # [verified] Lucas County AREIS — Parcel_Zoning layer 0 (parcel-level zoning)
        "https://lcaudgis.co.lucas.oh.us/gisaudserver/rest/services/"
        "LandUse_Zoning/Parcel_Zoning/MapServer/0"
    ),
    floodzone_url=(  # [verified] FEMA NFHL S_FLD_HAZ_AR (national layer 28)
        "https://hazards.fema.gov/arcgis/rest/services/public/NFHL/MapServer/28"
    ),
    gis_parcel=LUCAS_AREIS_PARCEL_SCHEMA,  # [verified] AREIS layer 38 — owner + land-use (#384)
    gis_zoning=LUCAS_ZONING_SCHEMA,  # [verified] AREIS Parcel_Zoning — parcel-level catalog (#384)
    gis_flood=NATIONAL_NFHL_FLOOD_SCHEMA.model_copy(update={"reference_dir": "toledo-gis"}),
    gnis_default_state="OH",
    hydro_utm_epsg=32617,  # [verified] UTM 17N (Toledo ~83.54 degW; zone 17 spans 84-78 degW)
    lsc_default_ga="136",  # [verified] Ohio 136th General Assembly (2025-2026); state-level, shared with Lima
    # stormwater (the Atlas-14 corridor point = city centroid; cover scenario pending a site)
    design_lat=41.6529,  # [verified] city centroid = NOAA Atlas-14 point
    design_lon=-83.5378,
    corridor_name="Lower Maumee / tidal corridor",  # [inference] the tidal Maumee → Lake Erie reach
    dominant_hsg="D",  # [inference] Lucas Co lake-plain Black Swamp clays (Hoytville/Toledo/Lucas) → HSG D
    hsg_citation=(
        "Lucas County, OH dominant hydrologic soil group D — very-poorly-drained Great Black "
        "Swamp lake-plain clays (Hoytville/Toledo/Lucas series; NRCS Soil Survey of Lucas County); "
        "[inference] pending an SSURGO area-weighted confirmation (onboard SSURGO step needs a footprint)"
    ),
    pre_cover="TODO",  # [open] development land-cover scenario — pending an identified site
    post_cover="TODO",
    developed_pervious_cover="TODO",
    noaa_fallback_24h_depth_in={  # [reference] NOAA Atlas-14 Vol 2 (Ohio River Basin) PDS at 41.6529/-83.5378
        1: 2.01,
        2: 2.42,
        5: 3.03,
        10: 3.53,
        25: 4.25,
        50: 4.84,
        100: 5.47,
        200: 6.15,
        500: 7.12,
        1000: 7.92,
    },
    parcels_relpath="reference/toledo/bosc-parcels.geojson",  # [open] commit the site's own geometry
    footprint_relpath="extracted/toledo/bosc-site-footprint.yaml",  # [open] pending an identified site
    # per-site onboard reach outputs (slug-scoped — never clobber Lima/Findlay/Fort Wayne/Van Wert)
    climatology_relpath="reference/hydrology/toledo/nasa-power-climatology.yaml",
    corridor_ddf_relpath="reference/hydrology/toledo/atlas14-corridor-ddf.yaml",
    baseline_relpath="reference/economics/toledo/baseline.yaml",
    rsei_relpath="reference/rsei/toledo/inventory.yaml",
    consumer_energy_relpath="reference/eia/toledo/consumer-energy.yaml",
    grid_relpath="reference/eia/toledo/grid-profile.yaml",
    # toxics (no identified industrial corridor yet)
    toxic_corridor_bbox=(
        0.0,
        0.0,
        0.0,
        0.0,
    ),  # [open] pending an identified corridor on the Lower Maumee
    receiving_water_name="Maumee River",  # [verified: ECHO] Lucas Co WRRF OH0034223 → Lower Maumee (tidal) → Lake Erie
    # balance (per-WWTP receiving waters pending the site's NPDES fact sheets)
    plant_receiving={},  # [open] pending Toledo-area WWTP NPDES fact sheets
    abstraction_gage="04193500",  # [inference] the Maumee-at-Waterville mainstem gage (nearest the WRRF reach)
    # refill (the water-balance supply model is not yet designed for Toledo)
    supply_gage_primary="TODO",  # [open] refill supply gage — pending the site's water-balance model
    supply_gage_secondary="TODO",
    passby_primary_cfs=0.0,  # [open] in-stream passby minimums — pending the model
    passby_secondary_cfs=0.0,
    # grid / facility (no identified data-center facility → grid backdrop only, no campus share)
    facility=None,  # [open] the data-center dimension onboarding doesn't capture (no disclosed facility)
    serving_utility_source="reference",  # not corpus-grounded — EIA-861/PUCO record
    serving_utility_citation=(  # [reference] not corpus
        "EIA-861 service-territory file (The Toledo Edison Co #18997, a FirstEnergy operating "
        "company) + PUCO certified-territory; Toledo Edison serves the Toledo metro"
    ),
    # grid (Toledo Edison is in PJM's ATSI / FirstEnergy zone — NOT the AEP zone of the other OH sites)
    lmp_usd_mwh=45.84,  # connector-sourced ATSI-zone 2025 day-ahead annual mean (#387; not the AEP value)
    lmp_citation=(
        "PJM Data Miner 2 da_hrl_lmps, ATSI zone (FirstEnergy / Toledo Edison, pnode 116013753), "
        "2025 day-ahead annual mean $45.84/MWh (8760 h); connector-sourced 2026-06-21 (bosc lmp)"
    ),
    lmp_pnode_id=116013753,
    lmp_pnode_name="ATSI",
    # rsei
    county_name="Lucas County, OH",  # [verified]
    # map
    map_view_lat=41.6529,
    map_view_lon=-83.5378,
    map_view_zoom=12,
)


# The Maumee-mainstem comparator: Defiance, OH (#238). The Defiance WWTP (12.0 MGD, NPDES
# OH0024899) discharges to the **Maumee mainstem** right at the Maumee/Auglaize/Tiffin
# confluence — where the river carries far more flow than Lima's tributaries, so the screen
# reads "tight" (~6.2:1) rather than violation (docs/bigger-picture.md §2): the cleanest test
# of "is Lima's tributary siting what drives its violation?". A *coming-soon* point. Served by
# Toledo Edison (FirstEnergy / PJM ATSI, EIA #18997 — same as Toledo, the largest IOU in
# Defiance County), so it reuses the non-AEP grid path (#236) and stays in Ohio (PUCO, the
# Ohio LSC). Geography is sourced + cited; the data-center dimension and facility-specific
# model inputs stay `[open]` until a site is identified.
_DEFIANCE = SiteProfile(
    slug="defiance",
    place="Defiance",
    basin="maumee",  # [verified] Maumee mainstem at the Auglaize/Tiffin confluence; HUC-8 04100009
    # config knobs
    nwis_sites=[
        "04192500",  # [verified] Maumee River near Defiance OH (the mainstem receiving reach, below the confluence)
        "04191500",  # [verified] Auglaize River near Defiance OH (the major tributary joining at Defiance)
    ],
    nasa_power_lat=41.2868,  # [verified] Defiance city centroid (OSM admin boundary; Defiance County)
    nasa_power_lon=-84.3621,
    rsei_fips="39039",  # [verified] Defiance County, OH
    econ_fips="39039",
    eia861_utility_number=18997,  # [reference] The Toledo Edison Co (FirstEnergy) — largest IOU in Defiance Co
    eia_state="OH",
    # GIS — schema-driven (#237): flood = the shared national NFHL; parcels/zoning discovered in
    # a follow-up live metadata read (Defiance County GIS + City of Defiance GIS).
    parcels_url="TODO",  # [open] pending the Defiance County, OH GIS REST endpoint discovery
    zoning_url="TODO",  # [open] pending the City of Defiance GIS REST endpoint discovery
    floodzone_url=(  # [verified] FEMA NFHL S_FLD_HAZ_AR (national layer 28)
        "https://hazards.fema.gov/arcgis/rest/services/public/NFHL/MapServer/28"
    ),
    gis_parcel=None,  # [open] pending Defiance County, OH parcel-layer discovery
    gis_zoning=None,  # [open] pending City of Defiance zoning-layer discovery
    gis_flood=NATIONAL_NFHL_FLOOD_SCHEMA.model_copy(update={"reference_dir": "defiance-gis"}),
    gnis_default_state="OH",
    hydro_utm_epsg=32616,  # [verified] UTM 16N (Defiance ~84.36 degW; zone 16 spans 90-84 degW)
    lsc_default_ga="136",  # [verified] Ohio 136th General Assembly (2025-2026); state-level, shared with Lima
    # stormwater (the Atlas-14 corridor point = city centroid; cover scenario pending a site)
    design_lat=41.2868,  # [verified] city centroid = NOAA Atlas-14 point
    design_lon=-84.3621,
    corridor_name="Maumee-Auglaize confluence corridor",  # [inference] the Maumee mainstem reach at Defiance
    dominant_hsg="D",  # [inference] Defiance Co Maumee lake-plain Black Swamp clays (Hoytville/Nappanee) → HSG D
    hsg_citation=(
        "Defiance County, OH dominant hydrologic soil group D — very-poorly-drained Great Black "
        "Swamp lake-plain clays (Hoytville/Nappanee/Paulding; NRCS Soil Survey of Defiance County); "
        "[inference] pending an SSURGO area-weighted confirmation (onboard SSURGO step needs a footprint)"
    ),
    pre_cover="TODO",  # [open] development land-cover scenario — pending an identified site
    post_cover="TODO",
    developed_pervious_cover="TODO",
    noaa_fallback_24h_depth_in={  # [reference] NOAA Atlas-14 Vol 2 (Ohio River Basin) PDS at 41.2868/-84.3621
        1: 2.06,
        2: 2.48,
        5: 3.08,
        10: 3.57,
        25: 4.26,
        50: 4.82,
        100: 5.41,
        200: 6.03,
        500: 6.90,
        1000: 7.60,
    },
    parcels_relpath="reference/defiance/bosc-parcels.geojson",  # [open] commit the site's own geometry
    footprint_relpath="extracted/defiance/bosc-site-footprint.yaml",  # [open] pending an identified site
    # per-site onboard reach outputs (slug-scoped — never clobber the other sites)
    climatology_relpath="reference/hydrology/defiance/nasa-power-climatology.yaml",
    corridor_ddf_relpath="reference/hydrology/defiance/atlas14-corridor-ddf.yaml",
    baseline_relpath="reference/economics/defiance/baseline.yaml",
    rsei_relpath="reference/rsei/defiance/inventory.yaml",
    consumer_energy_relpath="reference/eia/defiance/consumer-energy.yaml",
    grid_relpath="reference/eia/defiance/grid-profile.yaml",
    # toxics (no identified industrial corridor yet)
    # [inference] the Defiance industrial cluster on the Maumee/Auglaize mainstem from the
    # Auglaize/Tiffin confluence downstream (#393): covers GM Defiance Casting (now GM Global
    # Propulsion Systems, 41.282/-84.292), the three Johns Manville fiberglass plants (~41.28-41.30/
    # -84.34 to -84.36), and GT Technologies (41.27/-84.39); excludes the far-west Hicksville cluster
    # (Syn Ind. -84.75). A water-releasing RSEI facility inside the box is inferred to discharge to
    # the Maumee (tagged `assumption`). (lat_min, lat_max, lon_min, lon_max)
    toxic_corridor_bbox=(41.26, 41.31, -84.40, -84.28),
    receiving_water_name="Maumee River",  # [verified: ECHO] Defiance WWTP OH0024899 → Maumee River (mainstem)
    # balance (per-WWTP receiving waters pending the site's NPDES fact sheets)
    plant_receiving={},  # [open] pending Defiance-area WWTP NPDES fact sheets
    abstraction_gage="04192500",  # [inference] the Maumee-near-Defiance mainstem gage (below the confluence)
    # refill (the water-balance supply model is not yet designed for Defiance)
    supply_gage_primary="TODO",  # [open] refill supply gage — pending the site's water-balance model
    supply_gage_secondary="TODO",
    passby_primary_cfs=0.0,  # [open] in-stream passby minimums — pending the model
    passby_secondary_cfs=0.0,
    # grid / facility (no identified data-center facility → grid backdrop only, no campus share)
    facility=None,  # [open] the data-center dimension onboarding doesn't capture (no disclosed facility)
    serving_utility_source="reference",  # not corpus-grounded — EIA-861/PUCO record
    serving_utility_citation=(  # [reference] not corpus
        "EIA-861 service-territory file (The Toledo Edison Co #18997, a FirstEnergy operating "
        "company; the largest IOU in Defiance County) + PUCO certified-territory; the City of "
        "Defiance electric-aggregation program rides Toledo Edison distribution"
    ),
    # grid (Toledo Edison is in PJM's ATSI / FirstEnergy zone — same non-AEP path as Toledo)
    lmp_usd_mwh=35.0,  # [inference] PJM ATSI-zone placeholder — verify via PJM Data Miner 2 (not the AEP value)
    lmp_citation=(
        "PJM ATSI zone (FirstEnergy / Toledo Edison) ~2024 annual average LMP ($/MWh) via PJM Data "
        "Miner 2 da_hrl_lmps; [inference] not the AEP-zone value used by the AEP OH sites — verify"
    ),
    # rsei
    county_name="Defiance County, OH",  # [verified]
    # map
    map_view_lat=41.2868,
    map_view_lon=-84.3621,
    map_view_zoom=12,
)


# The municipal-utility / Tiffin-subbasin headwaters comparator: Bryan, OH (#380). The Bryan
# WWTP (NPDES OH0020532) discharges to Prairie Creek → Tiffin River → Maumee → Lake Erie at the
# far NW corner of the basin (HUC-8 04100006 Tiffin) — a small-tributary headwaters point like
# Van Wert, but in the Tiffin subbasin rather than the Auglaize. A *coming-soon* point. Its
# distinguishing feature is the GRID: Bryan is the network's **first municipal electric utility**
# (City of Bryan, EIA #2439; an American Municipal Power member, PJM) — not an IOU like every
# other registered site, so it exercises the grid connector's short-form (EIA-861S) path and the
# ownership-aware retail-regulator (municipal home rule, not PUCO). Geography is sourced + cited;
# the data-center dimension and facility-specific model inputs stay `[open]` until a site is found.
_BRYAN = SiteProfile(
    slug="bryan",
    place="Bryan",
    basin="maumee",  # [verified] Prairie Creek → Tiffin River → Maumee → Lake Erie; HUC-8 04100006
    # config knobs
    nwis_sites=[
        "04185000",  # [verified] Tiffin River at Stryker OH (receiving Tiffin mainstem below Bryan; long record)
        "04184500",  # [verified] Bean Creek at Powers OH (the Tiffin's principal gaged headwaters tributary)
    ],
    nasa_power_lat=41.4748,  # [verified] Bryan city centroid (OSM admin boundary relation 182831; Census place 09064)
    nasa_power_lon=-84.5525,
    rsei_fips="39171",  # [verified] Williams County, OH
    econ_fips="39171",
    eia861_utility_number=2439,  # [verified] City of Bryan - (OH); MUNICIPAL, EIA-861S short-form filer (BA=PJM)
    eia_state="OH",
    # GIS — schema-driven (#237). Parcels (#410): Williams County, OH publishes NO county parcel
    # REST of its own (the bhamaps PAT MapServer that would host one has the same expired TLS cert
    # as Van Wert/Defiance, #421/#394), so — exactly like Findlay/Hancock — the substitute is the
    # OGRIP Ohio statewide parcels public view scoped to County='Williams'. NOTE: the ArcGIS org the
    # onboarding GIS-discovery pass flagged as a "wire-ready Williams County ArcGIS"
    # (services1.arcgis.com/D85sDZoJyameepNh) is Williams County, NORTH DAKOTA — a same-named-county
    # cross-state misidentification (situs cities Williston/Tioga/Grenora; owner Hess Tioga Gas
    # Plant). It is NOT wired here. Flood = the shared national NFHL; zoning stays [open].
    parcels_url=(  # [reference] OGRIP Ohio statewide parcels, scoped to County='Williams' (39171)
        "https://services2.arcgis.com/MlJ0G8iWUyC7jAmu/arcgis/rest/services/"
        "OhioStatewidePacels_full_view/FeatureServer/0"
    ),
    zoning_url="TODO",  # [open] pending a real City of Bryan / Williams Co OH zoning REST (none found)
    floodzone_url=(  # [verified] FEMA NFHL S_FLD_HAZ_AR (national layer 28)
        "https://hazards.fema.gov/arcgis/rest/services/public/NFHL/MapServer/28"
    ),
    gis_parcel=OHIO_STATEWIDE_PARCEL_SCHEMA.model_copy(
        # Williams' OGRIP LocalParcelID is the dashed NN-NNN-NN-NNN.NNN form (e.g. "062-350-02-013.001"),
        # not Hancock's dashless 12 digits — so id lookups are verbatim, with the dashed deed_id_regex.
        update={
            "reference_dir": "bryan-gis",
            "query_scope": "County='Williams'",
            "id_normalize": "verbatim",
            "deed_id_regex": r"\b\d{3}-\d{3}-\d{2}-\d{3}\.\d{3}\b",
        }
    ),
    gis_zoning=None,  # [open] no real City of Bryan/Williams OH zoning REST (the discovered one was ND)
    gis_flood=NATIONAL_NFHL_FLOOD_SCHEMA.model_copy(update={"reference_dir": "bryan-gis"}),
    gnis_default_state="OH",
    hydro_utm_epsg=32616,  # [verified] UTM 16N (Bryan ~84.55 degW; zone 16 spans 90-84 degW)
    lsc_default_ga="136",  # [verified] Ohio 136th General Assembly (2025-2026); state-level, shared with Lima
    # stormwater (the Atlas-14 corridor point = city centroid; cover scenario pending a site)
    design_lat=41.4748,  # [verified] city centroid = NOAA Atlas-14 point
    design_lon=-84.5525,
    corridor_name="Prairie Creek / Tiffin River corridor",  # [inference] the receiving-water reach
    dominant_hsg="C",  # [inference] Williams Co upper-Maumee/Tiffin till plain (Blount/Glynwood/Pewamo) → HSG C
    hsg_citation=(
        "Williams County, OH dominant hydrologic soil group C — upper-Maumee/Tiffin till-plain "
        "soils (Blount/Glynwood/Pewamo association; NRCS Soil Survey of Williams County), the "
        "till-plain headwaters rather than the lake-plain Black Swamp clays (HSG D) downstream; "
        "[inference] pending an SSURGO area-weighted confirmation (onboard SSURGO step needs a footprint)"
    ),
    pre_cover="TODO",  # [open] development land-cover scenario — pending an identified site
    post_cover="TODO",
    developed_pervious_cover="TODO",
    noaa_fallback_24h_depth_in={  # [reference] NOAA Atlas-14 Vol 2 (Ohio River Basin) PDS at 41.4748/-84.5525
        1: 2.07,
        2: 2.48,
        5: 3.10,
        10: 3.60,
        25: 4.30,
        50: 4.87,
        100: 5.48,
        200: 6.12,
        500: 7.04,
        1000: 7.78,
    },
    parcels_relpath="reference/bryan/bosc-parcels.geojson",  # [open] commit the site's own geometry
    footprint_relpath="extracted/bryan/bosc-site-footprint.yaml",  # [open] pending an identified site
    # per-site onboard reach outputs (slug-scoped — never clobber the other sites)
    climatology_relpath="reference/hydrology/bryan/nasa-power-climatology.yaml",
    corridor_ddf_relpath="reference/hydrology/bryan/atlas14-corridor-ddf.yaml",
    baseline_relpath="reference/economics/bryan/baseline.yaml",
    rsei_relpath="reference/rsei/bryan/inventory.yaml",
    consumer_energy_relpath="reference/eia/bryan/consumer-energy.yaml",
    grid_relpath="reference/eia/bryan/grid-profile.yaml",
    # [inference] the City of Bryan reach of Prairie Creek (#412): covers the Bryan-city industrial
    # cluster — NEW ERA OHIO (41.478/-84.559; now CLOSED, a legacy emitter), Titan Tire of Bryan
    # (41.467/-84.530; active), Hayes-Albion, Ohio Art, A-Stamp, Plastech — and excludes the
    # Montpelier/Edgerton/Stryker facilities on other drainages (Chase Brass 41.61, A Schulman
    # -84.43, Edgerton -84.75). A water-releasing RSEI facility inside the box is inferred to
    # discharge to Prairie Creek (tagged `assumption`). (lat_min, lat_max, lon_min, lon_max)
    toxic_corridor_bbox=(41.46, 41.49, -84.57, -84.52),
    receiving_water_name="Prairie Creek",  # [verified] Bryan WWTP NPDES OH0020532 → Prairie Creek → Tiffin River
    # balance (per-WWTP receiving waters pending the site's NPDES fact sheets)
    plant_receiving={},  # [open] pending Bryan-area WWTP NPDES fact sheets
    abstraction_gage="04185000",  # [inference] the Tiffin-at-Stryker mainstem gage (receiving reach below Bryan)
    # refill (the water-balance supply model is not yet designed for Bryan)
    supply_gage_primary="TODO",  # [open] refill supply gage — pending the site's water-balance model
    supply_gage_secondary="TODO",
    passby_primary_cfs=0.0,  # [open] in-stream passby minimums — pending the model
    passby_secondary_cfs=0.0,
    # grid / facility (no identified data-center facility → grid backdrop only, no campus share)
    facility=None,  # [open] the data-center dimension onboarding doesn't capture (no disclosed facility)
    serving_utility_source="reference",  # not corpus-grounded — the EIA-861S municipal record
    serving_utility_citation=(  # [reference] municipal home-rule electric (NOT PUCO rate-regulated)
        "EIA-861S Short Form (City of Bryan - OH, #2439; Municipal, BA=PJM, ~160 GWh sold 2024) — "
        "Bryan Municipal Utilities, a municipally-owned electric system and American Municipal "
        "Power (AMP) member; municipal home-rule retail, the network's first municipal/short-form "
        "utility. Wholesale power + PJM scheduling are through AMP, not an IOU holding company"
    ),
    # grid: Bryan municipal load is scheduled into PJM via AMP, but the City-of-Bryan load settles
    # in the PJM AEP zone — the live PJM Data Miner 2 pnode table lists CTYBRYAN ("City of Bryan",
    # LOAD pnodes 32411011/32411013) in zone AEP (#411, verified 2026-06-21). So Bryan's zonal LMP
    # IS the AEP zone (same pnode/fixture as the AEP OH sites), despite the AMP wholesale arrangement.
    lmp_usd_mwh=45.81,  # connector-sourced AEP-zone 2025 day-ahead annual mean (CTYBRYAN is in AEP)
    lmp_citation=(
        "PJM Data Miner 2 da_hrl_lmps, AEP zone (pnode 8445784), 2025 day-ahead annual mean "
        "$45.81/MWh (8760 h); connector-sourced 2026-06-21 (bosc lmp) — the City-of-Bryan load "
        "(CTYBRYAN) settles in the PJM AEP zone"
    ),
    lmp_pnode_id=8445784,
    lmp_pnode_name="AEP",
    # rsei
    county_name="Williams County, OH",  # [verified]
    # map
    map_view_lat=41.4748,
    map_view_lon=-84.5525,
    map_view_zoom=13,
)


# The intra-tributary (same-river) comparator: Ottawa, OH (#381) — the **Village** of Ottawa,
# Putnam County, on the **Blanchard River**, the downstream sibling of Findlay (#237, also on the
# Blanchard). The Ottawa WWTP (NPDES OH0026921, 3.0 MGD) discharges to the Blanchard → Auglaize →
# Maumee → Lake Erie (HUC-8 04100008). Where most network points compare *across* tributaries,
# Findlay↔Ottawa is a comparison *along one river* — same receiving water, two points ~40 river-mi
# apart — a clean control on watershed identity. A *coming-soon* point; an Ohio AEP site (AEP Ohio /
# PJM AEP zone, the Ohio LSC applies), so the cross-state / non-AEP connector axes are not
# re-exercised. (Disambiguation: NOT Ottawa County / Port Clinton, and NOT the Ottawa River of Lima
# or Toledo.) Geography is sourced + cited; the data-center dimension and facility-specific model
# inputs stay `[open]` until a site is identified.
_OTTAWA = SiteProfile(
    slug="ottawa",
    place="Ottawa",
    basin="maumee",  # [verified] Blanchard R. → Auglaize → Maumee → Lake Erie; HUC-8 04100008 (Blanchard)
    # config knobs
    nwis_sites=[
        "04189260",  # [verified] Blanchard River at Ottawa OH (the WWTP receiving reach, at the village)
        "04189500",  # [verified] Blanchard River at Glandorf OH (the long-record Blanchard gage just downstream)
    ],
    nasa_power_lat=41.0192,  # [verified] Ottawa village centroid (OSM admin boundary relation 182178; Putnam Co)
    nasa_power_lon=-84.0472,
    rsei_fips="39137",  # [verified] Putnam County, OH
    econ_fips="39137",
    eia861_utility_number=14006,  # [reference] Ohio Power Co (AEP Ohio) — the IOU serving the incorporated village
    eia_state="OH",
    # GIS — schema-driven (#237): parcels = Putnam County's self-hosted ArcGIS (#420); flood = the
    # shared national NFHL; zoning still pending (the village's zoning is class-coded / map-only).
    parcels_url=(  # [verified] Putnam County GIS — Parcels layer 0 (auditor CAMA + geometry)
        "https://putnamcountygis.com/arcgis/rest/services/Parcels/Parcels/MapServer/0"
    ),
    zoning_url="TODO",  # [open] pending the Village of Ottawa, OH GIS REST endpoint discovery
    floodzone_url=(  # [verified] FEMA NFHL S_FLD_HAZ_AR (national layer 28)
        "https://hazards.fema.gov/arcgis/rest/services/public/NFHL/MapServer/28"
    ),
    gis_parcel=PUTNAM_PARCEL_SCHEMA,  # [verified] Putnam County Parcels (owner + CAMA values; #420)
    gis_zoning=None,  # [open] pending Village of Ottawa zoning-layer discovery (class-coded/map-only)
    gis_flood=NATIONAL_NFHL_FLOOD_SCHEMA.model_copy(update={"reference_dir": "ottawa-gis"}),
    gnis_default_state="OH",
    hydro_utm_epsg=32616,  # [verified] UTM 16N (Ottawa ~84.05 degW; zone 16 spans 90-84 degW)
    lsc_default_ga="136",  # [verified] Ohio 136th General Assembly (2025-2026); state-level, shared with Lima
    # stormwater (the Atlas-14 corridor point = village centroid; cover scenario pending a site)
    design_lat=41.0192,  # [verified] village centroid = NOAA Atlas-14 point
    design_lon=-84.0472,
    corridor_name="Lower Blanchard River corridor",  # [inference] the receiving-water reach below Findlay
    dominant_hsg="D",  # [inference] Putnam Co lake-plain Black Swamp clays (Hoytville/Latty/Paulding) → HSG D
    hsg_citation=(
        "Putnam County, OH dominant hydrologic soil group D — very-poorly-drained Great Black "
        "Swamp lake-plain clays (Hoytville/Latty/Paulding/Nappanee; NRCS Soil Survey of Putnam "
        "County); [inference] pending an SSURGO area-weighted confirmation (onboard SSURGO step needs a footprint)"
    ),
    pre_cover="TODO",  # [open] development land-cover scenario — pending an identified site
    post_cover="TODO",
    developed_pervious_cover="TODO",
    noaa_fallback_24h_depth_in={  # [reference] NOAA Atlas-14 Vol 2 (Ohio River Basin) PDS at 41.0192/-84.0472
        1: 2.07,
        2: 2.48,
        5: 3.05,
        10: 3.52,
        25: 4.19,
        50: 4.74,
        100: 5.31,
        200: 5.91,
        500: 6.75,
        1000: 7.44,
    },
    parcels_relpath="reference/ottawa/bosc-parcels.geojson",  # [open] commit the site's own geometry
    footprint_relpath="extracted/ottawa/bosc-site-footprint.yaml",  # [open] pending an identified site
    # per-site onboard reach outputs (slug-scoped — never clobber the other sites)
    climatology_relpath="reference/hydrology/ottawa/nasa-power-climatology.yaml",
    corridor_ddf_relpath="reference/hydrology/ottawa/atlas14-corridor-ddf.yaml",
    baseline_relpath="reference/economics/ottawa/baseline.yaml",
    rsei_relpath="reference/rsei/ottawa/inventory.yaml",
    consumer_energy_relpath="reference/eia/ottawa/consumer-energy.yaml",
    grid_relpath="reference/eia/ottawa/grid-profile.yaml",
    # toxics (no identified industrial corridor yet)
    toxic_corridor_bbox=(
        0.0,
        0.0,
        0.0,
        0.0,
    ),  # [open] pending an identified corridor on the Blanchard
    receiving_water_name="Blanchard River",  # [verified] Ottawa WWTP NPDES OH0026921 → Blanchard River (gage 04189260)
    # balance (per-WWTP receiving waters pending the site's NPDES fact sheets)
    plant_receiving={},  # [open] pending Ottawa-area WWTP NPDES fact sheets
    abstraction_gage="04189260",  # [inference] the Blanchard-at-Ottawa receiving-reach gage
    # refill (the water-balance supply model is not yet designed for Ottawa)
    supply_gage_primary="TODO",  # [open] refill supply gage — pending the site's water-balance model
    supply_gage_secondary="TODO",
    passby_primary_cfs=0.0,  # [open] in-stream passby minimums — pending the model
    passby_secondary_cfs=0.0,
    # grid / facility (no identified data-center facility → grid backdrop only, no campus share)
    facility=None,  # [open] the data-center dimension onboarding doesn't capture (no disclosed facility)
    serving_utility_source="reference",  # not corpus-grounded — EIA-861/PUCO record
    serving_utility_citation=(  # [reference] not corpus
        "EIA-861 service-territory file (Ohio Power Co #14006) + PUCO certified-territory: AEP Ohio "
        "serves the incorporated Village of Ottawa; rural Putnam County is served by cooperatives "
        "(Paulding-Putnam, Midwest, Hancock-Wood, Tricounty) — the village seat is AEP Ohio"
    ),
    # grid (same PJM AEP zone as Lima/Findlay/Van Wert — Ohio Power Co; Findlay is the Blanchard sibling)
    lmp_usd_mwh=45.81,  # connector-sourced AEP-zone 2025 day-ahead annual mean (same zone as Lima)
    lmp_citation=(
        "PJM Data Miner 2 da_hrl_lmps, AEP zone (pnode 8445784), 2025 day-ahead annual mean "
        "$45.81/MWh (8760 h); connector-sourced 2026-06-21 (bosc lmp) — same AEP zone as Lima/Findlay"
    ),
    lmp_pnode_id=8445784,
    lmp_pnode_name="AEP",
    # rsei
    county_name="Putnam County, OH",  # [verified]
    # map
    map_view_lat=41.0192,
    map_view_lon=-84.0472,
    map_view_zoom=13,
)


# The network's FIRST Miami-basin site (the second basin branch) and the flagship of the
# Wright-Patterson / Mad River corridor expansion. Urbana sits on the **Mad River** in
# Champaign County — the clean headwaters of the **Mad River buried-valley aquifer** (glacial
# outwash sand & gravel; a US-EPA sole-source aquifer that supplies the Springfield/Dayton/
# Wright-Patterson AFB corridor downstream). That geology is the deliberate CONTRAST with the
# Maumee lake-plain sites: a groundwater-dominated, highly permeable HSG A/B valley fill, the
# inverse of the poorly-drained Black Swamp clays (HSG D). Sink is the Ohio River, not Lake
# Erie, and there is no Maumee-style basin TMDL — a genuinely different mix of influences.
# Registered for onboarding (#440); most fields are [open] research targets filled by
# `bosc onboard urbana --research` — only the verified geography/gages are set here.
_URBANA = SiteProfile(
    slug="urbana",
    place="Urbana",
    basin="great-miami",  # [verified] Mad River → Great Miami River → Ohio River (HUC-8 05080001)
    nwis_sites=[
        "03267000",  # [verified] Mad River near Urbana OH (the at-site supply/abstraction reach)
        "03267900",  # [verified] Mad River at St Paris Pike at Eagle City OH (downstream of Urbana)
    ],
    nasa_power_lat=40.1084,  # [verified] Urbana city centroid (Census place 3979002)
    nasa_power_lon=-83.7524,
    rsei_fips="39021",  # [verified] Champaign County, OH
    econ_fips="39021",
    eia861_utility_number=0,  # [open] pending the Champaign County retail utility (research)
    eia_state="OH",
    parcels_url="TODO",  # [open] pending the Champaign County, OH GIS REST endpoint discovery
    zoning_url="TODO",  # [open] pending the City of Urbana, OH GIS REST endpoint discovery
    floodzone_url=(  # [verified] FEMA NFHL S_FLD_HAZ_AR (national layer 28)
        "https://hazards.fema.gov/arcgis/rest/services/public/NFHL/MapServer/28"
    ),
    gnis_default_state="OH",
    hydro_utm_epsg=32617,  # [verified] UTM 17N (Urbana ~83.75 degW; zone 17 spans 84-78 degW)
    lsc_default_ga="136",  # [verified] Ohio 136th General Assembly (2025-2026); state-level
    gis_parcel=None,  # [open] pending Champaign County, OH parcel-layer discovery
    gis_zoning=None,  # [open] pending City of Urbana zoning-layer discovery
    gis_flood=NATIONAL_NFHL_FLOOD_SCHEMA.model_copy(update={"reference_dir": "urbana-gis"}),
    design_lat=40.1084,  # [verified] city centroid = NOAA Atlas-14 point
    design_lon=-83.7524,
    corridor_name="Mad River buried-valley corridor",  # [inference] the Mad River valley reach at Urbana
    dominant_hsg="B",  # [inference] Mad River buried-valley outwash sand & gravel (well-drained valley fill)
    hsg_citation=(
        "Champaign County / Mad River valley at Urbana sits on the Mad River buried-valley aquifer "
        "— glacial outwash sand & gravel, a US-EPA designated sole-source aquifer feeding the "
        "Springfield/Dayton/Wright-Patterson AFB corridor downstream — so the valley fill is "
        "well-drained HSG B, the INVERSE of the Maumee lake-plain Black Swamp clays (HSG D); "
        "[inference] pending an SSURGO area-weighted confirmation (onboard SSURGO needs a footprint)"
    ),
    pre_cover="TODO",  # [open] development land-cover scenario — pending an identified site
    post_cover="TODO",
    developed_pervious_cover="TODO",
    noaa_fallback_24h_depth_in={},  # [open] pending the NOAA Atlas-14 pull (onboard corridor-DDF step)
    parcels_relpath="reference/urbana/bosc-parcels.geojson",  # [open] commit the site's own geometry
    footprint_relpath="extracted/urbana/bosc-site-footprint.yaml",  # [open] pending an identified site
    climatology_relpath="reference/hydrology/urbana/nasa-power-climatology.yaml",
    corridor_ddf_relpath="reference/hydrology/urbana/atlas14-corridor-ddf.yaml",
    baseline_relpath="reference/economics/urbana/baseline.yaml",
    rsei_relpath="reference/rsei/urbana/inventory.yaml",
    consumer_energy_relpath="reference/eia/urbana/consumer-energy.yaml",
    grid_relpath="reference/eia/urbana/grid-profile.yaml",
    toxic_corridor_bbox=(
        0.0,
        0.0,
        0.0,
        0.0,
    ),  # [open] pending an identified corridor on the Mad River
    receiving_water_name="Mad River",  # [verified] the Mad River reach at Urbana (→ Great Miami → Ohio R.)
    plant_receiving={},  # [open] pending the Urbana-area WWTP NPDES fact sheet(s)
    abstraction_gage="03267000",  # [verified] Mad River near Urbana OH
    supply_gage_primary="03267000",  # [verified] Mad River near Urbana
    supply_gage_secondary="03267900",  # [verified] Mad River at Eagle City (downstream)
    passby_primary_cfs=0.0,  # [open] pending the in-stream passby minimum
    passby_secondary_cfs=0.0,  # [open]
    facility=None,  # [open] the WPAFB-corridor data-center dimension is the research target (#440)
    serving_utility_citation="[open] pending Champaign County, OH retail utility verification (research)",
    serving_utility_source="reference",
    lmp_usd_mwh=35.0,  # [inference] PJM placeholder — likely the DAY zone (AES Ohio/DP&L); pin via research
    lmp_citation=(
        "PJM LMP placeholder for the Urbana area; [inference] the PJM transmission zone is not yet "
        "pinned — likely the DAY zone (Dayton/AES Ohio territory) — verify the utility + zone (research)"
    ),
    lmp_pnode_id=0,  # [open] pending the Champaign County PJM zone (likely DAY)
    lmp_pnode_name="",
    county_name="Champaign County, OH",  # [verified]
    map_view_lat=40.1084,
    map_view_lon=-83.7524,
    map_view_zoom=13,
)


# The network's SECOND Miami-basin site (onboarding #452 under epic #451) and the MID-CORRIDOR
# node of the Mad River line: Springfield sits ~20 mi downstream of Urbana and ~25 mi upstream
# of Dayton / Wright-Patterson AFB, on the same **Mad River buried-valley sole-source aquifer**
# (US-EPA designated) — the Springfield municipal well field is the textbook draw on that
# outwash sand & gravel. What distinguishes Springfield from headwater Urbana is a SECOND
# supply water: **Buck Creek**, regulated by USACE **C.J. Brown Reservoir** (a flood-control +
# water-supply impoundment NE of the city), joining the Mad River at Springfield — a managed,
# two-source hydrology versus Urbana's single free-flowing reach. The data-center dimension is
# the corpus thread the Springfield epic (#451) tracks (the in-record Roshel / International
# Motors activity at the Springfield-Beckley APA, 2026-03-30); all such fields stay [open]
# research targets filled by `bosc onboard springfield --research`.
_SPRINGFIELD = SiteProfile(
    slug="springfield",
    place="Springfield",
    basin="great-miami",  # [verified] Mad River → Great Miami River → Ohio River (HUC-8 05080001)
    nwis_sites=[
        "03269500",  # [verified] Mad River near Springfield OH (the at-site supply/abstraction reach)
        "03267900",  # [verified] Mad River at St Paris Pike at Eagle City OH (upstream, Urbana→Springfield)
        "03268100",  # [verified] Buck Creek bl CJ Brown Reservoir nr Springfield OH (the second supply water)
    ],
    nasa_power_lat=39.9242,  # [verified] Springfield, OH city centroid (39deg55'27"N 83deg48'32"W)
    nasa_power_lon=-83.8089,
    rsei_fips="39023",  # [verified] Clark County, OH
    econ_fips="39023",
    eia861_utility_number=0,  # [open] pending the Clark County retail utility (research)
    eia_state="OH",
    parcels_url="TODO",  # [open] pending the Clark County, OH GIS REST endpoint discovery
    zoning_url="TODO",  # [open] pending the City of Springfield, OH GIS REST endpoint discovery
    floodzone_url=(  # [verified] FEMA NFHL S_FLD_HAZ_AR (national layer 28)
        "https://hazards.fema.gov/arcgis/rest/services/public/NFHL/MapServer/28"
    ),
    gnis_default_state="OH",
    hydro_utm_epsg=32617,  # [verified] UTM 17N (Springfield ~83.81 degW; zone 17 spans 84-78 degW)
    lsc_default_ga="136",  # [verified] Ohio 136th General Assembly (2025-2026); state-level
    gis_parcel=None,  # [open] pending Clark County, OH parcel-layer discovery
    gis_zoning=None,  # [open] pending City of Springfield zoning-layer discovery
    gis_flood=NATIONAL_NFHL_FLOOD_SCHEMA.model_copy(update={"reference_dir": "springfield-gis"}),
    design_lat=39.9242,  # [verified] city centroid = NOAA Atlas-14 point
    design_lon=-83.8089,
    corridor_name="Mad River buried-valley corridor",  # [inference] the Mad River valley reach at Springfield
    dominant_hsg="B",  # [inference] Mad River buried-valley outwash sand & gravel (well-drained valley fill)
    hsg_citation=(
        "Clark County / Springfield sits on the Mad River buried-valley aquifer - glacial "
        "outwash sand & gravel, a US-EPA designated sole-source aquifer tapped directly by the "
        "Springfield municipal well field - so the valley fill is well-drained HSG B, the "
        "INVERSE of the Maumee lake-plain Black Swamp clays (HSG D); [inference] pending an "
        "SSURGO area-weighted confirmation (onboard SSURGO needs a footprint)"
    ),
    pre_cover="TODO",  # [open] development land-cover scenario — pending an identified site
    post_cover="TODO",
    developed_pervious_cover="TODO",
    noaa_fallback_24h_depth_in={},  # [open] pending the NOAA Atlas-14 pull (onboard corridor-DDF step)
    parcels_relpath="reference/springfield/bosc-parcels.geojson",  # [open] commit the site's own geometry
    footprint_relpath="extracted/springfield/bosc-site-footprint.yaml",  # [open] pending an identified site
    climatology_relpath="reference/hydrology/springfield/nasa-power-climatology.yaml",
    corridor_ddf_relpath="reference/hydrology/springfield/atlas14-corridor-ddf.yaml",
    baseline_relpath="reference/economics/springfield/baseline.yaml",
    rsei_relpath="reference/rsei/springfield/inventory.yaml",
    consumer_energy_relpath="reference/eia/springfield/consumer-energy.yaml",
    grid_relpath="reference/eia/springfield/grid-profile.yaml",
    toxic_corridor_bbox=(
        0.0,
        0.0,
        0.0,
        0.0,
    ),  # [open] pending an identified corridor on the Mad River
    receiving_water_name="Mad River",  # [verified] the Springfield WRF receiving water (→ Great Miami → Ohio R.)
    plant_receiving={},  # [open] pending the Springfield-area WWTP NPDES fact sheet(s)
    abstraction_gage="03269500",  # [verified] Mad River near Springfield OH
    supply_gage_primary="03269500",  # [verified] Mad River near Springfield
    supply_gage_secondary="03268100",  # [verified] Buck Creek bl CJ Brown Reservoir (the second supply water)
    passby_primary_cfs=0.0,  # [open] pending the in-stream passby minimum
    passby_secondary_cfs=0.0,  # [open]
    facility=None,  # [open] the WPAFB-corridor / Roshel-APA data-center dimension is the research target (#451)
    serving_utility_citation="[open] pending Clark County, OH retail utility verification (research)",
    serving_utility_source="reference",
    lmp_usd_mwh=35.0,  # [inference] PJM placeholder — Clark County sits at the AEP/DAY seam; pin via research
    lmp_citation=(
        "PJM LMP placeholder for the Springfield area; [inference] the PJM transmission zone is "
        "not yet pinned - Clark County sits at the AEP/DAY seam - verify the utility + zone (research)"
    ),
    lmp_pnode_id=0,  # [open] pending the Clark County PJM zone
    lmp_pnode_name="",
    county_name="Clark County, OH",  # [verified]
    map_view_lat=39.9242,
    map_view_lon=-83.8089,
    map_view_zoom=13,
)


# The network's FIRST Little Miami-basin site (a THIRD basin branch, after Maumee and Great
# Miami) and the WPAFB-adjacent node: Xenia / Greene County sits on the **Little Miami River**,
# SE of Wright-Patterson AFB. Its distinguishing influence is NOT a new geology but a heightened
# **regulatory overlay** the other sites lack — the Little Miami is a **National & State Scenic
# River** (NPS Wild & Scenic + Ohio Scenic River), a protected receiving water that materially
# constrains a large new discharger/withdrawal. The aquifer is the same buried-valley sole-source
# system (Greene County's Xenia/Beavercreek well fields draw on the Mad River / Little Miami
# outwash valleys), but the inter-valley till uplands at Xenia proper are less permeable than the
# Mad River outwash - so the dominant HSG is footprint-dependent. The WPAFB defense-supplier
# corridor + the base groundwater plume are the [open] data-center/contamination overlays (#444).
_XENIA = SiteProfile(
    slug="xenia",
    place="Xenia",
    basin="little-miami",  # [verified] Little Miami River → Ohio River (HUC-8 05090202); a 3rd basin branch
    nwis_sites=[
        "03240000",  # [verified] Little Miami River near Oldtown OH (at-site reach, just N of Xenia)
        "03241500",  # [verified] Massies Creek at Wilberforce OH (the local tributary E of Xenia)
        "03242050",  # [verified] Little Miami River near Spring Valley OH (downstream, Greene/Warren)
    ],
    nasa_power_lat=39.6861,  # [verified] Xenia, OH city centroid (39deg41'10"N 83deg55'44"W)
    nasa_power_lon=-83.9289,
    rsei_fips="39057",  # [verified] Greene County, OH
    econ_fips="39057",
    eia861_utility_number=0,  # [open] pending the Greene County retail utility (research; likely AES Ohio/DAY)
    eia_state="OH",
    parcels_url="TODO",  # [open] pending the Greene County, OH GIS REST endpoint discovery
    zoning_url="TODO",  # [open] pending the City of Xenia / Greene County zoning REST endpoint discovery
    floodzone_url=(  # [verified] FEMA NFHL S_FLD_HAZ_AR (national layer 28)
        "https://hazards.fema.gov/arcgis/rest/services/public/NFHL/MapServer/28"
    ),
    gnis_default_state="OH",
    hydro_utm_epsg=32617,  # [verified] UTM 17N (Xenia ~83.93 degW; zone 17 spans 84-78 degW)
    lsc_default_ga="136",  # [verified] Ohio 136th General Assembly (2025-2026); state-level
    gis_parcel=None,  # [open] pending Greene County, OH parcel-layer discovery
    gis_zoning=None,  # [open] pending City of Xenia / Greene County zoning-layer discovery
    gis_flood=NATIONAL_NFHL_FLOOD_SCHEMA.model_copy(update={"reference_dir": "xenia-gis"}),
    design_lat=39.6861,  # [verified] city centroid = NOAA Atlas-14 point
    design_lon=-83.9289,
    corridor_name="Little Miami buried-valley corridor",  # [inference] the Little Miami valley reach at Xenia
    dominant_hsg="B",  # [inference] Greene County buried-valley outwash (valley fill); footprint-dependent
    hsg_citation=(
        "Greene County is underlain by the Mad River / Little Miami buried-valley aquifer system "
        "- glacial outwash sand & gravel, a US-EPA sole-source aquifer the Xenia/Beavercreek well "
        "fields draw on [reference: ODNR/USGS] - so the valley fill is well-drained HSG A/B; but "
        "the inter-valley till uplands at Xenia proper are less permeable (HSG C/D), so the "
        "dominant class is footprint-dependent; [inference] pending an SSURGO area-weighted "
        "confirmation (onboard SSURGO needs a footprint)"
    ),
    pre_cover="TODO",  # [open] development land-cover scenario — pending an identified site
    post_cover="TODO",
    developed_pervious_cover="TODO",
    noaa_fallback_24h_depth_in={},  # [open] pending the NOAA Atlas-14 pull (onboard corridor-DDF step)
    parcels_relpath="reference/xenia/bosc-parcels.geojson",  # [open] commit the site's own geometry
    footprint_relpath="extracted/xenia/bosc-site-footprint.yaml",  # [open] pending an identified site
    climatology_relpath="reference/hydrology/xenia/nasa-power-climatology.yaml",
    corridor_ddf_relpath="reference/hydrology/xenia/atlas14-corridor-ddf.yaml",
    baseline_relpath="reference/economics/xenia/baseline.yaml",
    rsei_relpath="reference/rsei/xenia/inventory.yaml",
    consumer_energy_relpath="reference/eia/xenia/consumer-energy.yaml",
    grid_relpath="reference/eia/xenia/grid-profile.yaml",
    toxic_corridor_bbox=(
        0.0,
        0.0,
        0.0,
        0.0,
    ),  # [open] pending an identified corridor (incl. the WPAFB plume overlay)
    receiving_water_name="Little Miami River",  # [verified] reach; [reference] a National & State Scenic River
    plant_receiving={},  # [open] pending the Xenia-area WWTP NPDES fact sheet(s)
    abstraction_gage="03240000",  # [verified] Little Miami River near Oldtown OH
    supply_gage_primary="03240000",  # [verified] Little Miami River near Oldtown
    supply_gage_secondary="03241500",  # [verified] Massies Creek at Wilberforce (the local tributary)
    passby_primary_cfs=0.0,  # [open] pending the in-stream passby minimum (scenic-river protection likely raises it)
    passby_secondary_cfs=0.0,  # [open]
    facility=None,  # [open] the WPAFB-corridor defense/data-center dimension is the research target (#444)
    serving_utility_citation="[open] pending Greene County, OH retail utility verification (research)",
    serving_utility_source="reference",
    lmp_usd_mwh=35.0,  # [inference] PJM placeholder — likely the DAY zone (AES Ohio, Dayton area); pin via research
    lmp_citation=(
        "PJM LMP placeholder for the Xenia area; [inference] the PJM transmission zone is not yet "
        "pinned - likely the DAY zone (AES Ohio / Dayton territory) - verify the utility + zone (research)"
    ),
    lmp_pnode_id=0,  # [open] pending the Greene County PJM zone (likely DAY)
    lmp_pnode_name="",
    county_name="Greene County, OH",  # [verified]
    map_view_lat=39.6861,
    map_view_lon=-83.9289,
    map_view_zoom=13,
)


# The DOWNSTREAM TERMINUS of the Mad River corridor (Urbana → Springfield → **Dayton/WPAFB**) and
# the richest node of the Miami expansion: the SW-Ohio analog to Lima's JSMC / tank-plant defense
# nexus. Wright-Patterson AFB (AFRL, the Air Force Rapid Sustainment Office, AFLCMC) is one of
# Ohio's largest single-site employers, and — unlike the bare greenfield Miami sites — **the corpus
# already carries this thread**: written testimony §8 "Ohio defense footprint" (Google Distributed
# Cloud air-gapped DoD IL5, RSO a named early customer, GDIT + Google Public Sector at Exercise
# Mobility Guardian 2025) + the `cloud-consumer-candidates.yaml` WPAFB-adjacent corridor entry. The
# distinctive data-center variant here is **regulated/air-gapped DoD cloud**, not hyperscale. Two
# overlays make it load-bearing: WPAFB runs its own production well-field on the **Great Miami /
# Mad River Buried Valley Aquifer** (US-EPA sole-source) and is the source of a documented **TCE /
# PFAS groundwater plume** on that same drinking-water aquifer. The buried-valley supply (not surface
# 7Q10 dilution) is the water story. GEOGRAPHY NOTES: the base STRADDLES Greene + Montgomery counties
# — the economic/toxics unit chosen here is **Montgomery County (Dayton metro, FIPS 39113)** (the
# well-field + defense-metro + plume context), distinct from the Greene-County (Xenia #444) economics
# on the Little Miami side; and at ~84.05 degW the base is WEST of the 84 degW meridian, so it is the
# network's first **UTM zone 16N** site (NOT the zone 17 the other Miami sites use).
_WPAFB = SiteProfile(
    slug="wpafb",
    place="Wright-Patterson AFB",
    basin="great-miami",  # [verified] Mad River → Great Miami River → Ohio River (HUC-8 05080001/2)
    nwis_sites=[
        "03270000",  # [verified] Mad River near Dayton OH (the at-base reach; corridor terminus)
        "03270500",  # [verified] Great Miami River at Dayton OH (metro mainstem / well-field reach)
        "03263000",  # [verified] Great Miami River at Taylorsville OH (upstream of the Mad confluence)
    ],
    nasa_power_lat=39.8261,  # [verified] Wright-Patterson AFB centroid (39deg49'34"N 84deg02'58"W)
    nasa_power_lon=-84.0494,
    rsei_fips="39113",  # [verified] Montgomery County, OH (Dayton metro; base straddles Greene+Montgomery)
    econ_fips="39113",
    eia861_utility_number=0,  # [open] pending the Montgomery County retail utility (research; likely AES Ohio/DAY)
    eia_state="OH",
    parcels_url="TODO",  # [open] pending the Montgomery County, OH GIS REST endpoint discovery
    zoning_url="TODO",  # [open] pending the City of Dayton / Montgomery County zoning REST endpoint discovery
    floodzone_url=(  # [verified] FEMA NFHL S_FLD_HAZ_AR (national layer 28)
        "https://hazards.fema.gov/arcgis/rest/services/public/NFHL/MapServer/28"
    ),
    gnis_default_state="OH",
    hydro_utm_epsg=32616,  # [verified] UTM 16N (WPAFB ~84.05 degW; zone 16 spans 90-84 degW) — NOT zone 17
    lsc_default_ga="136",  # [verified] Ohio 136th General Assembly (2025-2026); state-level
    gis_parcel=None,  # [open] pending Montgomery County, OH parcel-layer discovery (+ the WPAFB federal enclave)
    gis_zoning=None,  # [open] pending City of Dayton / Montgomery County zoning-layer discovery
    gis_flood=NATIONAL_NFHL_FLOOD_SCHEMA.model_copy(update={"reference_dir": "wpafb-gis"}),
    design_lat=39.8261,  # [verified] base centroid = NOAA Atlas-14 point
    design_lon=-84.0494,
    corridor_name="Great Miami / Mad River buried-valley corridor (Dayton terminus)",  # [inference]
    dominant_hsg="B",  # [inference] Great Miami / Mad River buried-valley outwash (well-drained valley fill)
    hsg_citation=(
        "Dayton / WPAFB sits on the Great Miami / Mad River Buried Valley Aquifer - glacial outwash "
        "sand & gravel, a US-EPA designated sole-source aquifer (the Dayton municipal + WPAFB "
        "production well fields draw on it) - so the valley fill is well-drained HSG A/B, the INVERSE "
        "of the Maumee lake-plain Black Swamp clays (HSG D); [inference] pending an SSURGO "
        "area-weighted confirmation (onboard SSURGO needs a footprint)"
    ),
    pre_cover="TODO",  # [open] development land-cover scenario — pending an identified site
    post_cover="TODO",
    developed_pervious_cover="TODO",
    noaa_fallback_24h_depth_in={},  # [open] pending the NOAA Atlas-14 pull (onboard corridor-DDF step)
    parcels_relpath="reference/wpafb/bosc-parcels.geojson",  # [open] commit the site's own geometry
    footprint_relpath="extracted/wpafb/bosc-site-footprint.yaml",  # [open] pending an identified site
    climatology_relpath="reference/hydrology/wpafb/nasa-power-climatology.yaml",
    corridor_ddf_relpath="reference/hydrology/wpafb/atlas14-corridor-ddf.yaml",
    baseline_relpath="reference/economics/wpafb/baseline.yaml",
    rsei_relpath="reference/rsei/wpafb/inventory.yaml",
    consumer_energy_relpath="reference/eia/wpafb/consumer-energy.yaml",
    grid_relpath="reference/eia/wpafb/grid-profile.yaml",
    toxic_corridor_bbox=(
        0.0,
        0.0,
        0.0,
        0.0,
    ),  # [open] pending the identified corridor (the WPAFB TCE/PFAS plume + Dayton industrial reach)
    receiving_water_name="Mad River",  # [verified] the at-base reach (→ Great Miami → Ohio R.); aquifer is the supply story
    plant_receiving={},  # [open] pending the WPAFB / Dayton WWTP NPDES fact sheet(s)
    abstraction_gage="03270000",  # [verified] Mad River near Dayton OH
    supply_gage_primary="03270000",  # [verified] Mad River near Dayton (the buried-valley supply reach)
    supply_gage_secondary="03270500",  # [verified] Great Miami River at Dayton (the well-field mainstem)
    passby_primary_cfs=0.0,  # [open] pending the in-stream passby minimum
    passby_secondary_cfs=0.0,  # [open]
    facility=None,  # [open] the DoD-cloud / GDIT-RSO data-center dimension is the research target (#442)
    serving_utility_citation="[open] pending Montgomery County, OH retail utility verification (research)",
    serving_utility_source="reference",
    lmp_usd_mwh=35.0,  # [inference] PJM placeholder — likely the DAY zone (AES Ohio, Dayton area); pin via research
    lmp_citation=(
        "PJM LMP placeholder for the Dayton/WPAFB area; [inference] the PJM transmission zone is not "
        "yet pinned - likely the DAY zone (AES Ohio / Dayton territory) - verify the utility + zone (research)"
    ),
    lmp_pnode_id=0,  # [open] pending the Montgomery County PJM zone (likely DAY)
    lmp_pnode_name="",
    county_name="Montgomery County, OH",  # [verified] (Dayton metro; base straddles Greene+Montgomery)
    map_view_lat=39.8261,
    map_view_lon=-84.0494,
    map_view_zoom=12,
)


# The LOWER Great Miami **heavy-industry** node and the I-75 Cincinnati-Dayton corridor's southern
# anchor, near the Great Miami's Ohio River confluence. This is the **established-industry comparator**
# to the speculative-greenfield Miami sites: **Cleveland-Cliffs Middletown Works** (the former AK Steel
# integrated mill) anchors a legacy steel/paper/chemicals corridor of large existing water users +
# NPDES dischargers on the Great Miami **mainstem** — so unlike the bare headwaters, the toxics/NPDES
# dimension here is REAL and rich. The water story shifts too: the lower Great Miami is a large
# mainstem (genuine dilution capacity), not a buried-valley headwater 7Q10 — though the buried-valley
# sole-source aquifer is wider here near the confluence. The grid story is distinctive: the City of
# Hamilton runs its own **municipal electric utility** (AMP member, home-rule — the EIA-861S short-form
# pattern), while Middletown is Duke Energy Ohio; both settle in PJM's **DEOK** (Duke Energy Ohio/
# Kentucky) zone — a third PJM zone for the network (after AEP and DAY). DISAMBIGUATION: the City of
# Hamilton is the seat of **Butler County (FIPS 39017)** — NOT Hamilton County, OH (which is
# Cincinnati). Both cities sit west of the 84 degW meridian, so this is a **UTM 16N** site (like WPAFB).
_HAMILTON_MIDDLETOWN = SiteProfile(
    slug="hamilton-middletown",
    place="Hamilton · Middletown",
    basin="great-miami",  # [verified] lower Great Miami River → Ohio River (HUC-8 05080002)
    nwis_sites=[
        "03274000",  # [verified] Great Miami River at Hamilton OH (downstream reach; Hamilton well-field)
        "03272100",  # [verified] Great Miami River at Middletown OH (the Middletown Works reach)
    ],
    nasa_power_lat=39.3994,  # [verified] Hamilton, OH city centroid (39deg23'58"N 84deg33'41"W)
    nasa_power_lon=-84.5613,
    rsei_fips="39017",  # [verified] Butler County, OH (seat = City of Hamilton; NOT Hamilton County/Cincinnati)
    econ_fips="39017",
    eia861_utility_number=0,  # [open] Hamilton muni (AMP; EIA-861S short-form) vs Middletown=Duke — pin via research
    eia_state="OH",
    parcels_url="TODO",  # [open] pending the Butler County, OH GIS REST endpoint discovery
    zoning_url="TODO",  # [open] pending the City of Hamilton / Middletown GIS REST endpoint discovery
    floodzone_url=(  # [verified] FEMA NFHL S_FLD_HAZ_AR (national layer 28)
        "https://hazards.fema.gov/arcgis/rest/services/public/NFHL/MapServer/28"
    ),
    gnis_default_state="OH",
    hydro_utm_epsg=32616,  # [verified] UTM 16N (Hamilton ~84.56 degW; zone 16 spans 90-84 degW) — NOT zone 17
    lsc_default_ga="136",  # [verified] Ohio 136th General Assembly (2025-2026); state-level
    gis_parcel=None,  # [open] pending Butler County, OH parcel-layer discovery
    gis_zoning=None,  # [open] pending City of Hamilton / Middletown zoning-layer discovery
    gis_flood=NATIONAL_NFHL_FLOOD_SCHEMA.model_copy(
        update={"reference_dir": "hamilton-middletown-gis"}
    ),
    design_lat=39.3994,  # [verified] Hamilton centroid = NOAA Atlas-14 point
    design_lon=-84.5613,
    corridor_name="Lower Great Miami industrial corridor",  # [inference] the Hamilton-Middletown mainstem reach
    dominant_hsg="B",  # [inference] lower Great Miami buried-valley outwash (wider near the Ohio confluence)
    hsg_citation=(
        "The lower Great Miami valley (Hamilton/Middletown, Butler County) sits on the Great Miami "
        "Buried Valley Aquifer - glacial outwash sand & gravel, a US-EPA designated sole-source "
        "aquifer, wider near the Ohio River confluence - so the valley fill is well-drained HSG A/B, "
        "the INVERSE of the Maumee lake-plain Black Swamp clays (HSG D); [inference] pending an "
        "SSURGO area-weighted confirmation (onboard SSURGO needs a footprint)"
    ),
    pre_cover="TODO",  # [open] development land-cover scenario — pending an identified site
    post_cover="TODO",
    developed_pervious_cover="TODO",
    noaa_fallback_24h_depth_in={},  # [open] pending the NOAA Atlas-14 pull (onboard corridor-DDF step)
    parcels_relpath="reference/hamilton-middletown/bosc-parcels.geojson",  # [open] commit the site's own geometry
    footprint_relpath="extracted/hamilton-middletown/bosc-site-footprint.yaml",  # [open] pending an identified site
    climatology_relpath="reference/hydrology/hamilton-middletown/nasa-power-climatology.yaml",
    corridor_ddf_relpath="reference/hydrology/hamilton-middletown/atlas14-corridor-ddf.yaml",
    baseline_relpath="reference/economics/hamilton-middletown/baseline.yaml",
    rsei_relpath="reference/rsei/hamilton-middletown/inventory.yaml",
    consumer_energy_relpath="reference/eia/hamilton-middletown/consumer-energy.yaml",
    grid_relpath="reference/eia/hamilton-middletown/grid-profile.yaml",
    toxic_corridor_bbox=(
        0.0,
        0.0,
        0.0,
        0.0,
    ),  # [open] pending the identified corridor (the Middletown Works + Hamilton industrial reach)
    receiving_water_name="Great Miami River",  # [verified] the lower Great Miami mainstem (→ Ohio R.)
    plant_receiving={},  # [open] pending the Hamilton/Middletown WWTP + industrial NPDES fact sheet(s)
    abstraction_gage="03274000",  # [verified] Great Miami River at Hamilton OH
    supply_gage_primary="03274000",  # [verified] Great Miami River at Hamilton
    supply_gage_secondary="03272100",  # [verified] Great Miami River at Middletown (the Works reach)
    passby_primary_cfs=0.0,  # [open] pending the in-stream passby minimum
    passby_secondary_cfs=0.0,  # [open]
    facility=None,  # [open] the I-75-corridor data-center dimension is the research target (#443)
    serving_utility_citation="[open] pending Butler County retail utility verification (Hamilton muni / Duke; research)",
    serving_utility_source="reference",
    lmp_usd_mwh=35.0,  # [inference] PJM placeholder — Butler County is the DEOK zone (Duke Energy OH/KY); pin via research
    lmp_citation=(
        "PJM LMP placeholder for the Hamilton/Middletown area; [inference] the PJM transmission zone "
        "is not yet pinned - Butler County is the DEOK zone (Duke Energy Ohio/Kentucky), with Hamilton "
        "on its own municipal system (AMP) - verify the utility + zone (research)"
    ),
    lmp_pnode_id=0,  # [open] pending the Butler County PJM zone (DEOK)
    lmp_pnode_name="",
    county_name="Butler County, OH",  # [verified] (seat = City of Hamilton; NOT Hamilton County/Cincinnati)
    map_view_lat=39.455,  # centered on the lower Great Miami reach between Hamilton + Middletown
    map_view_lon=-84.49,
    map_view_zoom=11,
)


# The UPPER Great Miami mainstem node (Miami County) — the I-75 corridor between the Great Miami
# headwaters (Indian Lake / Sidney) and Dayton, **upstream of WPAFB** — the upstream complement to
# the lower-mainstem Hamilton/Middletown node. Same buried-valley sole-source aquifer, but a mid-size
# **manufacturing** county (Hobart commercial food equipment HQ in Troy, auto parts) rather than
# Butler's heavy steel, and a second muni-power story: **Piqua runs its own municipal electric
# utility** (AMP member, Great Miami hydro), Troy/Miami County otherwise likely AES Ohio. The site
# also carries a distinct second supply water — the **Stillwater River** (gage 03265000). Both cities
# sit west of the 84 degW meridian, so this is a **UTM 16N** site (like WPAFB / Hamilton-Middletown).
_TROY_PIQUA = SiteProfile(
    slug="troy-piqua",
    place="Troy · Piqua",
    basin="great-miami",  # [verified] upper Great Miami River → Ohio River (HUC-8 05080001)
    nwis_sites=[
        "03262700",  # [verified] Great Miami River at Troy OH (the Troy reach; county seat)
        "03262500",  # [verified] Great Miami River at Piqua OH (the upstream Piqua reach)
        "03265000",  # [verified] Stillwater River at Pleasant Hill OH (the second supply water)
    ],
    nasa_power_lat=40.0392,  # [verified] Troy, OH city centroid (40deg02'21"N 84deg12'12"W)
    nasa_power_lon=-84.2033,
    rsei_fips="39109",  # [verified] Miami County, OH
    econ_fips="39109",
    eia861_utility_number=0,  # [open] Piqua muni (AMP) vs Troy/Miami Co — pin via research
    eia_state="OH",
    parcels_url="TODO",  # [open] pending the Miami County, OH GIS REST endpoint discovery
    zoning_url="TODO",  # [open] pending the City of Troy / Piqua GIS REST endpoint discovery
    floodzone_url=(  # [verified] FEMA NFHL S_FLD_HAZ_AR (national layer 28)
        "https://hazards.fema.gov/arcgis/rest/services/public/NFHL/MapServer/28"
    ),
    gnis_default_state="OH",
    hydro_utm_epsg=32616,  # [verified] UTM 16N (Troy ~84.20 degW; zone 16 spans 90-84 degW) — NOT zone 17
    lsc_default_ga="136",  # [verified] Ohio 136th General Assembly (2025-2026); state-level
    gis_parcel=None,  # [open] pending Miami County, OH parcel-layer discovery
    gis_zoning=None,  # [open] pending City of Troy / Piqua zoning-layer discovery
    gis_flood=NATIONAL_NFHL_FLOOD_SCHEMA.model_copy(update={"reference_dir": "troy-piqua-gis"}),
    design_lat=40.0392,  # [verified] Troy centroid = NOAA Atlas-14 point
    design_lon=-84.2033,
    corridor_name="Upper Great Miami industrial corridor",  # [inference] the Troy-Piqua mainstem reach
    dominant_hsg="B",  # [inference] upper Great Miami buried-valley outwash (well-drained valley fill)
    hsg_citation=(
        "The upper Great Miami valley (Troy/Piqua, Miami County) sits on the Great Miami Buried "
        "Valley Aquifer - glacial outwash sand & gravel, a US-EPA designated sole-source aquifer "
        "the Troy/Piqua well fields draw on - so the valley fill is well-drained HSG A/B, the "
        "INVERSE of the Maumee lake-plain Black Swamp clays (HSG D); [inference] pending an SSURGO "
        "area-weighted confirmation (onboard SSURGO needs a footprint)"
    ),
    pre_cover="TODO",  # [open] development land-cover scenario — pending an identified site
    post_cover="TODO",
    developed_pervious_cover="TODO",
    noaa_fallback_24h_depth_in={},  # [open] pending the NOAA Atlas-14 pull (onboard corridor-DDF step)
    parcels_relpath="reference/troy-piqua/bosc-parcels.geojson",  # [open] commit the site's own geometry
    footprint_relpath="extracted/troy-piqua/bosc-site-footprint.yaml",  # [open] pending an identified site
    climatology_relpath="reference/hydrology/troy-piqua/nasa-power-climatology.yaml",
    corridor_ddf_relpath="reference/hydrology/troy-piqua/atlas14-corridor-ddf.yaml",
    baseline_relpath="reference/economics/troy-piqua/baseline.yaml",
    rsei_relpath="reference/rsei/troy-piqua/inventory.yaml",
    consumer_energy_relpath="reference/eia/troy-piqua/consumer-energy.yaml",
    grid_relpath="reference/eia/troy-piqua/grid-profile.yaml",
    toxic_corridor_bbox=(
        0.0,
        0.0,
        0.0,
        0.0,
    ),  # [open] pending the identified corridor (the Troy/Piqua manufacturing reach)
    receiving_water_name="Great Miami River",  # [verified] the upper Great Miami mainstem (→ Ohio R.)
    plant_receiving={},  # [open] pending the Troy/Piqua WWTP NPDES fact sheet(s)
    abstraction_gage="03262700",  # [verified] Great Miami River at Troy OH
    supply_gage_primary="03262700",  # [verified] Great Miami River at Troy
    supply_gage_secondary="03262500",  # [verified] Great Miami River at Piqua (the upstream reach)
    passby_primary_cfs=0.0,  # [open] pending the in-stream passby minimum
    passby_secondary_cfs=0.0,  # [open]
    facility=None,  # [open] the I-75-corridor data-center dimension is the research target (#475)
    serving_utility_citation="[open] pending Miami County retail utility verification (Piqua muni / AES Ohio; research)",
    serving_utility_source="reference",
    lmp_usd_mwh=35.0,  # [inference] PJM placeholder — likely the DAY zone (AES Ohio, Dayton area); pin via research
    lmp_citation=(
        "PJM LMP placeholder for the Troy/Piqua area; [inference] the PJM transmission zone is not "
        "yet pinned - likely the DAY zone (AES Ohio territory), with Piqua on its own municipal "
        "system (AMP) - verify the utility + zone (research)"
    ),
    lmp_pnode_id=0,  # [open] pending the Miami County PJM zone (likely DAY)
    lmp_pnode_name="",
    county_name="Miami County, OH",  # [verified]
    map_view_lat=40.092,  # centered on the upper Great Miami reach between Troy + Piqua
    map_view_lon=-84.215,
    map_view_zoom=11,
)


SITES: dict[str, SiteProfile] = {
    _LIMA.slug: _LIMA,
    _FINDLAY.slug: _FINDLAY,
    _FORT_WAYNE.slug: _FORT_WAYNE,
    _VAN_WERT.slug: _VAN_WERT,
    _TOLEDO.slug: _TOLEDO,
    _DEFIANCE.slug: _DEFIANCE,
    _BRYAN.slug: _BRYAN,
    _OTTAWA.slug: _OTTAWA,
    _URBANA.slug: _URBANA,
    _SPRINGFIELD.slug: _SPRINGFIELD,
    _XENIA.slug: _XENIA,
    _WPAFB.slug: _WPAFB,
    _HAMILTON_MIDDLETOWN.slug: _HAMILTON_MIDDLETOWN,
    _TROY_PIQUA.slug: _TROY_PIQUA,
}

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
    if origin is Literal:
        return repr(get_args(annotation)[0])  # first allowed value (constructible)
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
        elif not field.is_required():  # optional (e.g. facility) — absence is a valid state
            value = repr(field.get_default())
            comment = "  # optional (set only if the site has a documented facility)"
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
    for name, field in SiteProfile.model_fields.items():
        if name == "slug":
            continue
        value = getattr(prof, name)
        # An optional field left at its default (e.g. facility=None) is a deliberate absence,
        # not an unfilled gap — don't flag it.
        if not field.is_required() and value == field.get_default():
            continue
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
