# OEPA / Wilmington — basin-coverage stub

**Status:** Little Miami basin scaffolding — no registered `SiteProfile`, no confirmed
site-specific load driver as of 2026-06-29.

## What this directory contains

Seven NPDES permit PDFs for facilities in Wilmington, OH (Clinton County):

| Permit | Facility | Receiving water |
|---|---|---|
| `1PD00013` | City of Wilmington WWTP | Lytle Creek |
| `1II00129` | Wilmington Sanitary Landfill | Lytle Creek at RM 6.5 |
| `1IW00240` | Wilmington Water Plant | Unnamed trib of Lytle Creek |
| `1PV00089` | Pine Hills MHP (RLR Investments) | Unnamed trib of Lytle Creek |
| `1PX00010` | Wilmington RV Resort | Unnamed trib of Todd Fork |
| `1PT00125` | Clinton Co. Board of Developmental Disabilities | Unnamed trib of Wilson Creek |
| `1MP00060` | Wilmington Nursery (Kyle Isler) — **LAMP, non-discharging** | N/A |

Receiving waters for the true NPDES discharge permits are **Lytle Creek, Todd Fork,
and Wilson Creek** — all Little Miami basin waters (HUC-8 05090202).

## Why these permits were pulled

The pull was basin-coverage scaffolding for the **Little Miami River** — a third
basin branch for the Watermark Directory network (after Maumee and Great Miami).
Wilmington, with a multi-discharger Lytle Creek reach, is a natural candidate for
the network's first Little Miami watershed point.

**No site-specific data-center or industrial load driver has been confirmed** for
Wilmington or Clinton County. The Wilmington Air Park (former DHL/ABX hub, a large
redevelopment candidate) is the natural external check; verification requires
JobsOhio/Clinton County ED announcements, utility interconnection filings, or new
OEPA air/NPDES sources — none are in the corpus.

## Scope exclusions (see also catalog note)

- `1PV00037` (Hidden Valley MHP, Sidney, Shelby County — Tawawa Creek / **Great
  Miami** basin) and `1PD00008` (Piqua WWTP, Miami County — **Great Miami** River)
  are catalogued under their own sites (`oepa-sidney`, `oepa-troy-piqua`). They are
  not Wilmington dischargers; do not count their design-flow figures toward Lytle
  Creek or any Little Miami assimilative screen.
- `1MP00060` is a LAMP permit (non-discharging); exclude from all surface-water
  load screens.

## Promotion criteria

Promote Wilmington from basin-coverage stub to a registered `SiteProfile` only when:

1. A specific load driver (data-center, major industrial, or significant WWTP
   expansion) is confirmed from external sources.
2. Permit body re-extractions supply design average flow + peak hydraulic capacity
   for `1PD00013` (City WWTP).
3. A 7Q10 low-flow value for Lytle Creek is captured (USGS connector or permit
   fact sheet).
