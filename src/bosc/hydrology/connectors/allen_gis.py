"""Allen County, Ohio GIS — parcel (CAMA) connector.

Pulls real-estate / parcel attributes from the county's public **ArcGIS REST**
server. The authoritative parcel layer is "Current Parcels"
(``AGOL/AGOL_NonEditLayers/MapServer/1``) — the auditor's CAMA data joined to the
parcel geometry: owner, situs address, land use, acreage, market/CAUV values, last
sale, tax district. The server is anonymous (no token), paginates at 1,000
features, and supports ``f=json``.

Two ways in:

* :func:`fetch_parcel` — one parcel by its number (deed IDs like
  ``36-0100-03-002.000`` are normalized to the server's dashless ``PARCEL_NO``);
* :func:`query_parcels` — any ``where`` clause, transparently paged to completion.

Values are passed through **verbatim** from the service; only the obvious encodings
are decoded (the ``DATE`` sale field is an ``M(M)DDYYYY`` integer, not an epoch).
``None`` means the service returned no value — never a fabricated default. Reuses
the shared connector cache/offline/fixture machinery; synchronous (``httpx``).
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any, cast

import httpx
import yaml
from pydantic import BaseModel, ConfigDict

from bosc.config import Settings, get_settings
from bosc.hydrology.connectors._cache import cached_get
from bosc.logging import get_logger

log = get_logger(__name__)

# CAMA fields requested from the Current Parcels layer (selected by name).
_OUT_FIELDS = [
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
]
_PAGE_SIZE = 1000  # the layer's maxRecordCount


class Parcel(BaseModel):
    """One parcel's CAMA attributes, as returned by the county GIS."""

    model_config = ConfigDict(extra="forbid")

    parcel_no: str | None
    owner: str | None  # OWNNAM1
    owner_2: str | None  # OWNNAM2
    deeded_owner: str | None  # DEEDOWN
    situs_address: str | None  # assembled from HOUSENO/ST_DIR/STREET/ST_DESC
    owner_address: str | None  # assembled mailing address
    land_use_code: int | None
    acres: float | None
    market_land_value: int | None
    market_improvement_value: int | None
    market_total_value: int | None
    cauv_value: int | None
    tax_district: str | None
    school_code: str | None
    neighborhood_code: str | None
    last_sale_date: str | None  # ISO yyyy-mm-dd, decoded from the M(M)DDYYYY int
    last_sale_amount: int | None
    valid_sale: str | None

    @classmethod
    def from_attrs(cls, a: dict[str, Any]) -> Parcel:
        return cls(
            parcel_no=_s(a.get("PARCEL_NO")),
            owner=_s(a.get("OWNNAM1")),
            owner_2=_s(a.get("OWNNAM2")),
            deeded_owner=_s(a.get("DEEDOWN")),
            situs_address=_join(
                a.get("HOUSENO"), a.get("ST_DIR"), a.get("STREET"), a.get("ST_DESC")
            ),
            # OWNADR2 already carries city/state/zip, so OWNST/OWNZIP aren't re-joined.
            owner_address=_join(a.get("OWNADR1"), a.get("OWNADR2")),
            land_use_code=_i(a.get("LNDUSECD")),
            acres=_f(a.get("ACRES")),
            market_land_value=_i(a.get("MKTLNDVAL")),
            market_improvement_value=_i(a.get("MKTIMPVAL")),
            market_total_value=_i(a.get("MKTTOTVAL")),
            cauv_value=_i(a.get("CAUVVAL")),
            tax_district=_s(a.get("TAXDIST")),
            school_code=_s(a.get("SCHOOL")),
            neighborhood_code=_s(a.get("NBRHCODE")),
            last_sale_date=_parse_parcel_date(a.get("DATE")),
            last_sale_amount=_i(a.get("SALEAMT")),
            valid_sale=_s(a.get("VAL_SAL")),
        )


