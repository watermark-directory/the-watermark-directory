# Wapakoneta / Auglaize Co., OH — Data-Center Activity Register

Discover-and-pin register for the Wapakoneta watershed point (upper Auglaize River → **Maumee** at
Defiance → Lake Erie). Status **as of 2026-10-28** (#2184). Tags are BOSC evidentiary discipline:
`[verified]` = cited primary/government source, `[reference]` = secondary source or a party's own
self-report (leads only, never a finding), `[inference]` = arithmetic or pattern from cited inputs,
`[open]` = not found in any public source yet. This records the public record as of the date above
and the primary instruments to *pull*. The sources filed so far are under
`data/documents/wapakoneta/`; the rest are cited by URL. Nothing here is fabricated; every figure
is cited or marked `[open]`.

**The finding is a proposal with no instrument behind it.** One developer has asked about one site.
By the City's own account, nothing is negotiated, approved, committed, or filed. Wapakoneta's
`SiteProfile` therefore carries `facilities=()`, and the `facility` readiness domain stays
**locked**. The one instrument that exists is the City's own: in 2024 it legislated conditional-use
review for this class of use **before** any developer asked.

## Disambiguation guardrail — run first, always

- **"CTS" is not QTS.** QTS (Quality Technology Services) is the Van Wert Mega Site operator
  (`data/extracted/van-wert/`). The 2026-10-12 sweep found no web footprint for **Colocation
  Technology Services LLC**. On 2026-10-18 one turned up: **colotech.co**, a site whose footer reads
  "© 2026 Colocation Technology Services LLC" and whose privacy notice calls the company "CTS"
  (captured under `data/documents/wapakoneta/reference/`). Everything on it is the company's
  self-description `[reference]`: a "300+ MWs Development Pipeline", "6 DATA CAMPUSES Delivered",
  "up to 600kW per rack", "zero-water-waste" economizer designs, and a map of "five project states"
  that names only South Carolina. It names no Ohio project, no address and no officer, so that it
  is the company that approached WAEDC rests on the name alone `[inference]`. The Ohio SOS
  business search still answers a scripted client with a JavaScript "security check" (2026-10-18),
  which this repo does not get around; the record needs a browser. **Never resolve "CTS" by
  acronym**: the entity's formation, agent and principals stay `[open]` until the SOS record is
  pulled.
- **Auglaize County, Ohio (FIPS 39011)** is the scope. St. Marys is in the same county, and its
  moratorium (§3) is context, not an entry.
- **The Auglaize River is shared with Lima.** Wapakoneta sits on the upper Auglaize, upstream of the
  Ottawa River confluence. Lima's reservoirs refill from the Auglaize, gauged downstream at Fort
  Jennings (`SiteProfile.supply_gage_primary`, Lima). A shared river is a **hydrologic** relation,
  not an evidentiary link between the two sites' land or actors. Do not bridge the Lima/Allen
  County land-assembly graph onto Auglaize.

## 1 — Colocation Technology Services (CTS) / West Central Ohio Industrial Center

### 1.1 — What the City said

Source: City of Wapakoneta, "City Administration" statement, Facebook,
<https://www.facebook.com/cityofwapakoneta/posts/pfbid0uaLu5N75YRUZjhXZ1rGwkqYX7FL1fTTaB69UKmz2kZ8JJR1v3PoqZ4aNnuPaiyCCl>.
**The post date is `[open]`.** Facebook serves no dated page to a script, and the Wayback Machine has
no snapshot. The text in hand is a paste supplied 2026-10-12 (§Appendix), not a capture. The post is
the City's official channel, so *that the City said these things* is `[verified]` once the post is
captured. Everything the City relays from CTS remains CTS's self-report, so it is `[reference]`.

- **Status, as the City states it.** "The City has not entered into negotiations with the developer,
  Colocation Technology Services (CTS), approved any part of the project, or made any commitments to
  the development. CTS has also not submitted requests for annexation, conditional use approval, or
  other project-related approvals." The City has been aware of the project "for a few months."
- **The intermediary is WAEDC.** The Wapakoneta Area Economic Development Council is "a separate
  entity from the city." CTS approached WAEDC "about the possibility of developing a smaller sized
  data center in the industrial park."
- **Power: 50 MW `[reference]`.**
  - The City "requested an initial feasibility study with American Electric Power (AEP)." Its
    results "indicated that the facility could be served without improvements to AEP's existing
    infrastructure."
  - The facility would take "a new connection directly to an AEP electric line rather than supplying
    power through the City's existing electric distribution system."
  - CTS "would also be considered a Delivery Service Customer", buying "through separate contracts
    with American Municipal Power (AMP)". That class applies to "demands exceeding 10 megawatts."
  - The feasibility study itself is **not in hand** `[open]`.
- **Water: closed-loop cooling `[reference]`.** CTS indicated "approximately 5,000 to 10,000 gallons
  per day." Water from the cooling system "would not be discharged into the City's sewer system but
  would instead be periodically removed and properly disposed of off-site." Wastewater would
  "primarily come from normal restroom use."
- **Noise `[reference]`.** CTS estimates "approximately 60 decibels at their property edge."
- **Next step.** "In the coming weeks, CTS will be holding informational meetings, open to the
  public, prior to submitting any development requests to the City." Dates and venues are `[open]`.

### 1.2 — What the press reported, and where it differs

Source: Bob Neelski, "A Data Center In Wapakoneta?", *Wapakoneta Daily News*, 2026-10-08
<https://www.wapakdailynews.com/news/a-data-center-in-wapakoneta/article_30fa606e-99e6-4ea4-83e1-f45c0beaf5d8.html>
`[reference]`. The story reports WAEDC Executive Director **Josh Bloomfield**'s briefing to City
Council. That briefing was the **2026-10-05** Council meeting `[verified]` (§1.2a).

- **Site.** "a 30 acre 50 megawatt data center at the **West Central Ohio Industrial Center**." The
  City's post says only "the industrial park"; the press supplies the name.
  - WCOIC is at I-75 × US-33, inside city limits, and SiteOhio-authenticated per WAEDC's own site
    (<https://whywapakoneta.com/west-central-ohio-industrial-center>).
  - **Which parcel(s) the "30 acre" site is remains `[open]`.** The platted park and its zoning, as
    the City's published GIS layer shows them, are in §2.
- **Expansion.** "with the potential to eventually expand to **70 acres and 200 megawatts**." **This
  is not in the City's post**, which describes only the 50 MW first phase as "a smaller sized data
  center." The two are not in conflict. The 200 MW figure is an unfiled, secondhand ceiling, and it
  is the one that would matter to a grid or water screen.
- **Timeline.** Initial contact came "about 9 months ago" (≈ January 2026, `[inference]` from the
  article date). A "due diligence and feasibility period over the next 6 weeks" follows. If the
  project is viable, CTS "would seek a conditional use approval."
- **Economics `[reference]`.**
  - Jobs: 25 full-time jobs, about 25 vendors, and 200+ construction jobs over 12–18 months.
  - Tax: "$4+ million" a year in kWh tax and local taxes.
  - **No abatements requested.**
- **Instruments.** "No development agreements have been executed, no guarantees … no non-disclosure
  agreement."

### 1.2a — What the Council minutes record

Source: City Council minutes, 2026-10-05, p. 1 (`data/documents/wapakoneta/governance/10-5-2026-Minutes.pdf`;
image-only, read by OCR and checked against the rendered page). *That Bloomfield said these things to
Council* is `[verified]`. What he relays about the project is the developer's account, so it is
`[reference]`.

- **The announcement.** Bloomfield addressed Council "to announce the potential for a 30-acre, 50
  megawatt data center project within the West Central Ohio Industrial Center." **The minutes do not
  name the company.** That this is CTS rests on the City's post and the WDN story, which do.
- **Stage.** "due diligence and feasibility stage, with examination of the viability of electrical
  and utility needs for the site." Before a formal request, "the company involved will conduct a
  press release to the public, as well as provide a project-specific web page and webinars." He added
  that "the informational website should go live sometime this week." Whether colotech.co (see the
  guardrail) is that website is `[inference]`: it carries no Wapakoneta content.
- **Cooling.** "a closed-loop, oil-cooled system, which will limit its water and wastewater needs."
  **"Oil-cooled" is not in the City's post or the WDN story.** It reads as dielectric (immersion)
  cooling `[inference]`, which would make a 5,000–10,000 GPD demand plausible and the hauled
  "cooling water" of the City's post a different stream from the coolant. Neither is established.
- **No asks.** "The company has not requested tax abatements, extension of additional utilities to the
  site or the building of additional roadways."
- **Jobs and investment.** "25 permanent full-time positions plus 25 jobs from outside employers and
  200 construction workers", and "an estimated 500 million dollar investment". The **$500 million**
  figure is not in the WDN story, which gives "$4+ million" a year in taxes instead.
- **Expansion.** Asked by Mrs. Muhlenkamp, Bloomfield said "the company would ideally like to expand
  to a total of 70-acres and 200 megawatts if possible." Asked by Mr. Greve how the City can limit
  it, he "encouraged Council to codify these details if the project moves forward, noting that the
  conditional use parameters within the zoning code does provide additional protections."
- **Timeline.** "6 weeks of community engagement followed by a conditional use request to City
  Council, then potential to break ground in Spring of 2027 with a 12 month construction timeline."
  - **The forum is misstated.** Under §1282.04 and §1252.07 the conditional use is decided by the
    **Planning Commission**, not City Council (§2) `[verified]` as to the code. Whether Council has any
    role (an appeal, a development agreement, the "codify" route) is `[inference]`.
  - WDN gives construction as 12–18 months; the minutes say 12.
- **Council's response.** Ms. Behr, Mr. Dunlap and Mr. Greve "recommended that the developers conduct
  town hall style meetings for public input." No motion was made.

**Two earlier executive sessions** invited Bloomfield. Neither names its subject, so **whether either
concerned CTS is `[open]`**:

- **2026-06-15** (p. 4): 9:10–9:56 pm, for pending or imminent litigation **and** "confidential
  information related to the marketing plans, specific business strategy, production techniques, trade
  secrets, or personal financial statements of an applicant for economic development assistance";
  6–0 `[verified]`. The WDN story says CTS asked for no abatement, so "an applicant for economic
  development assistance" need not be CTS. Another economic-development item was live in
  the same period: a development agreement with Elfie Properties LLC (Ord. 2026-50R, adopted on third
  reading 2026-10-05).
- **2026-09-08** (p. 4): 8:27–9:23 pm, "to discuss confidential information regarding economic
  development", inviting Bloomfield and City Administration; 7–0 `[verified]`.

### 1.3 — The capacity gap

- JobsOhio's site listing gives WCOIC "excess electric capacity of **5 MW** with a dual feed from
  dual substations." It also lists water at 1.5 MGD and sewer at 1.2 MGD
  (<https://jobsohio.com/available-sites/west-central-ohio-industrial-center>) `[reference]`.
- The 50 MW ask is ten times that, and the 200 MW ceiling is forty times. **`[inference]`** This is
  consistent with the City's account that the load bypasses the park's city-fed distribution
  entirely, through a direct AEP-line tap.
- The listing's vintage is `[open]`. So is who owns the line that crosses or abuts WCOIC.

### 1.4 — Water / hydrology hook

- **Max withdrawal:** not disclosed `[open]`.
- **Stated water demand:** 5,000–10,000 GPD, CTS's self-report via the City `[reference]`. The
  City's words are "requiring approximately 5,000 to 10,000 gallons per day". That figure is a
  demand on the City system, not a consumption figure.
  - At the 4× scale-up to 200 MW `[inference]`, demand would be ~20,000–40,000 GPD if it scaled
    linearly with load. That linear scaling is not a claim anyone has made.
  - It is an order of magnitude a closed-loop design makes plausible. It is not demonstrated.
- **Net consumption:** `[open]`. Part of the demand leaves as hauled cooling water rather than as
  evaporation. The split between the two is undisclosed, and so is the hauled volume and where it
  goes. Until both are known, no consumptive figure can be derived from the demand figure.
- **Water source:** the City system. That system is **groundwater**: "ancient Teays River Valley
  Aquifer … nine deep wells, located in two well fields." Ohio EPA rates the source "high
  susceptibility." Source: City of Wapakoneta 2025 Consumer Confidence Report
  (<https://files-backend.assets.thrillshare.com/documents/asset/uploaded_file/5500/Cow/9b742bf8-0c2b-4605-9be3-438522796072/Revised-FINAL-2025-CCR-Text---For-2026-Year.pdf>)
  `[verified]`.
  - There is no river intake, so a 7Q10 abstraction ratio does not apply to *supply*.
  - The City says its plant "currently treats more than a million gallons daily" `[reference]`.
- **Wastewater:** restroom sanitary to the City WRF `[reference]`. Cooling blowdown is **hauled
  off-site**, destination `[open]`.
  - That disposal path is the instrument to find. A hauled waste stream lands at *someone's* permit,
    whether a POTW receiving trucked waste or an industrial treater.
- **Stormwater:** `[open]`. No NPDES construction stormwater (OHC) coverage can exist before a
  project does.

### 1.5 — Hydrology screen

- **Receiving water for the city WRF:** the Auglaize River at **River Mile 84.9**.
  - Source: Ohio EPA, *Fact Sheet for NPDES Permit Renewal, Wapakoneta WRF, 2024*, permit
    **2PD00019** / NPDES **OH0027952** (p. 7)
    (<https://dam.assets.ohio.gov/image/upload/epa.ohio.gov/Portals/35/permits/doc/2PD00019.fs.pdf>)
    `[verified]`.
  - Instream design flows (Table 14, StreamStats basis): **7Q10 2.29 cfs**, 1Q10 1.49 cfs, summer
    30Q10 3.51 cfs. The StreamStats figure is reduced by its standard error from a 110 mi² drainage
    area.
  - The plant is expanding to an **average daily design flow of 6.0 MGD** with flow augmentation.
    This follows Director's Final Findings and Orders (DFFOs) over the effluent's toxicity from total
    filterable residue `[verified]`.
- **The WLA already carries the expansion.** The Maumee nutrient TMDL raised Wapakoneta WWTP's WLA
  design flow **4.0 → 6.0 MGD** (Group GP2), per
  `data/reference/hydrology/maumee-tmdl-responsiveness.yaml` `[verified]`.
- **Effluent-dominated `[inference]`.** 6.0 MGD ≈ 9.3 cfs against a 2.29 cfs 7Q10. At design flow
  in a 7Q10 week, the reach below RM 84.9 would be roughly **80% effluent**.
- **Restroom flow is immaterial to that ratio.** The CTS ask adds only restroom sanitary to it, and
  routes cooling water elsewhere by its own account `[reference]`.
- **Lima drinks downstream of this outfall `[verified]` as to the flow path.** Lima's Auglaize River
  pump stations (L107 "Auglaize Pump St." and L111 "Auglaize River St #2", 40°43'45"N 84°18'01"W)
  are in the City of Lima's own 2022 NPDES renewal application
  (`data/extracted/legal/prr-mandamus/prr-production-2026-08-lima/lima-wwtp-npdes-renewal-application-2022.application.yaml`).
  ODNR's withdrawal registry puts reg. 01320 "LIMA CITY PWS-AUGLAIZE" (2 intakes, 161 MGD capacity)
  at the same point (`data/reference/ohio-water-withdrawal/allen.yaml`). The WRF outfall is at
  40.5702, -84.2107 (`data/extracted/oepa/wapakoneta/2PD00019.npdes.yaml`). Both points snap to NHDPlus
  flowlines (outfall COMID 15652927, intake COMID 15652553), and the USGS NLDI downstream-mainstem
  trace from the outfall reaches the intake's flowline within 30–35 km of channel (queried
  2026-10-18; the bracket is NLDI's distance argument, not a river-mile figure).
  - So the Wapakoneta WRF's effluent, and whatever TDS it carries under the DFFO relief, is in the
    river Lima pumps to fill Bresler and Williams `[inference]`. How much depends on when Lima pumps,
    which is a refill-season, higher-flow question, not the 7Q10 one above `[open]`.
  - This is the **hydrologic** relation the guardrail allows. It does not tie the two sites' actors
    or land together.
- **Gage:** 04186500 Auglaize River near Fort Jennings (DA 332 mi²), downstream, above the Ottawa
  confluence. It is live per USGS IV, checked 2026-10-12. The at-Wapakoneta gage 04185800
  (DA 103 mi²) serves no series.

### 1.6 — Regulatory record (status as of 2026-10-18)

| Instrument | Status |
|---|---|
| Conditional-use application (§1282.04, M-3) | **Not filed**, per the City's statement (§1.1) |
| Annexation petition | **Not filed**, per City |
| Development agreement / NDA | **None executed**, per WDN `[reference]` |
| Council briefing | 2026-10-05, minutes `[verified]` (§1.2a); company not named |
| Ohio SOS: Colocation Technology Services LLC | `[open]`; registry behind a browser check (2026-10-18) |
| AEP feasibility study | Exists per City; not in hand `[open]` |
| PJM large-load / interconnection request | Not searched `[open]` |
| Ohio EPA air PTI (emergency generators) | None expected pre-application; not searched `[open]` |
| Ohio EPA NPDES (stormwater / industrial) | None; not searched `[open]` |
| AMP delivery-service contract | `[open]` |

## 2 — The City's prior instrument: data centers as a conditional use (2024)

The source for the entries below is the City Council minutes, held since 2026-10-28 under
`data/documents/wapakoneta/governance/` (the 09-03 agenda and the 09-03 through 11-18 minutes,
from the City's own document library) and extracted, with page cites and a tag per entry, in
`governance/council-2024-data-center-ordinances.timeline.yaml`. What the minutes record is read
off them; the items marked `[open]` or `[inference]` below are not. Those minutes are
born-digital and were read from their text layer.

- **2024-09-03.** The agenda lists "WAEDC Josh Bloomfield – data processing centers". The minutes
  record that he did not present, "due to illness."
- **2024-09-16.** Bloomfield presented on "data processing centers". He urged Council "to be
  proactive in their discussion and consideration of city zoning, utilities and potential sites
  prior to being approached." No company is named.
- **2024-10-07.** President Doll asked whether the Planning Commission was examining the zoning
  code after the presentation, and SSD Price "spoke to John Courtney at the AMP conference on the
  matter." The Mayor's report lists a 09-23 meeting with Bloomfield, subject not stated.
- **2024-10-21: first readings.** Law Director Neal said "having them both clarifies a 'warehouse'
  versus 'data warehouse' and allows the City more discretion." SSD Price added: "should the City
  decide to allow a data warehouse in the future, Ord 2024-46 contains the language needed for
  this." The same meeting held an executive session on "confidential information regarding
  economic development", inviting Bloomfield. Its subject is not minuted `[open]`.
- **2024-11-04: second readings.** The Planning Commission had no comments, "utility rate
  conversations" had not occurred, and Courtney & Associates had "not yet" provided input, all per
  SSD Price. Councilor Dunlap "shared a text from a citizen concerned about water usage and the
  people needed for employment purposes." President Doll called Ord. 2024-46 "merely clarifying
  the zoning language."
- **2024-11-18: both adopted on third reading, 7–0, with no recorded discussion.** So neither the
  Planning Commission comment, the utility-rate conversation nor the consultant's input is recorded
  as having happened before adoption `[inference]`.
  - **Ord. 2024-46**, "AN ORDINANCE AMENDING SECTION 1250.10 (174) … SPECIFIC TO THE ZONING
    DEFINITION OF 'WAREHOUSE'" (Dunlap / Sheipline).
  - **Ord. 2024-48**, "AN ORDINANCE AMENDING SECTION 1282.04 … SPECIFIC TO THE CONDITIONAL PERMITTED
    USES OF THE M-3 INDUSTRIAL DISTRICT" (Dunlap / Muhlenkamp).
- **Two corrections to this section's 2026-10-12 text,** found by reading the minutes:
  - The Neal and Price answers were given at the 10-21 first reading only, not at "10-21 / 11-04".
  - The 11-04 water remark is a councilor relaying a citizen's text. It is not a citizen speaking,
    and the earlier quoted words "concern about water usage" are not in the minutes.

**The codified text (read 2026-10-18).** Neither ordinance title says "data center", but the
codification does. Read from American Legal's codification (supplement 2026 S-27, current through
2026-05-18), captured under `data/documents/wapakoneta/governance/` and extracted in
`governance/wapakoneta-zoning-code-data-centers.zoning.yaml`:

- **§1250.10(174)** now excludes from "Warehouse" a subcategory A, **"Data Warehouse (Center)"**:
  buildings "specifically designed or modified to house data and related infrastructure support
  equipment", naming "computer equipment colocation services". The definition sets no size
  threshold. Its history note cites Ord. 2024-46, passed 11-18-24 `[verified]`.
- **§1282.04** lists **"Data warehouses (centers)"** among the M-3 uses "permitted only if
  specifically authorized by the Planning Commission in accordance with Chapter 1252". Its history
  note cites Ord. 2024-48, passed 11-18-24 `[verified]`.
- **M-3 is the only industrial district** that admits a data center: the M-1, M-2 and M-3 use lists
  on file name it only as the M-3 conditional use `[verified]`. The rest of the 2026-10-18 sweep
  (every district chapter) found no other mention, but those pages are not committed `[inference]`.
- M-1 and M-2 permit "Wholesale and warehouse establishments" by right (§1278.02, §1280.02)
  `[verified]`. The carve-out therefore closes a by-right path, as the Law Director described
  `[inference]`.
- **The review is generic.** §1252.07 (2010, unamended) governs. The Planning Commission makes eight
  written findings `[verified]`. Water and power can be reached only through general ones:
  "adequate utility … facilities", the necessary permits, and public health and safety. None is
  specific to data centers `[inference]`.
  - "No public hearing need be held" unless the Commission deems one necessary `[verified]`.
  - The permit "shall run with the land and not the applicant/owner" `[verified]`.
  - No application item asks for water demand, load, cooling or generation `[verified]`.
- **§1252.07(b)(17)** points applicants to standards "listed in Section 1254.08(c)". §1254.08 has
  no subsection (c): it is a dangling cross-reference `[verified]`.

**The WCOIC parcels on the City's zoning layer (queried 2026-10-28).** The City's zoning web app
(the viewer in Instruments item 7) draws its districts from Auglaize County's ArcGIS server:
`gis.auglaizecounty.org/arcgis/rest/services/Wapakoneta/WapakonetaZoning/MapServer/1` (field
`ZONECLASS`; the layer carries no update date) and the county parcels at
`BasemapServices/Parcels_and_Addresses_2019/MapServer/0`. Despite the "2019" in its name, the
parcel layer is current: it records transfers as late as 2026-08-06. Intersecting the two:

- The parcels whose legal description reads "WEST CENTRAL OHIO INDUSTRIAL PARK" are **19 lots
  (I4504500100–I4504500600), 102.408 ac in all**, around 40.550, -84.186 `[reference]`.
- **Every one of them falls in M-1. Two (I4504500401, I4504500404) also touch R-3. None touches
  M-3** `[reference]`.
- No lot is 30 acres. The largest vacant one is I4504500400, 15.986 ac, held by Wapakoneta
  Industrial Development Inc. since 1991. The City holds I4504500200 (6.258 ac) and I4504500502
  (1.31 ac) `[reference]`.
- The M-3 polygons lie **south of the park**, on land that is mostly in private hands: Pratt Paper,
  farm parcels of 30–209 ac, and AEP Ohio Transmission's 4.27 ac at 570 Short Road `[reference]`.
- So **if CTS's site is a platted WCOIC lot, a data center there needs a rezoning to M-3 before any
  conditional use** `[inference]`. A rezoning is a Council ordinance, which a conditional use alone
  is not.
- The layer is a finding aid, not the zoning map of record. A rezoning since it was drawn would not
  show. WAEDC's "greenfield" WCOIC site may also reach beyond the platted lots. Both are `[open]`.

**Still open.** The codification is the publisher's, not the signed instruments: Ord. 2024-46 and
2024-48 as enacted are not in hand `[open]`. The official zoning map for WCOIC, and which land the
"30 acre" site is, are `[open]`.

## 2a — Adjacent, not a data center: Regensyn Energy at the WRF (Ord. 2026-20)

This is **not** a data-center entry. It is recorded because it concerns the same treatment plant
(§1.5), the same WAEDC intermediary, and the WRF's TDS problem.

- **2026-04-20.** The agenda lists "Chas Roemer – Regensyn Energy LLC" under guest petitions and
  **Ord. 2026-20**, "AN ORDINANCE AUTHORIZING A COOPERATION AGREEMENT BETWEEN THE CITY OF WAPAKONETA
  AND REGENSYN ENERGY LLC AND DECLARING AN EMERGENCY". The minutes (p. 2, image-checked) record:
  - Roemer, representing Regensyn, addressed Council about "the emerging technology regarding the
    removal of forever chemicals from wastewater streams while simultaneously creating energy". He
    said the work had moved "from lab level testing to a commercialized model in Corpus Christi, TX"
    `[reference]`.
  - He stated "there is no financial obligation on the City of Wapakoneta, nor any obligation on
    Regensyn Energy LLC to continue their investments and efforts indefinitely", and that Ord. 2026-20
    "is a cooperative agreement between the parties to show this technology can be used to clean the
    wastewater system and generate energy" `[reference]`.
  - Bloomfield (WAEDC) introduced Rick Johnson of Applied Environmental Solutions, "working closely
    with Wapakoneta's Wastewater Department for project development on said cooperative agreement."
  - Ord. 2026-20 was read once, the rules were suspended 6–0, and it was **adopted 6–0** on emergency
    `[verified]`.
- **The characterization diverges.** The minutes say "forever chemicals" (PFAS). The *Wapakoneta Daily
  News* (Bob Neelski, 2026-04-22) attributes the City's interest to Mayor Dan Lee "researching
  solutions for ways to improve total dissolved solids metrics" `[reference]`. TDS is the WRF's
  documented problem: the 2019 DFFO and the 2024 permit's tiered TFR limits (§1.5;
  `reference/owea-2019-tds-challenges.yaml`). Which constituent the agreement targets is `[open]`.
- **Not in hand `[open]`:** Ord. 2026-20 as signed, the cooperation agreement itself, its term, any
  site or discharge it touches, and whether a pilot unit at the WRF needs an Ohio EPA permit
  modification or PTI.

## 3 — Elsewhere in Auglaize County

- **St. Marys** (city, ~13 mi west) adopted a **12-month data-center moratorium**. It passed first
  reading on 2026-05-27 and was adopted around 2026-06-22. The ordinance number is `[open]`, and no
  specific proposal behind it was found. Sources: Lima News 2026-05-28 and 2026-06-23, and the
  *Daily Standard* 2026-05-28 `[reference]`.
- **Cridersville, Minster, New Bremen, New Knoxville:** no data-center activity found in the
  2026-10-12 web sweep `[reference]`. This is a press-and-web negative only. RSEI 518210, ECHO and
  PJM-queue checks have **not** been run for Auglaize.
- **Nov 2026 ballot:** no Auglaize data-center measure found. This is a weak negative: Ballotpedia's
  2026-09-21 roundup does not list jurisdictions.

## Instruments to pull (priority order)

1. **The City's Facebook post.** Capture it with a date before it can be edited or deleted. It is
   the one source that states the City's no-commitment position, and today it exists here only as
   a paste.
2. **Ord. 2024-48 and Ord. 2024-46 as enacted.** The codified sections are now read (§2). American
   Legal (`codelibrary.amlegal.com/codes/wapakoneta`) answers 403 over HTTP/2 but 200 over HTTP/1.1.
   The signed ordinances still need the Clerk. Ask for the zoning map covering WCOIC at the same
   time.
3. **Ord. 2026-20 and the Regensyn cooperation agreement** (§2a), from the Clerk. The 2026 Council
   minutes are read for the Bloomfield briefing (2026-10-05, §1.2a); the June and September
   executive sessions are the remaining question, and minutes will not answer it.
4. **The Ohio SOS record** for Colocation Technology Services LLC: formation, statutory agent,
   principals, foreign or domestic. Pull it by hand in a browser at businesssearch.ohiosos.gov.
   If it is a foreign LLC, the home-state filing (South Carolina is the only state its site names)
   is the next record.
5. **The AEP feasibility study** the City requested, via an R.C. 149.43 request to the City. With it,
   the City's correspondence with AEP, AMP, WAEDC and CTS. Drafted, **not sent**:
   `governance/records-requests/2026-10-18-wapakoneta-clerk-of-council.md` (it also asks for items 2
   and 3 and the WCOIC zoning).
6. **The CTS informational meetings**: dates, venue and materials.
7. **The WCOIC parcel(s)**: which land the "30 acre" site is, and the official zoning map. The
   City's GIS zoning viewer
   (<https://augcogis.maps.arcgis.com/apps/webappviewer/index.html?id=8f3f1b5bcb734d3c8b52326346667be9>)
   shows the platted park as M-1, not M-3 (§2, queried 2026-10-28). It is a finding aid, not the
   zoning map of record. Any rezoning ordinance for the park would appear in the Council record
   first.
8. **The blowdown disposal path.** A hauled waste stream must land at a permitted receiver.
9. **The Wapakoneta WRF's DFFO after 2025-12-31.** The permit (OH0027952), the 2019-02-06 DFFO
   (eDoc 992359) and its 2024-11-20 modification (eDoc 3301212) are in the record. The
   modification extended the WWTP work and the interim limits to 2025-12-31, and its findings
   name wells piped near the outfall as the augmentation water. That date has passed. Ohio EPA's
   2025-07-29 inspection (eDoc 3793658) dates the new plant's start-up to 2024-08-21, though a form
   comment in the same report says 2025-08-01. The City's 2026-01-15 non-compliance notice
   (eDoc 3971298) says it "now" has flow augmentation online (`[verified]` as the City's statement only),
   and the same notice reports a TFR exceedance (1687 against 1561 mg/l). Whether Ohio EPA has
   acknowledged completion, or terminated or modified the order again, is open. The portal's other
   2PD00019 row (eDoc 3480641) is a mis-indexed ODOT rest-area order, not Wapakoneta's.
   - **Re-swept 2026-10-28; no later order.** The eDocument portal (`watermark oepa portal --county
     AUGLAIZE --program NPDES --entity WAPAKONETA`; output committed as
     `data/research/oepa-portal-wapakoneta-2026-10-28/manifest.yaml`) returned 268 rows over 7
     permits, the same set as the 2026-10-27 run. It lists no order on 2PD00019 dated after
     2024-11-20 `[verified]` as to the portal. Controls in the same run: both 3301212 (the 2024 DFFO)
     and 3971298 (the 2026-01-15 notice) came back, and the newest row is dated 2026-10-22
     `[verified]`. Because the silence runs 10 months past the deadline, well beyond the portal's
     1–28-day publication lag, it is not a lag artifact `[inference]`. An order served but never
     posted to the portal would not show.
   - Later WWTP filings are listed but **not read**: non-compliance reports 3944611 (2025-12-18),
     4164444 (2026-06-22), 4190722 (2026-07-15) and 4267970 (2026-09-21), all on 2PD00019, and the
     SSO annual reports 4024930 (2026-03-02) and 4032419 (2026-03-05). The portal's description says
     only "NONCOMPLIANCE". Whether any of them is a TFR exceedance is `[open]` until they are read.
10. **The county-wide negative checks**: RSEI 518210, ECHO and the PJM queue for Auglaize.

## Sources

- City of Wapakoneta, City Administration statement, Facebook (undated; text pasted 2026-10-12):
  <https://www.facebook.com/cityofwapakoneta/posts/pfbid0uaLu5N75YRUZjhXZ1rGwkqYX7FL1fTTaB69UKmz2kZ8JJR1v3PoqZ4aNnuPaiyCCl>
- *Wapakoneta Daily News*, 2026-10-08:
  <https://www.wapakdailynews.com/news/a-data-center-in-wapakoneta/article_30fa606e-99e6-4ea4-83e1-f45c0beaf5d8.html>
- City Council agenda 2024-09-03 and minutes 2024-09-03, 09-16, 10-07, 10-21, 11-04 and 11-18, filed
  under `data/documents/wapakoneta/governance/` (source URLs and sha256 in that shelf's
  `filename-map.yaml`) and extracted in `governance/council-2024-data-center-ordinances.timeline.yaml`.
- City Council agenda 2026-04-20 and minutes 2026-04-20, 06-15, 09-08 and 10-05, filed under
  `data/documents/wapakoneta/governance/` (source URLs and sha256 in that shelf's `filename-map.yaml`).
- *Wapakoneta Daily News*, Bob Neelski, "Council greenlights trial to address TDS issues", 2026-04-22
  (lede only; paywalled):
  <https://www.wapakdailynews.com/news/council-greenlights-trial-to-address-tds-issues/article_c3d032fd-4b9e-404e-b160-15a8ad64e9cf.html>
- Ohio EPA, Fact Sheet for NPDES Permit Renewal, Wapakoneta WRF, 2024 (2PD00019):
  <https://dam.assets.ohio.gov/image/upload/epa.ohio.gov/Portals/35/permits/doc/2PD00019.fs.pdf>
- City of Wapakoneta 2025 CCR:
  <https://files-backend.assets.thrillshare.com/documents/asset/uploaded_file/5500/Cow/9b742bf8-0c2b-4605-9be3-438522796072/Revised-FINAL-2025-CCR-Text---For-2026-Year.pdf>
- EIA-861 2024, Service_Territory: City of Wapakoneta #20077 and Ohio Power Co #14006, both in
  Auglaize County.
- U.S. Census 2024 Gazetteer, places, Ohio: Wapakoneta city, GEOID 3980766.
- USGS NWIS IV, 04186500 (checked 2026-10-12).
- WAEDC, WCOIC: <https://whywapakoneta.com/west-central-ohio-industrial-center>; JobsOhio listing:
  <https://jobsohio.com/available-sites/west-central-ohio-industrial-center>
- AMP, "Member Spotlight: Wapakoneta" (2019): <https://www.amppartners.org/news/member-spotlight/wapakoneta-ohio/>
- St. Marys moratorium: <https://www.limaohio.com/top-stories/2026/06/23/st-marys-council-adopts-temporary-data-center-ban/>

## Appendix — the City's statement, as pasted (2026-10-12)

This is a transcription supplied by the requester, **not a capture**. Facebook's obfuscated
timestamp header is omitted, the body is otherwise verbatim, and paragraph breaks are condensed. It
is kept here only because no archived copy exists. Cite the post, never this appendix.

> City Administration would like to provide an update about the potential development of a data
> center in our community and where it currently stands.
>
> To start, the City has not entered into negotiations with the developer, Colocation Technology
> Services (CTS), approved any part of the project, or made any commitments to the development. CTS
> has also not submitted requests for annexation, conditional use approval, or other
> project-related approvals. All of the known information comes from discussions with WAEDC and
> preliminary questions the city has asked WAEDC and CTS.
>
> For a little context, The Wapakoneta Area Economic Development Council (WAEDC), a separate entity
> from the city, works with businesses interested in locating or expanding in our community. Over
> the past few years, WAEDC has received several inquiries about potential data center projects.
> Recognizing this growing interest, City Council passed legislation in 2024 making data centers a
> "conditional use," requiring additional review and approval before one could locate here.
>
> City Administration also made it clear to WAEDC that any potential data center project should be
> discussed openly, allowing residents to learn about the proposal, ask questions, and share
> concerns before decisions are made. WAEDC agreed with this approach and with evaluating each
> project on its own merits.
>
> CTS approached WAEDC about the possibility of developing a smaller sized data center in the
> industrial park. During early conversations between WAEDC and CTS, they also agreed to open and
> transparent discussions with the public, as that was made clear to them when they submitted their
> request.
>
> The City has been aware of this potential project for a few months. However, much of that time
> was spent exploring preliminary questions and waiting for responses about electric service and
> whether existing infrastructure could support a facility requiring 50 megawatts of power. We
> believed it was important to determine whether the project was even feasible before considering a
> more detailed proposal.
>
> As part of that work, the City requested an initial feasibility study with American Electric
> Power (AEP). The results indicated that the facility could be served without improvements to
> AEP's existing infrastructure. The proposed arrangement would establish a new connection directly
> to an AEP electric line rather than supplying power through the City's existing electric
> distribution system.
>
> Based on our utility structure, CTS would also be considered a Delivery Service Customer, meaning
> it would purchase electricity through separate contracts with American Municipal Power (AMP),
> independent of the City's existing power supply contracts. This arrangement applies to large
> electric customers with demands exceeding 10 megawatts and would keep the facility's power
> purchasing separate from that of the City's other customers.
>
> Regarding water usage, CTS has indicated it would use a closed-loop cooling system requiring
> approximately 5,000 to 10,000 gallons per day. For comparison, the EPA estimates an average person
> uses about 80 gallons daily. While this may sound significant, the City's water treatment plant is
> designed to handle millions of gallons per day, currently treats more than a million gallons
> daily, and already serves customers with substantially higher water demands. Based on the
> estimates provided, this facility's water usage would be well within the capacity of our existing
> system and is not expected to present a concern.
>
> CTS has also indicated that wastewater would primarily come from normal restroom use. Water from
> its cooling system would not be discharged into the City's sewer system but would instead be
> periodically removed and properly disposed of off-site.
>
> The proposed location is within an existing industrial park, where CTS anticipates noise levels
> similar to other industrial operations. Their estimate is that the noise will be approximately 60
> decibels at their property edge, which is around the same sound level of a window air conditioner.
>
> Again, all of this information is preliminary. It reflects what is currently known or has been
> provided by CTS and does not mean every question has been answered or that all information has
> been independently verified. The most important factor with all of the utilities would be
> ensuring that they remain whole and that utility revenue generated by the facility would more
> than cover any service costs, so that no costs could ever be subsidized to other residents or
> businesses. That will require additional due diligence, if the project moves forward.
>
> We understand that data centers have raised concerns in communities across the country, including
> our surrounding area. Questions about electricity, water, infrastructure, noise, environmental
> impacts, and long-term community effects are reasonable and deserve consideration.
>
> Surrounding communities' experiences can help us identify important questions, but data centers
> can differ considerably in size, design, operations, and utility demands. We believe it is
> important to learn from those experiences while evaluating this particular proposal based on its
> own facts and circumstances, rather than assuming that what happened elsewhere will necessarily
> happen here.
>
> Our responsibility is to understand both the concerns and potential benefits, ask questions,
> verify information, and fairly evaluate the company, the proposed location, and what the
> development would mean for Wapakoneta. We recognize that residents may have different opinions,
> and those perspectives deserve to be heard.
>
> CTS has expressed a willingness to provide public presentations and answer questions as more
> information becomes available. City Council and Administration will be learning about much of the
> proposal alongside the community. The preliminary work completed over the past few months was
> intended to answer basic feasibility questions for our own infrastructure, not to evaluate the
> entire project or make decisions outside of public discussion.
>
> Administration's goal is not to approach this project with a predetermined outcome, either for or
> against it. We want to give it the same fair consideration we would any other industrial
> development, with additional attention to public input given the mixed information surrounding
> data centers.
>
> A fair review does not mean overlooking concerns or assuming benefits. It means understanding
> both, asking questions, and making decisions based on facts rather than assumptions. Our
> responsibility is to consider what is best for Wapakoneta and its residents, both today and in the
> future.
>
> In the coming weeks, CTS will be holding informational meetings, open to the public, prior to
> submitting any development requests to the City. We encourage all those interested to attend and
> get answers to the questions and concerns you have.
>
> Thank you,
> City Administration
