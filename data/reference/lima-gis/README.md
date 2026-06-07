# City of Lima, Ohio GIS — zoning

Zoning attributes pulled from the **City of Lima GIS** public ArcGIS REST server.
Every value here was returned by the service — nothing is fabricated or estimated.
Regenerate with `bosc zoning --districts` (or query ad hoc with
`bosc zoning --parcel <no>` / `--cited`).

## Source

Layer 6 **"Current Lima Zoning"** of the `CitywideMaps/Lima_Zoning` map service
(the web adaptor is `/server`, not `/arcgis`):

```
https://colgis.cityhall.lima.oh.us/server/rest/services/CitywideMaps/Lima_Zoning/MapServer/6
```

Anonymous (no token), serves `f=json`, `maxRecordCount` 10,000. Each zoning polygon
carries a `ZONING` district label **and** a `PARCEL_NO`, so zoning joins to the
Allen County CAMA parcel layer by id — no spatial query needed.

## Files

`zoning-districts.yaml` — the district catalog: each `ZONING` code and the number
of polygons carrying it (10 districts, 2,670 polygons), with a provenance `meta`
block.

## Gaps / caveats

- **City limits only.** This layer covers the City of Lima. Parcels in
  unincorporated Allen County — including the American Township corridor at the
  centre of the corpus — are **not** in it; a lookup there returns nothing, which
  means "outside the city," not "unzoned." (None of the 45 corpus-cited corridor
  parcels fall inside the city limits.)
- **`polygon_count` ≠ parcel count.** A parcel may carry more than one zoning
  polygon; the catalog counts polygons.
- District labels are the city's own verbatim strings (e.g.
  `CLASS I RESIDENTIAL SINGLE FAMILY`, `SECOND INDUSTRIAL HEAVY`); the service
  ships no separate code→description lookup.
