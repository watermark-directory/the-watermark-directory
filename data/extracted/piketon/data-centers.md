# Piketon / Pike Co., OH — Data-Center Activity Register

Discover-and-pin register for the Piketon watershed point (Scioto River at the DOE Portsmouth
site, "PORTS"). Status **as of 2026-11-02** (#1282). Tags are BOSC evidentiary discipline:
`[verified]` = cited primary/government source, `[reference]` = secondary source or a party's own
self-report (leads only, never a finding), `[inference]` = arithmetic or pattern from cited inputs,
`[open]` = not found in any public source yet. **Nothing here is in the BOSC corpus yet**; this
records the public record and the primary instruments to *pull*. Nothing here is fabricated; every
figure is cited or marked `[open]`.

**The finding is a federal permitting designation, not a permit.** The one government instrument
read is a press release saying the project is covered by FAST-41. No federal, state or local
approval of the campus or its generation is in hand.

## Disambiguation guardrail — run first, always

- **"Portsmouth" here is the DOE plant, not the city.** The Portsmouth Gaseous Diffusion Plant
  ("PORTS") is in **Pike County**, at Piketon. The City of Portsmouth is in **Scioto County**, and
  its project (Tilted Gate LLC / "Project Dazzler", Green Twp) is in
  `data/extracted/portsmouth/data-centers.md`. The FAST-41 dashboard slug
  `portsmouth-data-center` names the DOE site; it does not put the project in Scioto County.
- **Pike County, Ohio (FIPS 39131)** is the scope.

## 1 — SB Energy / "PORTS Technology Campus"

- **FAST-41 coverage:** the Federal Permitting Improvement Steering Council's release of
  2026-06-16, "PORTS Technology Campus latest to gain FAST-41 coverage", names the sponsor as
  "SB Energy" and the lead agency as the "U.S. Army Corps of Engineers", and describes a "10
  gigawatt (GW) data center complex that will include new gas generation and grid upgrades" in
  Pike County, redeveloping a decommissioned DOE site plus nearby private land. `[verified]` for
  what the release says. It lists no milestones.
- **The dashboard entry itself** returned HTTP 403 on 2026-11-02. A posting date of 2026-06-11 and
  a statement that "No DOE permitting support is being requested" come from secondary accounts
  `[reference]`, not from the dashboard.
- **Announcement:** DOE and SB Energy (SoftBank), 2026-03-20: 10 GW of data center plus up to
  10 GW of generation, of which ~9.2 GW gas (the "PORTS Energy Center"); $33.3B for the gas
  portion and $4.2B for transmission; first phase 800 MW by 2028 `[reference]` (WYSO).
- **Acreage:** ~2,700 ac of private land next to the DOE site per WYSO; other accounts give
  1,300 ac `[reference]`. **The two conflict**; neither is from a deed or a filing. `[open]`
- **Tenant:** OpenAI lease talks reported in June 2026 are `[open]`.
- **Generation siting:** no OPSB application for the gas plant was found `[open]`. A plant of
  that size would need an OPSB certificate unless it is federal-site or otherwise exempt; which
  route applies is `[open]`.

### Financial / tax instruments

`[open]`. No CRA, PILOT, enterprise-zone or JEDD instrument was found.

### Water / hydrology hook

- **Max withdrawal / consumption / source:** `[open]`. Nothing is disclosed.
- **Wastewater:** `[open]`. The Village of Piketon's WWTW (NPDES 0PB00031, ~0.45–0.5 MGD design,
  Scioto River — `data/extracted/oepa/piketon/0PB00031.npdes.yaml`) is far too small to be the
  path for a campus of this scale `[inference]`; it is context only.
- `data/sites.yaml` keeps `receiving_water: null`; the Scioto is the likely, unconfirmed receiver.

### Hydrology screen

`[open]` — no disclosed draw.

### Regulatory record (status as of 2026-11-02)

- FAST-41 covered project: `[verified]` (release). Schedule and the permits it lists: `[open]`.
- USACE (lead) permit actions: `[open]`.
- OPSB certificate for generation: `[open]`, none found.
- Ohio EPA air PTI for the gas plant or generators: `[open]`.

## Instruments to pull (priority order)

1. **The FAST-41 dashboard entry and initiation notice** (permitting.performance.gov) — the
   permit list and milestone schedule. Needs a fetch that the site does not refuse.
2. **USACE Huntington District public notices** for the project.
3. **OPSB DIS** — any BGN case for the PORTS Energy Center.
4. **Pike County recorder** — the private-land assembly next to the DOE site.
5. **DOE lease / transfer instrument** for the federal parcel.

## Sources

- <https://www.permitting.gov/newsroom/press-releases/ports-technology-campus-latest-gain-fast-41-coverage>
  — Permitting Council release, 2026-06-16 `[verified]`.
- <https://www.permits.performance.gov/permitting-project/fast-41-covered-projects/portsmouth-data-center>
  — FAST-41 dashboard (403 on 2026-11-02; not read).
- <https://www.wyso.org/2026-03-20/feds-announce-huge-natural-gas-plant-data-center-project-in-southern-ohio>
  — announcement `[reference]`.
