---
name: gis-and-siting-analysis
description: Use for spatial analysis, parcel research, siting/site-selection modeling, easement and corridor mapping, mineral-rights and well-record work, or any task layering public geospatial datasets to identify candidate parcels or infrastructure corridors. Trigger on parcel data, GIS downloads, ArcGIS/PostGIS, ownership chains, easement records, rail or utility ROW, well points, or "score these parcels / find candidate sites." Methodology only; specific endpoints and parcels live in the project enrichment layer.
---

# GIS & Siting Analysis

Methodology for spatial investigation. The output of siting analysis is **not a prediction** — it is a set of parcels the evidence says deserve a closer look. State it that way every time.

## Core framing

A siting model layers public datasets against the known requirements of a workload or infrastructure type and scores parcels for fit. Typical layers:
- zoning / land-use classification
- utility corridors and transmission capacity
- water access
- parcel ownership history (flag corporate and out-of-state ownership)
- proximity to anchor facilities
- recorded easements and severed-estate records
- rail and utility rights-of-way
- well points and subsurface records

The result is a ranked candidate set, not a claim that any parcel *will* be used. The methodology and the output are separate deliverables; a companion methodology piece can walk through the process without contaminating the output piece with speculation.

## Easement and corridor work

- Severed mineral estates and their associated access easements are recorded with the county recorder and **predate** later zoning. Map them from recorded instruments, not from inference.
- An easement corridor follows geometry tied to geology and infrastructure, not to zoning maps. Where a corridor runs is a documentable fact; *why* it runs there, or whether anyone intends to use it, is a question.
- Rail and federally regulated ROW are their own register. Note preemption where relevant (a local land-use instrument generally does not reach a federally regulated corridor) but treat the legal conclusion as a flag for the legal-strategy skill, not a finding you assert in spatial prose.

## Provenance discipline

Every value that enters a document from spatial analysis carries its source. Use a provenanced-value convention: a number or classification travels with its dataset, layer, and date of access. A figure without provenance does not ship.

## Captioning analysis outputs

Map and chart captions state: what the layer shows, the classification scheme and color key, the corridor or area of interest, and the source datasets — in that order, plainly. The caption is part of the evidentiary record, not decoration.

## Standard pipeline

Acquire (county parcel/CAMA, statewide REST endpoints, well records, recorder indexes) → normalize → load to spatial store → score against profile → render with provenanced captions → visual QA. Keep raw acquisitions immutable; do transformations downstream.

## Project enrichment

The project layer supplies the actual datasets, endpoints, parcel identifiers, scoring profiles, and the corridor(s) under study. In *Project BOSC* the provenanced-value convention is the `ProvenancedValue` model in `bosc.hydrology.model` (a value carries `source` / `citation` / `confidence` / `asof`); spatial layers live in `bosc.gis` (`sites`, `corridor`, `raster`, `imagery`, `analysis`) over committed GeoJSON rather than live ArcGIS REST. Bind to those; keep this file endpoint-free. See `docs/investigative-method/ENRICHMENT.md`.
