# Wapakoneta / Auglaize Co., OH — Data-Center Activity Register

Discover-and-pin register for the Wapakoneta watershed point (upper Auglaize River → **Maumee** at
Defiance → Lake Erie). Status **as of 2026-10-12** (#2184). Tags are BOSC evidentiary discipline:
`[verified]` = cited primary/government source, `[reference]` = secondary source or a party's own
self-report (leads only, never a finding), `[inference]` = arithmetic or pattern from cited inputs,
`[open]` = not found in any public source yet. **Nothing here is in the BOSC corpus yet**: this
records the public record as of the date above and the primary instruments to *pull*. Nothing here
is fabricated; every figure is cited or marked `[open]`.

**The finding is a proposal with no instrument behind it.** One developer has asked about one site.
By the City's own account, nothing is negotiated, approved, committed, or filed. Wapakoneta's
`SiteProfile` therefore carries `facilities=()`, and the `facility` readiness domain stays
**locked**. The one instrument that exists is the City's own: in 2024 it legislated conditional-use
review for this class of use **before** any developer asked.

## Disambiguation guardrail — run first, always

- **"CTS" is not QTS.** QTS (Quality Technology Services) is the Van Wert Mega Site operator
  (`data/extracted/van-wert/`). **Colocation Technology Services LLC** has no web footprint that the
  2026-10-12 sweep could find. Exact-phrase searches return nothing. The Ohio SOS business search was
  down on 2026-10-12 (the API showed a maintenance page and the site returned 403). **Never resolve
  "CTS" by acronym**: the identity of this entity is `[open]` until the SOS record is pulled.
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
Council. The briefing date is `[open]`; it was probably the 2026-10-05/06 meeting, but the minutes
are not pulled.

- **Site.** "a 30 acre 50 megawatt data center at the **West Central Ohio Industrial Center**." The
  City's post says only "the industrial park"; the press supplies the name.
  - WCOIC is at I-75 × US-33, inside city limits, and SiteOhio-authenticated per WAEDC's own site
    (<https://whywapakoneta.com/west-central-ohio-industrial-center>).
  - **The parcel(s) are `[open]`.**
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
- **Projected consumption:** 5,000–10,000 GPD, CTS's self-report via the City `[reference]`.
  - At the 4× scale-up to 200 MW `[inference]`, this would be ~20,000–40,000 GPD if it scaled
    linearly with load. That linear scaling is not a claim anyone has made.
  - It is an order of magnitude a closed-loop design makes plausible. It is not demonstrated.
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
- **Gage:** 04186500 Auglaize River near Fort Jennings (DA 332 mi²), downstream, above the Ottawa
  confluence. It is live per USGS IV, checked 2026-10-12. The at-Wapakoneta gage 04185800
  (DA 103 mi²) serves no series.

### 1.6 — Regulatory record (status as of 2026-10-12)

| Instrument | Status |
|---|---|
| Conditional-use application (§1282.04, M-3) | **Not filed**, per the City's statement (§1.1) |
| Annexation petition | **Not filed**, per City |
| Development agreement / NDA | **None executed**, per WDN `[reference]` |
| Ohio SOS: Colocation Technology Services LLC | `[open]`, registry down 2026-10-12 |
| AEP feasibility study | Exists per City; not in hand `[open]` |
| PJM large-load / interconnection request | Not searched `[open]` |
| Ohio EPA air PTI (emergency generators) | None expected pre-application; not searched `[open]` |
| Ohio EPA NPDES (stormwater / industrial) | None; not searched `[open]` |
| AMP delivery-service contract | `[open]` |

## 2 — The City's prior instrument: data centers as a conditional use (2024)

All four items below are `[verified]` against City Council minutes. The 11-18 minutes were read
directly on 2026-10-12. The earlier minutes were read by the sweep via their Wayback `id_` URLs.

- **2024-09-16.** WAEDC's Bloomfield presented on "data processing centers." He urged Council "to be
  proactive … prior to being approached." The item was also on the 09-03 agenda
  (`wapakoneta.net/wp-content/uploads/2024/10/09-16-2024-Minutes.pdf`).
- **2024-10-07.** SSD Price "spoke to John Courtney at the AMP conference on the matter."
- **2024-10-21 / 11-04.** These were the first and second readings. Law Director Neal said "having
  them both clarifies a 'warehouse' versus 'data warehouse' and allows the City more discretion."
  SSD Price added: "should the City decide to allow a data warehouse in the future, Ord 2024-46
  contains the language needed." On 11-04 a citizen raised "concern about water usage."
- **2024-11-18: both adopted on third reading, 7–0.**
  - **Ord. 2024-46**, "AN ORDINANCE AMENDING SECTION 1250.10 (174) … SPECIFIC TO THE ZONING
    DEFINITION OF 'WAREHOUSE'" (Dunlap / Sheipline).
  - **Ord. 2024-48**, "AN ORDINANCE AMENDING SECTION 1282.04 … SPECIFIC TO THE CONDITIONAL PERMITTED
    USES OF THE M-3 INDUSTRIAL DISTRICT" (Dunlap / Muhlenkamp).
  - Source: Council minutes 2024-11-18
    (<https://files-backend.assets.thrillshare.com/documents/asset/uploaded_file/5500/Cow/04ed5d3c-0a7b-4ea1-91fe-70341bd79b80/11-18-2024-Minutes.pdf>).

**Caveat.** Neither ordinance title says "data center." The link between these ordinances and data
centers rests on the minutes' discussion. The amended text of §1282.04 and §1250.10(174) is
**unread** `[open]`. The City's 2026 post describes the outcome as "making data centers a
'conditional use'." What the enacted text actually conditions is the first thing to pull.

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
2. **Ord. 2024-48 and Ord. 2024-46 as enacted**, plus codified §1282.04 and §1250.10(174). American
   Legal (`codelibrary.amlegal.com/codes/wapakoneta`) returns 403 to scripts, so ask the Clerk.
3. **The 2026 Council minutes for the Bloomfield briefing**, and every agenda item on CTS.
4. **The Ohio SOS record** for Colocation Technology Services LLC: formation, statutory agent,
   principals, foreign or domestic.
5. **The AEP feasibility study** the City requested, via an R.C. 149.43 request to the City. With it,
   the City's correspondence with AEP, AMP, WAEDC and CTS.
6. **The CTS informational meetings**: dates, venue and materials.
7. **The WCOIC parcel(s)**: ownership and transfer history from the Auglaize County Auditor/Recorder.
8. **The blowdown disposal path.** A hauled waste stream must land at a permitted receiver.
9. **The Wapakoneta WRF permit OH0027952 and its DFFO record**, from the Ohio EPA eDocument portal.
10. **The county-wide negative checks**: RSEI 518210, ECHO and the PJM queue for Auglaize.

## Sources

- City of Wapakoneta, City Administration statement, Facebook (undated; text pasted 2026-10-12):
  <https://www.facebook.com/cityofwapakoneta/posts/pfbid0uaLu5N75YRUZjhXZ1rGwkqYX7FL1fTTaB69UKmz2kZ8JJR1v3PoqZ4aNnuPaiyCCl>
- *Wapakoneta Daily News*, 2026-10-08:
  <https://www.wapakdailynews.com/news/a-data-center-in-wapakoneta/article_30fa606e-99e6-4ea4-83e1-f45c0beaf5d8.html>
- City Council minutes 2024-11-18:
  <https://files-backend.assets.thrillshare.com/documents/asset/uploaded_file/5500/Cow/04ed5d3c-0a7b-4ea1-91fe-70341bd79b80/11-18-2024-Minutes.pdf>
- Earlier 2024 Council minutes (09-16, 10-21, 11-04) via
  `web.archive.org/web/2025id_/https://wapakoneta.net/wp-content/uploads/2024/{10,11}/…-Minutes.pdf`
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
