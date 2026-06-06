# Allen County, Ohio GIS — parcels (CAMA)

Parcel / real-estate attributes pulled from the **Allen County GIS** public ArcGIS
REST server. Every value here was returned by the service — nothing is fabricated
or estimated. Regenerate with `bosc parcels --cited` (or query ad hoc with
`bosc parcels --parcel <no>` / `--owner <name>`).

## Source

Layer **"Current Parcels"** (the auditor's CAMA data joined to parcel geometry):

```
https://gis.allencountyohio.com/arcgis/rest/services/AGOL/AGOL_NonEditLayers/MapServer/1
```

Anonymous (no token), paginates at 1,000 features (`exceededTransferLimit` →
loop `resultOffset`), serves `f=json`. There are ~105,362 parcels countywide; this
folder holds only the subset relevant to the corpus.

## Files

`parcels.cited.yaml` — every parcel id cited in the corpus's deeds (e.g.
`36-0100-03-002.000`), resolved against the GIS. Deed ids are normalized to the
service's dashless `PARCEL_NO` (`36010003002000`) for lookup. Each record carries
owner / deeded owner, situs + mailing address, land-use code, acreage, market
land/improvement/total and CAUV values, tax district, school/neighborhood codes,
and last sale (date + amount). `null` = the service returned no value.

## Gaps / caveats

- **Market values are the auditor's appraised values, not sale prices.** The sale
  price is `last_sale_amount` (often `0` for non-arms-length transfers);
  `valid_sale` is the service's validity flag.
- **`last_sale_date`** is decoded from the GIS `DATE` integer (`M(M)DDYYYY`);
  verify against the recorded deed before relying on it.
- **`land_use_code`** is the numeric Ohio land-use code (e.g. 500-series =
  residential); the service ships no code→label lookup.
- **Zoning is not here.** The county server has no countywide zoning layer; Lima
  zoning lives on a separate City of Lima ArcGIS server and is City-limits only.
- Some parcels return multiple feature rows (splits/condos); the writer keeps the
  first row per distinct `PARCEL_NO`.
