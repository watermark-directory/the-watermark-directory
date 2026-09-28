# Urbana / Champaign County, OH — Data-Center Activity Register

Discover-and-pin register for the Urbana watershed point (readiness epic #1263). Status **as of
2026-09-28**. Tags are BOSC evidentiary discipline: `[verified]` = cited primary instrument or
official public record, `[inference]`, `[open]`, `[reference]` = secondary source, contributing
leads and never findings.

Unlike most registers, this one sits on top of an **already-ingested record**: the Urbana
Technology Hub has a land-assembly register, a facility record, a federal complaint and a water
account in corpus (all as of ~2026-07-10). This register therefore **pins** that record by
pointer rather than restating it, and adds what the 2026-09-28 sweep found **after** the corpus
freeze: the county-court appeal's schedule, the November ballot measures, the township ban, and
the county-wide negative. Nothing below the "Since the corpus freeze" heading is in the corpus
yet. Every figure is cited; none is fabricated. Do not bridge the Lima/Allen County graph onto
Champaign County — there is no evidentiary link.

## Disambiguation guardrail (critical)

- **Champaign County, ILLINOIS is the live trap.** A sweep for `"data center" "Champaign County"`
  returns CU-CitizenAccess coverage (2026-04, 2026-07) of an Illinois county moratorium, a
  ~300-ac proposal "near southwest Champaign" and a 313-ac proposal in **Mahomet** — all Champaign
  County, **IL** (Champaign–Urbana, IL). `[verified]` by place names. **No Illinois project enters
  this register**, and "Urbana" in an Illinois story is Urbana, IL, not this site.
- **Urbana city ≠ Urbana Township.** The campus is on land **annexed into the City** (Ord. 4619-25);
  the County has stated the parcels are "wholly within the corporation limits of the City of
  Urbana" `[reference]`. The township's own zoning action (below) is a separate jurisdiction and does
  not govern the campus.
- **Conflation guard (carried from [`highland55-findings.md`](highland55-findings.md)):** the
  100 MW → 1.3 GW AES Ohio ramp is **Adams County (Stuart)**, and ~500 MW is Thor's **Van Wert**
  campus. Neither figure is Urbana's.
- **The same developer is at two network sites.** Thor Equities also develops at Van Wert
  ([`../van-wert/data-centers.md`](../van-wert/data-centers.md)). That is a shared *party*, not a
  shared record. Neither site's figures cross.

## 1 — Thor Equities / "Urbana Technology Hub" (Highland55)

- **Developer:** Thor Equities LLC (New York), acting through single-purpose entities Urbana Owner I
  LLC, Urbana Owner II LLC, Highland55 Investments LLC and contract purchaser Urbana Owner LLC.
  `[verified]`: auditor CAMA + federal complaint Doc #1 ¶¶10–13.
- **Location:** SR-55 & US-68, south of Rittal, in the City of Urbana (annexed), Champaign County,
  OH. The parcel IDs carry the K48 prefix. `[verified]`: [`land-assembly.yaml`](land-assembly.yaml),
  `data/reference/urbana/parcel-assemblage.geojson`.
- **Land:** **230.35 ac** owned across 4 parcels / 3 SPEs; deeds OR601/4948, OR603/1927 and
  OR606/3352. `[verified]` (CAMA). A further contract-purchase by Urbana Owner LLC
  (K48-25-11-01-36-001-00 plus part of -37-001-00) is not yet conveyed; its acreage is `[open]`.
- **End-use:** data-center campus. `[reference]`: public disclosure at the Feb-2026 City meeting
  (Urbana Daily Citizen 2026-02-18) and Thor's own pleading. A facility-naming primary instrument
  (air PTI, building permit, interconnection) has **not surfaced** (#1353). The end-use stays
  `[reference]`.
- **Scale as disclosed:** ~$1B, 460,000 sq ft, single-story, 40-ft profile; 80 permanent and 1,000
  construction jobs; ≥$3M/yr to the City and ≥$2.8M/yr to Urbana schools. `[reference]`: Thor's own
  figures, repeated in its July 2026 direct-mail and ad campaign (Springfield News-Sun,
  2026-07-30). These are a developer's claims, not findings.
- **Power:** serving utility AES Ohio (Dayton Power & Light), PJM **DAY** zone. `[verified]` The
  **MW load is not disclosed.** The profile carries only an `[inference]` floor-area screening
  bracket, and no PJM or TEAC large-load entry was found (#1353). Full record:
  [`datacenter-facility.md`](datacenter-facility.md) §4 and
  [`facility-power-instrument-search.md`](facility-power-instrument-search.md).
- **Status: NOT BUILT, and not permitted.** The site plan was rejected as "incomplete"
  (2026-02-20). Res. 2727-26 imposed a 12-month moratorium (2026-03-03). Ord. 4635-26 removed
  data centers from M-1, passing **6-0 on 2026-06-16** `[verified]` (minutes). The 401 WQC's
  06/01/2026 construction start was a *scheduled* date, not an event.

### Financial / tax instruments

- **No CRA agreement and no PILOT.** `[verified]` (#1354). Ord. 4631-25 designates a CRA *area*
  only, passing 5-2. It names no project and excludes Thor's first two parcels. The City's one
  contract with the developer is the **Pre-Annexation Agreement**, Ord. 4612-24 (Urbana0624C, LLC),
  passed 5-0 on 2024-12-17. `[verified]` See [`incentive-instruments.md`](incentive-instruments.md).
- **County land option.** In June 2024 the County Commissioners unanimously granted the Champaign
  Economic Partnership a multi-year option to sell county land on S. US-68 to the developer. They
  state a data center was never represented to them. `[reference]`: Commissioners' statement via
  Peak of Ohio (2026-02-13). A September-2024 purchase agreement for **94.11 ac** at 2500 and 2200
  S. US-68 is reported `[reference]` (Springfield News-Sun 2026-07-30), and a commissioner reports the
  final county parcel is "locked under a contract" `[reference]`. Whether those 94.11 ac are the
  Urbana Owner LLC contract parcels is `[inference]`/`[open]`. The purchase agreement itself is the
  pull.

### Water / hydrology hook

- **Max withdrawal:** not disclosed. `[open]`
- **Projected cooling-water consumption:** not disclosed as a number. The disclosure is a
  *comparison*: "closed-loop," "comparable to a standard office building." `[reference]`
- **Water source:** City of Urbana municipal supply. The City is obliged to provide water and sewer
  under Ord. 4612-24, and Ord. 4613-24 is the statement of services. `[verified]`
- **Wastewater:** City sanitary sewer → Urbana WPCF (OH0027880 / 1PD00011) → Mad River. `[verified]`
  for the plant and permit. Any blowdown would sit in a City **industrial-user / pretreatment
  permit**, which ECHO never carries. `[open]`
- **Stormwater:** construction stormwater general-permit coverage was scheduled for 2026-03-31 in
  the §401 WQC. No NOI has been found. `[open]`

### Hydrology screen

- **Receiving water:** Mad River at the Urbana WPCF outfall. Regulatory **7Q10 = 35 cfs** (OEPA
  1PD00011 fact sheet). `[verified]`
- **Abstraction vs. 7Q10:** not computable, because no draw is disclosed. `[open]` The only
  measurable denominator is the supplier's: the City withdrew **644.99 MG in 2024 (1.76 MGD)**.
  `[verified]` An evaporative reading of the campus at its screening bracket would be 28–93% of
  that total, while the "office building" reading is below the screen's floor. `[inference]`
  Route-blind — see [`cooling-water-account.md`](cooling-water-account.md) (B4, #1684).
- **Effluent path:** City WPCF, design 4.5 MGD. `[verified]` The campus contribution is `[open]`.

### Regulatory record (status as of 2026-09-28)

| Instrument | Status | Tag |
|---|---|---|
| USACE JDs + OEPA §401 WQC ("Urbana Brand I": substation, "industrial warehouse") | in corpus (`permits/highland55/`) | `[verified]` |
| OEPA air PTI (emergency gensets) | none found in ECHO ICIS-AIR at the site (#1353) | `[verified]` negative |
| NPDES construction stormwater NOI | not found | `[open]` |
| PJM / AES Ohio large-load or interconnection | none found for Champaign County (#1353) | `[verified]` negative |
| Ohio SOS: Thor SPEs + registered agents | not pulled (403 from this environment) | `[open]` |
| Ohio water-withdrawal registry | campus absent (a searched absence); City plants present | `[verified]` |

## 2 — Since the corpus freeze (2026-07-10 → 2026-09-28)

None of this is in the corpus. All of it is `[reference]` until the named instrument is pulled.

### Litigation

- **Federal:** *Thor Equities, LLC v. City of Urbana*, **3:26-cv-00196**, S.D. Ohio (Judge Michael
  J. Newman), filed 2026-06-19. `[verified]` (Doc #1 in corpus; the CourtListener docket index
  lists the same caption and number.) A docket snippet surfaced in search reads "motions directed
  to pleadings due by 9/5/2026" `[reference]`. Whether the City moved to dismiss or answered, and
  whether any PI motion was filed, is **`[open]`**. CourtListener refused automated access, so the
  docket needs to be pulled directly.
- **Champaign County Common Pleas (R.C. 2506 appeal of the BZA denial):** the court found the
  City's filed record **incomplete** and ordered the full transcript of the 2026-04-13 BZA hearing
  added, due **2026-08-03**. Briefing then runs: Thor's brief due **2026-09-02**, the City's response
  **2026-10-02**, and Thor's reply later in October. The project is on hold meanwhile. `[reference]`:
  Peak of Ohio 2026-07-20 and WDTN. The **case number is still `[open]`**. WDTN headlined this
  "County judge rules against Urbana," but it is a **record-completeness order, not a merits
  ruling**. Do not report it as a win on the merits.

### Ballot measures (Nov 3, 2026)

- **Charter amendment — data-center ban.** It adds Charter **Art. VIII § 8.07**, prohibiting data
  centers, with an exemption for a single organization's facility under **7.5 MW** aggregate
  monthly demand or peak load. The citizen petition was started 2026-07-07 by Nicole Nawman
  (Conserve Ohio) and filed 2026-07-14 with 400+ signatures against 169 required. The Champaign
  County BOE verified sufficiency. Council sent it to the ballot by **emergency Ord. 4640-26**
  (2026-08-04). The Ohio SOS had to rule on a typographical error before inclusion. `[reference]`:
  Peak of Ohio 2026-08-04, Urbana Daily Citizen 2026-08-31, WYSO 2026-07-15. The threshold is
  **7.5 MW**, not the 25 MW used elsewhere — do not normalize it. **A measure is not an outcome**,
  and it does not move `readiness`.
- **Recall — Mayor Bill Bean.** The petition was started 2026-07-07 by James Cropper; 326
  signatures were certified against 253 required. The grounds allege a lack of transparency about
  the project. If the recall carries, the replacement contest is Eugene E. Fields Jr. vs. Nicole L.
  Nawman. `[reference]`: WDTN, Urbana Daily Citizen 2026-07-20 and 2026-08-07.
- **Interaction worth tracking:** the charter ban would bind prospectively, while Thor's
  vested-rights count (Count 7) argues the 2026-02-13 application froze the pre-moratorium rules.
  How a charter prohibition meets a vested-rights claim is a question for the courts. `[open]`

### Urbana Township zoning ban (separate jurisdiction)

The Urbana Township Zoning Commission proposes to **add a "Data Center" definition and eliminate new
data centers and energy-storage systems as permitted or conditional uses**. The steps so far are a
public meeting on 2026-07-29 and a Commission hearing on 2026-08-18; on 2026-09-09 the Commission
referred the amendment to LUC Regional Planning. The **Trustees' hearing is 2026-10-05**.
`[verified]`: official township public notices (urbanatownship.com/public-notices). It does not
reach the annexed campus. It closes the unincorporated land around it. LUC Regional Planning has
reviewed **28** near-identical township bans across Logan, Union and Champaign counties from April
to September. `[reference]`: Ohio Capital Journal 2026-09-18.

## 3 — Pending confirmation

- **Honda "own Ohio data center," "Marysville / Clark / Champaign area."** A demand-fit candidate
  in `cloud-consumer-candidates.yaml`, **downgraded 2026-06-28** (`corridor_context: true`). No
  instrument pins it to Champaign County, and this sweep found none. `[open]`
- **Mad River Township (Champaign Co.) data-center zoning.** A search snippet indicates its Zoning
  Commission is considering data-center regulation. The township site failed TLS from this
  environment. No project is named. `[open]`: a lead only.

## 4 — No other activity found (county-wide)

- **RSEI (v2.3.12), Champaign County 39021:** 12 TRI facilities (Rittal, Honeywell Aerospace,
  Siemens, KTH, and others). **None in NAICS 518210.** `[verified]`:
  `data/reference/rsei/urbana/inventory.yaml`.
- **ECHO CWA, Champaign County:** 21 facilities, none at SR-55/US-68 and none of data-center type.
  `[verified]` (B4 pull, #1684; query with `p_co=Champaign&p_st=OH`, since a FIPS returns 0 rows).
- **Ohio water-withdrawal registry, Champaign:** 31 registrations, no data-center registrant.
  `[verified]` (`data/reference/ohio-water-withdrawal/champaign.yaml`).
- **Web sweep (2026-09-28):** no second Champaign County, OH data-center project in council, county
  or trade-press coverage. Mechanicsburg, St. Paris, North Lewisburg and Mad River Twp were searched,
  with only the zoning-regulation lead above. `[verified]` negative for the queries run, not
  proof of absence. The stopohiodatacenters.org county index **does not list Champaign County at
  all**, including the Thor project. That is an omission in a watchdog index, not a negative.
  `[reference]`

## Instruments to pull (priority order)

1. **S.D. Ohio 3:26-cv-00196 docket** (PACER): the City's answer or motion to dismiss, any PI
   motion and ruling, the scheduling order, and **Exhibits 1–9 to Doc #1**. The exhibits take the
   ordinance record from `[reference]` to `[verified]` (#1359).
2. **Champaign County Common Pleas R.C. 2506 appeal:** the case number, the record-completeness
   order, the **BZA transcript of 2026-04-13**, and the Sept–Oct briefs.
3. **City of Urbana: Ord. 4640-26** and the certified charter-amendment text (§ 8.07). Also the
   **Champaign County BOE** certifications for the charter amendment and the Bean recall
   (R.C. 149.43 to the BOE, the route van-wert already uses).
4. **City of Urbana utility records:** the capacity / supply-adequacy analysis for the campus, and
   any industrial-user or pretreatment permit application. These are the only instruments that would
   put a number on the "office building" claim (lead `URB-WATER-METER`).
5. **County ↔ Highland purchase agreement** (Sept 2024, 94.11 ac, via CEP), plus the Commissioners'
   June-2024 option resolution: this pins or rules out the Urbana Owner LLC contract parcels.
6. **Ohio SOS:** Thor SPE registrations and registered agents, including Urbana0624C, LLC.
7. **OEPA:** construction-stormwater NOI and any air PTI for the site. These are expected only if
   the litigation reopens the entitlement. Keep as a standing watch, not an active pull.
8. **Urbana Township:** the adopted amendment text after the 2026-10-05 Trustees' hearing.

## Sources

- Corpus: [`highland55-findings.md`](highland55-findings.md), [`land-assembly.yaml`](land-assembly.yaml),
  [`litigation-thor-v-urbana.md`](litigation-thor-v-urbana.md),
  [`incentive-instruments.md`](incentive-instruments.md),
  [`datacenter-facility.md`](datacenter-facility.md),
  [`facility-power-instrument-search.md`](facility-power-instrument-search.md),
  [`cooling-water-account.md`](cooling-water-account.md), `../oepa/urbana/1PD00011.npdes.yaml`.
- CourtListener docket index, 3:26-cv-00196 —
  <https://www.courtlistener.com/docket/73509496/thor-equities-llc-v-city-of-urbana-ohio/>
- Peak of Ohio, "Court grants Thor Equities' request in Urbana data center case" (2026-07-20) —
  <https://www.peakofohio.com/local-news/court-grants-thor-equities-request-in-urbana-data-center-case/>
- WDTN, "County judge rules against Urbana in data center lawsuit" —
  <https://www.wdtn.com/news/miami-valley-data-centers/county-judge-rules-against-urbana-in-data-center-lawsuit/>
- Peak of Ohio, "Urbana Council sends proposed data center ban to November ballot" (2026-08-04) —
  <https://www.peakofohio.com/featured-news/urbana-council-sends-proposed-data-center-ban-to-november-ballot/>
- Urbana Daily Citizen, "Data center ban will be on Urbana ballot" (2026-08-31) —
  <https://www.urbanacitizen.com/2026/08/31/data-center-ban-will-be-on-urbana-ballot/>
- WYSO, "Two Urbana residents start petitions…" (2026-07-15) —
  <https://www.wyso.org/news/2026-07-15/two-urbana-residents-start-petitions-in-response-to-data-center-dispute>
- WDTN, "Urbana mayor recall, data center ban headed to Nov. ballot" —
  <https://www.wdtn.com/news/local-news/urbana-mayor-recall-data-center-ban-headed-to-nov-ballot/>
- Urbana Daily Citizen, "Mayoral recall, charter amendment on Nov. ballot" (2026-07-20) and
  "Candidates file to replace Mayor Bean" (2026-08-07) — <https://www.urbanacitizen.com/>
- Springfield News-Sun, "Urbana data center saga continues…" (2026-07-30) —
  <https://www.springfieldnewssun.com/local/urbana-data-center-saga-continues-with-charter-amendment-mayor-recall-developer-campaign/article_3615a5d3-c607-524d-8b52-4f2a12435996.html>
- Peak of Ohio, Champaign County Commissioners' statement (2026-02-13) —
  <https://www.peakofohio.com/local-news/champaign-county-commissioners-release-statement-for-clarity-on-proposed-data-center-project/>
- Urbana Township public notices — <https://urbanatownship.com/public-notices>
- Ohio Capital Journal, "Ohio now has over 125 active moratoriums…" (2026-09-18) —
  <https://ohiocapitaljournal.com/2026/09/18/ohio-now-has-over-125-active-moratoriums-on-data-centers-see-where-they-are/>
- CU-CitizenAccess (Champaign County, **IL**; disambiguation only) —
  <https://cu-citizenaccess.org/2026/07/while-officials-debate-data-center-regulations-residents-want-to-know-where-theyll-be-built/>
