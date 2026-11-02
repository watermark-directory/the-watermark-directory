# Coshocton / Coshocton Co., OH — Data-Center Activity Register

Discover-and-pin register for the Coshocton watershed point (Tuscarawas + Walhonding → Muskingum).
Status **as of 2026-11-02** (#1281). Tags are BOSC evidentiary discipline: `[verified]` = cited
primary/government source, `[reference]` = secondary source or a party's own self-report (leads
only, never a finding), `[inference]` = arithmetic or pattern from cited inputs, `[open]` = not
found in any public source yet. **Nothing here is in the BOSC corpus yet**; this records the public
record and the primary instruments to *pull*. Nothing here is fabricated; every figure is cited or
marked `[open]`.

**The finding is an announced campus with no instrument found.** The only source is the
developer's own material.

## Disambiguation guardrail — run first, always

- **Coshocton County, Ohio (FIPS 39031).** Conesville is in Coshocton County, south of the City.
- **"CMH" is the developer's market code (Columbus), not a location.** Aligned's "CMH-02" is at
  Conesville, not in Franklin County; it does not enter the Columbus register.

## 1 — Aligned Data Centers "CMH-02" (Conesville Industrial Park)

- About 197 ac at the Conesville Industrial Park, the former AEP Conesville plant site; announced
  July 2025; a community FAQ posted June 2026 `[reference]` — the developer's own document.
- **No new instrument found** this pass: no deed, CRA, PILOT, air PTI or NPDES coverage `[open]`.
- MW and investment: `[open]` from any primary source.
- **Context, `[verified]`:** the City of Coshocton WWTP permit (NPDES 0PD00004) lists the
  Conesville Power Plant among the industrial users that **formerly** contributed and have
  ceased (`data/extracted/oepa/coshocton/0PD00004.npdes.yaml`). This confirms the plant is closed;
  it says nothing about the campus.

### Water / hydrology hook

`[open]` — nothing disclosed. The former plant's water infrastructure on the Muskingum is the
obvious candidate supply; that it will be reused is an `[inference]` with no source.

### Hydrology screen

`[open]`.

## Instruments to pull (priority order)

1. **Coshocton County recorder** — the Conesville Industrial Park transfer(s) to an Aligned
   entity.
2. **County / port authority incentive instruments** (CRA, enterprise zone, PILOT).
3. **Ohio EPA air PTI** search for Conesville.
4. **Ohio SOS** — the Aligned operating entity registered for the site.

## Sources

- <https://aligneddc.com/wp-content/uploads/2026/06/Aligned_Community-FAQs_Coshocton-County.pdf>
  — developer FAQ `[reference]`.
- `data/extracted/oepa/coshocton/0PD00004.npdes.yaml` — City of Coshocton WWTP permit
  `[verified]`.
