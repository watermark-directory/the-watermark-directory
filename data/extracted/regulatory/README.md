# Regulatory enforcement & framework extractions

Reviewed reads of the enforcement / capacity instruments governing the Allen County
sanitary system — the binding history the BOSC-1A wastewater routing must be read
against — plus the standing **regulatory-framework** permits the data-center site
itself is governed by. Sources under [`data/documents/regulatory/`](../../documents/regulatory/README.md)
and [`data/documents/sanitary/`](../../documents/sanitary/README.md).

## Files

| File | What |
|---|---|
| `wastewater-enforcement-history.yaml` | The 1996 federal CWA consent decree (US & Ohio v. Allen County, 3:96 CV 7134; effluent violations at American Bath 2PH00007 + Shawnee No.2 2PK00002), the 2005 10-Year Capital Needs Assessment + the 2005-04-21 OEPA SSO-elimination agreement (American No.2 0.80→1.2 MGD; $35M CIP doubling sewer rates), and the Indianbrook PS as-built title sheet (Shawnee collection asset). |
| `ohc000006-construction-stormwater-gp.yaml` | Ohio EPA statewide NPDES Construction Stormwater General Permit **OHC000006** (eff. 2023-04-23) + its Response to Comments — the 1-acre/larger-common-plan applicability threshold, the **NOI ≥21 days before commencement + coverage-not-effective-until-approval-letter** rule, and the SWP3 content requirements. The *standard* the BOSC site's documented "TBD" coverage and 2025-12-08 disturbance are read against; **not** the site's own coverage record (still owed — audit #143). |

## Notes

- The consent decree + CNA were read from the OCR text layer; the Indianbrook
  as-built is image-only drawings (only the title sheet was transcribed). OHC000006
  + its RTC were read from clean PDF text layers.
- These plants are the BOSC-1A receiving facilities (PRR items 8/9) and the same
  ones carrying TP wasteload allocations in the Maumee TMDL — cross-referenced to
  the hydrology references and the OEPA permit extractions.
- `ohc000006-...` is a statewide framework permit (`kind: general_permit`, not
  classified by the typed corpus loader, so parse-only validation applies). It is
  the regulatory backbone for the site permit-sequence reconstruction
  ([`../legal/prr-mandamus/bosc-site-permit-sequence.md`](../legal/prr-mandamus/bosc-site-permit-sequence.md)).
