# Fort Wayne data-center facility — discovery (Google "Project Zodiac")

Resolves **#360** (the data-center-activity dimension). The facility the registry carried as a
codename-only "confirmed" placeholder (`GCP`) is now **documented from the public record**. Tags
follow the project vocabulary (`[verified]` = primary/press/government source; `[reference]` =
authoritative outside data; `[inference]`; `[open]`).

This is external public-record discovery, not corpus extraction — **no primary documents (air permit,
IURC filing, abatement ordinance, IDEM wetland permit) are extracted into the corpus yet**; those are
the follow-up extraction targets in §7. Accordingly the `SiteProfile.facility` power basis stays
**`None`** (see §5): it requires air-permit-grounded MW, which is undisclosed here.

## 1. The facility `[verified]`

| Field | Value |
|---|---|
| Operator | **Google** (Google Cloud / AI workloads — the registry `GCP` codename) |
| Local codename | **Project Zodiac** (the name on the local-government filings) |
| Location | Southeast Fort Wayne, Allen County, IN — E. Tillman & Adams Center Rds (Phase I); E. Paulding & 6015 Adams Center Rd (Phase II) |
| Scale | ~12-building campus on **700+ acres** (Phase II adds 5 buildings incl. an electrical-transmission building) |
| Investment | **$2 billion** (first disclosed "at least $845M" Jan 2024 → "$2B" by the Apr 2024 groundbreaking) |
| Jobs | ~1,000 temporary (construction); **~200 permanent** |
| Status | **Operational** — Phase I went live Dec 11, 2025; Phase III under environmental review (permit requested Mar 2026) |
| Serving utility | **Indiana Michigan Power (I&M)** — matches `serving_utility` (EIA #9324, AEP, IURC, PJM AEP zone) |

## 2. Timeline `[verified]`

- **Oct 2023** — a 12-building, 700+ ac campus ("Project Zodiac", mystery developer) first surfaces.
- **2023** — Fort Wayne approves a 10-year, **50% property-tax abatement (~$55.5M)**.
- **Jan 2024** — Google confirmed as the developer; "at least $845M".
- **Apr 26, 2024** — groundbreaking; investment restated at **$2B**.
- **Sep 16, 2025** — IDEM grants the Phase II wetland permit; an expansion (5 buildings) announced.
- **Dec 11, 2025** — Phase I goes **operational**.
- **Mar 2026** — Google requests the Phase III permit (under environmental review).

## 3. Incentives `[verified]`

10-year, **50% property-tax abatement ≈ $55.5M**, with a floor: the city receives **≥ $1M/yr from
2025**, rising to **$1.2M after four buildings** and upward as the campus grows. Rezoning approved
locally. (The full abatement ordinance + the development agreement — described in coverage as
"very broad — on purpose" — are extraction targets, §7.)

## 4. Energy / grid `[verified / reference]`

- **Google–I&M demand-response program**, approved by the **IURC**, to curtail ML-workload power in
  certain hours/seasons to reduce grid strain. `[verified]`
- I&M is party (with Amazon, Google, Microsoft) to the **large-load interconnection rules** filed at
  the IURC for hyperscaler loads. `[verified]`
- Context (system-wide, not the campus alone): I&M projects **peak demand ≈ doubling to ~8,000 MW by
  2030** (from ~4,000 MW), driven by hyperscaler data centers. `[reference]`
- **The campus's own MW load is NOT publicly disclosed** — the demand-response framing substitutes for
  a hard capacity figure. `[open]` (see §5).

## 5. Why `SiteProfile.facility` stays `None` `[open]`

`SiteFacility` is an **air-permit-grounded power basis** (`genset_count` / `genset_mw` / `it_load_mw`
…), as for Lima (OEPA Air PTI P0138965). Fort Wayne's equivalent — the **IDEM air permit** for the
campus's emergency gensets — has not been extracted, and no IT-load MW is publicly disclosed. Per data
discipline (never fabricate a figure), the facility is documented here but `facility=None` /
`load_share=null` remain correct until that permit is pulled (§7). The data-center *activity* dimension
is now **confirmed and characterized**; the *power basis* is the open piece.

## 6. The thesis read `[inference]`

- **Load, not jobs.** $2B capital + ~200 permanent jobs + a $55.5M abatement is the load-not-jobs
  subsidy shape the network exists to compare against Lima (`docs/ECONOMICS.md`). The Allen County
  information-sector LQ of 0.44 (county baseline) is consistent — the campus is an electricity/water
  load, not an employment base.
- **Receiving-water / opacity tie-in.** The campus (SE Fort Wayne, Adams Center Rd corridor) is filling
  **6+ acres of wetlands** across Phases I–II (3.6 ac + ~2.5 ac; mitigated via The Openings bank), in
  the Allen County / Upper Maumee (HUC-8 04100005) drainage `[inference]` — the same headwaters reach
  the Fort Wayne WWTP discharges to ([`wwtp-receiving-water.md`](wwtp-receiving-water.md)). Commenters
  flagged the wetlands' lost **stormwater-filtering** function; IDEM issued the Phase II permit
  **without the publicly requested hearing** — an opacity-of-process datapoint on the BOSC thesis.

## 7. Follow-up extraction targets (corpus-grounding) `[open]`

To move these facts from `[reference]`/press to corpus `[verified]` and to populate the power basis:

1. **IDEM air permit** for the campus gensets → `SiteFacility` MW (the analog of Lima's OEPA Air PTI).
2. **IURC docket(s)** — the I&M large-load interconnection agreement + the Google–I&M demand-response
   approval (the load/curtailment terms).
3. **Fort Wayne abatement ordinance + development agreement** ("Project Zodiac").
4. **IDEM §401 / wetland permits** (Phases I–III) + the mitigation-bank record — the receiving-water /
   stormwater dimension.
5. Local **rezoning** record for the Tillman/Adams Center & Paulding parcels (also unblocks the #362
   site footprint + SSURGO/GIS work).

## Sources

- [Gov. Holcomb announces Google $2B data center (IEDC)](https://iedc.in.gov/events/news/details/2024/04/26/gov.-holcomb-announces-google-is-building-a-2b-data-center-in-northeast-indiana)
- [Google announces $2bn Fort Wayne campus (DCD)](https://www.datacenterdynamics.com/en/news/google-announces-2bn-campus-in-fort-wayne-indiana/)
- [$2B Google data center now operational (WANE 15)](https://www.wane.com/top-stories/2-billion-google-data-center-now-operational-in-fort-wayne-outlines-its-plans-for-the-community/)
- [Investment grows to $2 billion (Inside INdiana Business)](https://www.insideindianabusiness.com/articles/google-data-center-project-in-fort-wayne-grows-to-2-billion)
- [Fort Wayne approves tax abatement (fwbusiness.com)](https://www.fwbusiness.com/news/government/article_dddc1c20-ed4b-55f6-8be5-89ff78a0876c.html)
- [Google–I&M demand-response approved by IURC (DCD)](https://www.datacenterdynamics.com/en/news/google-and-im-gain-regulatory-approval-for-demand-response-system-at-fort-wayne-data-center-in-indiana/)
- [I&M / Amazon / Google / Microsoft large-load interconnection rules (Utility Dive)](https://www.utilitydive.com/news/indiana-michigan-power-aep-amazon-google-microsoft-data-center-interconnect/733850/)
- [IDEM grants Phase II wetland permit (WANE 15)](https://www.wane.com/top-stories/idem-grants-wetland-permit-for-phase-ii-of-google-data-center-in-fort-wayne/)
- [Indiana approves wetlands expansion despite opposition (DCD)](https://www.datacenterdynamics.com/en/news/indiana-approves-expanding-googles-fort-wayne-data-center-campus-onto-protected-wetlands-despite-local-opposition/)
- [Google's agreement is very broad — on purpose (WANE 15)](https://www.wane.com/top-stories/fort-waynes-google-agreement-is-very-broad-on-purpose/)