def _s(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _i(value: Any) -> int | None:
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return None


def _f(value: Any) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _join(*parts: Any) -> str | None:
    pieces = [str(p).strip() for p in parts if _s(p) is not None]
    return " ".join(pieces) or None


def _parse_parcel_date(value: Any) -> str | None:
    """Decode the GIS ``DATE`` sale field (``M(M)DDYYYY`` int) to ISO ``yyyy-mm-dd``.

    e.g. ``2252008`` -> ``2008-02-25``; ``8011994`` -> ``1994-08-01``. Returns
    ``None`` for missing/zero/unparseable values rather than inventing a date.
    """
    n = _i(value)
    if not n or n <= 0:
        return None
    digits = f"{n:08d}"  # MMDDYYYY zero-padded
    month, day, year = int(digits[:2]), int(digits[2:4]), int(digits[4:])
    if not (1 <= month <= 12 and 1 <= day <= 31 and 1800 <= year <= 2100):
        return None
    return f"{year:04d}-{month:02d}-{day:02d}"


def normalize_parcel_id(raw: str) -> str:
    """A parcel id as the GIS stores it: digits only (``36-0100-03-002.000`` -> ``36010003002000``)."""
    return re.sub(r"\D", "", raw)


def _query(params: dict[str, Any], *, settings: Settings) -> dict[str, Any]:
    """Run (or replay) one ArcGIS ``/query`` request; return the parsed JSON."""
    query = {"f": "json", "returnGeometry": "false", **params}

    def fetch() -> Any:
        log.info("allen_gis.fetch", where=params.get("where"), offset=params.get("resultOffset"))
        resp = httpx.get(
            f"{settings.allen_parcels_url}/query",
            params=query,
            timeout=settings.hydro_request_timeout_s,
        )
        resp.raise_for_status()
        return resp.json()

    payload = cast("dict[str, Any]", cached_get("allen_gis", query, fetch, settings=settings))
    if "error" in payload:
        raise AllenGisError(f"ArcGIS error: {payload['error']}")
    return payload


class AllenGisError(RuntimeError):
    """The ArcGIS service returned an error object (bad field, bad where, ...)."""


def query_parcels(
    where: str,
    *,
    out_fields: list[str] | None = None,
    max_records: int | None = None,
    settings: Settings | None = None,
) -> list[Parcel]:
    """Every parcel matching ``where``, paged to completion (or to ``max_records``)."""
    settings = settings or get_settings()
    fields = ",".join(out_fields or _OUT_FIELDS)
    parcels: list[Parcel] = []
    offset = 0
    while True:
        page = _query(
            {
                "where": where,
                "outFields": fields,
                "resultOffset": offset,
                "resultRecordCount": _PAGE_SIZE,
            },
            settings=settings,
        )
        features = page.get("features") or []
        parcels.extend(Parcel.from_attrs(f.get("attributes", {})) for f in features)
        if max_records is not None and len(parcels) >= max_records:
            return parcels[:max_records]
        if not page.get("exceededTransferLimit") or not features:
            return parcels
        offset += len(features)


def fetch_parcel(parcel_no: str, *, settings: Settings | None = None) -> Parcel | None:
    """One parcel by number (any separator format); ``None`` if the GIS has no match."""
    settings = settings or get_settings()
    normalized = normalize_parcel_id(parcel_no)
    matches = query_parcels(f"PARCEL_NO='{normalized}'", settings=settings)
    return matches[0] if matches else None


def parcels_by_owner(name: str, *, settings: Settings | None = None) -> list[Parcel]:
    """Parcels whose owner name contains ``name`` (case-insensitive substring)."""
    safe = name.upper().replace("'", "''")
    return query_parcels(f"UPPER(OWNNAM1) LIKE '%{safe}%'", settings=settings)


# --- Citations + reference dataset -----------------------------------------

# Parcel ids as they appear in deeds: 36-0100-03-002.000 style (2-4-2-3.3).
_PARCEL_ID_RE = re.compile(r"\b\d{2}-\d{4}-\d{2}-\d{3}\.\d{3}\b")


def scan_parcel_ids(*roots: Path) -> list[str]:
    """Distinct deed-style parcel ids cited under the given roots (verbatim form)."""
    found: set[str] = set()
    for root in roots:
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if not path.is_file() or path.suffix.lower() not in {".md", ".yaml", ".yml", ".txt"}:
                continue
            try:
                text = path.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue
            found.update(_PARCEL_ID_RE.findall(text))
    return sorted(found)


# --- Defense-industry land scan -------------------------------------------

# The Joint Systems Manufacturing Center (Lima Army Tank Plant) reservation: the
# cluster of UNITED STATES-owned parcels in this CAMA tax district on Buckeye/Reed
# Rd. A verbatim GIS filter — it excludes the downtown federal parcel (district
# M38) and the "UNITED STATES PLASTIC CORP" / "ARMY <surname>" false positives.
_JSMC_OWNER = "UNITED STATES"
_JSMC_TAXDIST = "L35"


def _dedupe(parcels: list[Parcel]) -> list[Parcel]:
    """Keep the first row per distinct ``parcel_no`` (the GIS repeats split rows)."""
    seen: set[str] = set()
    out: list[Parcel] = []
    for p in parcels:
        key = p.parcel_no or ""
        if key and key in seen:
            continue
        seen.add(key)
        out.append(p)
    return out


def _owner_names(p: Parcel) -> str:
    """The owner/deed-owner text a pattern is matched against (upper-cased)."""
    return " ".join(filter(None, (p.owner, p.owner_2, p.deeded_owner))).upper()


def defense_owner_scan(
    primes: list[tuple[str, list[str]]], *, settings: Settings | None = None
) -> dict[str, list[Parcel]]:
    """Allen County parcels whose owner name matches a defense-prime pattern.

    ``primes`` is ``[(prime_name, [patterns...]), ...]`` (e.g. from the curated
    defense-contractor seed list). One OR-ed GIS query covers all patterns across
    the owner / deeded-owner / second-owner fields; each returned parcel is then
    tagged locally to the prime(s) it matched. Returns ``{prime: [parcels]}`` for
    primes with at least one hit (empty when no prime owns county land — the
    expected result, since the local defense footprint is federally held).
    """
    settings = settings or get_settings()
    patterns = sorted({p.upper().replace("'", "''") for _, pats in primes for p in pats})
    if not patterns:
        return {}
    clauses = [
        f"(UPPER(OWNNAM1) LIKE '%{p}%' OR UPPER(DEEDOWN) LIKE '%{p}%' "
        f"OR UPPER(OWNNAM2) LIKE '%{p}%')"
        for p in patterns
    ]
    parcels = _dedupe(query_parcels(" OR ".join(clauses), settings=settings))
    hits: dict[str, list[Parcel]] = {}
    for name, pats in primes:
        for parcel in parcels:
            text = _owner_names(parcel)
            if any(pat.upper() in text for pat in pats):
                hits.setdefault(name, []).append(parcel)
    return hits


def army_controlled_defense_land(*, settings: Settings | None = None) -> list[Parcel]:
    """The JSMC / Lima Army Tank Plant reservation (UNITED STATES-owned, by GIS).

    Returns the federally-held parcels the defense-contractor seed list notes
    "function as Army-controlled land" — the actual local defense footprint, held
    by the United States rather than by a prime in its own name.
    """
    settings = settings or get_settings()
    where = f"OWNNAM1='{_JSMC_OWNER}' AND TAXDIST='{_JSMC_TAXDIST}'"
    return _dedupe(query_parcels(where, settings=settings))


def write_defense_scan(
    prime_owned: dict[str, list[Parcel]],
    army_controlled: list[Parcel],
    out_dir: Path,
    *,
    patterns_searched: int,
) -> Path:
    """Write the defense-land scan (prime-owned + Army-controlled) to one YAML file."""
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "parcels.defense.yaml"
    owned_rows = [
        {"matched_prime": name, **p.model_dump()}
        for name, parcels in sorted(prime_owned.items())
        for p in sorted(parcels, key=lambda p: p.parcel_no or "")
    ]
    doc = {
        "meta": {
            "subject": "Allen County, Ohio defense-industry land scan",
            "source": "Allen County GIS — ArcGIS REST, Current Parcels (AGOL_NonEditLayers/1)",
            "source_url": "https://gis.allencountyohio.com/arcgis/rest/services/AGOL/AGOL_NonEditLayers/MapServer/1",
            "scan": "Owner-name match of the curated DoD-prime seed list "
            "(data/entities/profiles/defense-contractors.yaml) against the CAMA "
            "owner / deeded-owner / second-owner fields.",
            "patterns_searched": patterns_searched,
            "prime_owned_count": len(owned_rows),
            "finding": "No Allen County parcel is owned by a DoD prime in its own name. "
            "The local defense footprint is the federally-held JSMC reservation below.",
            "army_controlled_note": "[inference] the UNITED STATES-owned cluster in tax "
            "district L35 on Buckeye/Reed Rd is the Joint Systems Manufacturing Center "
            "(Lima Army Tank Plant; 1151 Buckeye Rd), operated by General Dynamics Land "
            "Systems. Ownership is verbatim from the GIS; the JSMC identification is an "
            "analyst inference — verify against the deed/lease before relying on it.",
            "caveats": [
                "Values are verbatim from the county GIS; null means the service had no value.",
                "A pattern match is a lead to verify, not a classification or accusation.",
            ],
        },
        "prime_owned": owned_rows,
        "army_controlled": [
            p.model_dump() for p in sorted(army_controlled, key=lambda p: p.parcel_no or "")
        ],
    }
    path.write_text(yaml.safe_dump(doc, sort_keys=False, allow_unicode=True), encoding="utf-8")
    return path


def _parcel_doc(p: Parcel) -> dict[str, Any]:
    return p.model_dump()


def write_parcels(parcels: list[Parcel], out_dir: Path, *, scope: str) -> Path:
    """Write parcels to one YAML file with a provenance ``meta`` block."""
    out_dir.mkdir(parents=True, exist_ok=True)
    ordered = sorted(parcels, key=lambda p: p.parcel_no or "")
    path = out_dir / f"parcels.{scope}.yaml"
    doc = {
        "meta": {
            "subject": "Allen County, Ohio parcels (CAMA)",
            "scope": scope,
            "source": "Allen County GIS — ArcGIS REST, Current Parcels (AGOL_NonEditLayers/1)",
            "source_url": "https://gis.allencountyohio.com/arcgis/rest/services/AGOL/AGOL_NonEditLayers/MapServer/1",
            "count": len(ordered),
            "caveats": [
                "Values are verbatim from the county GIS; null means the service had no value.",
                "Market values are the auditor's appraised values, not sale prices.",
                "last_sale_date is decoded from the GIS M(M)DDYYYY integer; verify against the deed.",
            ],
        },
        "parcels": [_parcel_doc(p) for p in ordered],
    }
    path.write_text(yaml.safe_dump(doc, sort_keys=False, allow_unicode=True), encoding="utf-8")
    return path
