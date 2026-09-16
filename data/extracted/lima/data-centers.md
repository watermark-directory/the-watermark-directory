# Lima / Allen County, OH — Data-Center Activity Register

Discover-and-pin register for the **reference site** — the Ottawa River watershed point, Lima's
municipal loop, the Cole St / Bluelick corridor. Status **as of 2026-09-16**.

Tags are BOSC evidentiary discipline: `[verified]` = read off a cited primary instrument this
corpus holds; `[inference]` = reasoned from `[verified]` inputs, labelled; `[reference]` =
secondary or authoritative-but-secondary source, a lead and never a finding; `[open]` = not
established anywhere in this record.

**This register is unusual among its peers and it is worth saying why.** Every other site's
register was written *before* the instruments landed, as a list of things to pull. Lima's is
written *after*: the corpus already holds the air permit, the CRA, the roadwork agreement, the
indirect-discharge permit, the county resolution spine and the OPC estimates. So this file's job is
**not** to re-derive any of that. It reconciles — it points at the committed extraction that owns
each figure, repeats the figure only in the form that extraction states it, and records what is
still missing. Where a number here differs from a number you have seen in the press, the press
number is the one that is wrong, and the correction is cited.

## Disambiguation guardrail

Run every time, no exceptions.

1. **Lima, Ohio (Allen County) ≠ Lima, Peru.** Also ≠ Lima, NY (Livingston Co.), Lima, IN (LaGrange
   Co.) and Lima Township, MI. Every entry below is confirmed to Allen County, Ohio by a parcel,
   deed, permit or council instrument in this corpus.
2. ⚠️ **"Project BOSC" is a CODENAME, never a key.** It is the NDA-era name for the campus, and it
   is carried here only because the county resolution ledger, the OEPA permit and the Tetra Tech
   estimates all print it. It is *also this platform's own name*, so a plain web search on "Project
   BOSC" returns this repository and its own documentation before it returns any record of the
   campus. Treat a search hit on the string as a hit on nothing until an instrument is behind it.
   Same class as the **Project Galaxy** three-county collision: a codename identifies a negotiation,
   not a site, and two counties can be running the same codename in the same season.
3. ⚠️ **A "Lima, OH 45801" address is not a City of Lima address.** The campus mails as
   *4110 N. Cole St., Lima, OH 45801* and sits in **American Township**. ZIP and postal city do not
   follow corporate limits in Allen County, and this exact ambiguity is what makes §1 below easy to
   get wrong.
4. **Pioneer, Ohio passed a data-center moratorium on the same day** and is not in this register.
   Pioneer is in **Williams County** — BOSC's `bryan` watershed point, a different basin entirely.
   The Toledo Blade's 2026-09-15 piece covers both cities in one story; do not let its second half
   into this file.
5. **Adjacent-county campuses are context, not entries.** Amazon in Union County, Meta in Licking
   County, AWS in Adams County, QTS in Van Wert County: none of them is in Allen County and none of
   them belongs here.

## 1 — The moratorium: Lima Ordinance 198-26 (2026-09-14)

**This is the newest instrument in the register and the most likely to be misread.** Read the two
limbs below before reading anything else in this file.

- **Instrument:** City of Lima Ordinance **198-26**, "AN ORDINANCE ENACTING AN EIGHTEEN-MONTH
  MORATORIUM ON THE ESTABLISHMENT, DEVELOPMENT, PROCESSING, REVIEW AND APPROVAL OF NEW STAND-ALONE
  DATA CENTER DEVELOPMENT WITHIN THE CITY OF LIMA AND ON NEW REQUESTS FOR CITY SUPPLIED WATER FOR
  DATA CENTER DEVELOPMENTS OUTSIDE THE CORPORATE LIMITS". `[verified]` — the ordinance's own title
  page, Lima City Council meeting packet 2026-09-14 p. 154. Committed at
  `data/extracted/lima/council/2026-09-14-ord-198-26-data-center-moratorium.resolution.yaml`.
- **Introduced:** **2026-09-14**, the regular council meeting at the Mercy Health–St. Rita's
  Graduate Medical Education Center auditorium, 751 W. Market St. `[verified]` (agenda p. 0).
  ⚠️ **Not 2026-09-15.** Every secondary source carries 09-15, which is the Tuesday the coverage was
  filed; the meeting was the Monday, and the agenda's own text layer says so.
- **Passage:** `[open]`. See "What is not established" below — this is not a quibble.

### The two limbs, which have different geographies

| | Limb 1 — development | Limb 2 — water |
|---|---|---|
| **What is paused** | Further processing of any application for building permits, certificates of occupancy, conditional use, zoning approvals, or any other administrative action or approval, for **standalone data-center development** | **New requests for City-supplied water** for data-center developments |
| **Where it reaches** | **Within the corporate limits of the City of Lima only** | **Outside the corporate limits** |
| **Why** | Zoning and permitting are the City's, and stop at its boundary | Lima's water main does not stop at its boundary; this limb governs Lima's own act as a supplier |

Both are `[verified]` to Section 1, packet p. 155.

⚠️ **THE SINGLE MOST IMPORTANT SENTENCE IN THIS FILE.** *The moratorium does not stop the campus in
§2, and it never purported to.* Two independent reasons, either of which alone is sufficient:

1. **The campus is in American Township, not in the City of Lima.** `[verified]` — the site
   construction plan reads "Site Construction Plan for Project Bosc 2026, American Township, Allen
   County" (`data/extracted/plans/4091286.engineering.yaml`,
   `data/extracted/permits/4074529.epa.yaml`), and the Roadwork Development Agreement's property
   clause reads "real property in American Township, Allen County (Exhibit A)"
   (`data/extracted/aedg/roadwork-development-agreement.rda.yaml`). Limb 1 stops at the corporate
   limits and therefore never reaches it.
2. **Limb 2 reaches only NEW requests, and Section 1's last sentence exempts existing contracts.**
   `[verified]` verbatim: "This ordinance shall be prospective in nature and shall not affect any
   preexisting contracts entered into prior to passage of this ordinance."

And the distinction that is easiest to collapse and must not be:

> ⚠️ **The ordinance names neither Google nor American Township.** Its carve-out is generic — "any
> preexisting contracts". The identification of *the Google water commitment* as one of those
> contracts is made in the **administration's transmittal memo** (packet p. 43), which is a request
> that legislation be drafted, not the legislation. Both facts are `[verified]`; they come from
> different documents doing different work. "The ordinance exempts Google" is a sentence no
> instrument in this corpus supports.

The memo's sentence, verbatim and `[verified]` to p. 43: *"This proposal would be prospective and
would not alter, reopen, or otherwise affect the City's existing commitment to provide water to the
Google data center currently under development in American Township."* Signed Sharetta T. Smith,
JD, MBA, Mayor and Mike Caprella, Utilities Director, dated 2026-09-08.

### The clock and the early exit are two different facts

- **Duration:** eighteen months. `[verified]` Section 1.
- **Runs from:** "the date of passage of this ordinance" — a **passage-relative** clock. The
  instrument names no start date and no end date. `[verified]` Section 1.
- **Ends on the earlier of** `[verified]`:
  1. *the early exit* — "the effective date of an ordinance regulating or prohibiting new standalone
     data centers within the City of Lima, Ohio, or new requests for City-supplied water for data
     center developments outside the corporate limits of the City"; or
  2. *the outer limit* — "eighteen-months from the date of passage of this ordinance".
- **End date:** `[open]`, and **uncomputable from the instrument** — both branches run from a
  passage date this record does not have. No end date is stated anywhere in this file for that
  reason.
- Note the early exit tracks **both** limbs. On this text, standards for the city-limits limb alone
  would not end the water limb.

### What the ordinance does not do

- `[verified]` **It imposes no standard.** It pauses processing. It sets no water, discharge, noise,
  height, setback, lighting, generator or load condition. The standards are the *work the pause was
  bought to allow*, and they do not exist yet. The memo lists what the administration will study
  (p. 44): locations, land use, setbacks, buffering, water and wastewater capacity, electric demand,
  noise, environmental impacts, traffic and infrastructure, developer responsibility for
  infrastructure costs, fiscal return, workforce development, local contracting, community benefits,
  and public-engagement requirements. Nothing on that list is law today.
- `[verified]` **It sets no gallonage threshold.** Limb 2 reaches new requests for City water at any
  volume.
- `[open]` **"Standalone" is not defined.** The preamble defines "data center" at length and never
  defines "standalone"; the title hyphenates it and Section 1 does not. Whether a data center
  ancillary to another principal use falls inside the moratorium is not settled by this text.
- `[open]` **"New requests" is not defined either.** Whether a request pending on the date of
  passage is "new" is unanswered; the preexisting-contracts sentence addresses *contracts*.

### What the council put on the record as its reasons

`[verified]`, preamble p. 154 — the recitals are a water argument followed by a jurisdiction
argument:

- *"WHEREAS, some data centers use millions of gallons of fresh water per day for cooling"* — note
  this is generic ("some data centers") and asserts nothing about any Lima project.
- *"WHEREAS, the City of Lima remains confident in its ability to meet the commitments of now
  existing agreements for providing water for data centers"* — the very next recital says the City's
  capacity is not the problem.
- *"WHEREAS, a data center seeking to locate within Lima's corporate limits would require a much
  broader level of municipal review than a development located outside the City for which Lima's
  role is primarily that of a utility provider"* — the ordinance's own explanation for why its two
  limbs have different geographies.

The memo is blunter, `[verified]` p. 44: *"This proposed moratorium is not about a lack of water
capacity. Lima's water system remains one of our greatest economic development assets."* The
administration's own system figures, as stated on that page and transcribed not derived: five
upground reservoirs holding **approximately 15 billion gallons**; treatment capacity
**approximately 30 MGD**; 2025 average production **13.7 MGD**; 2025 maximum daily production
**17.4 MGD**.

### What is not established, and why it matters

⚠️ **The passage record does not exist in public yet.** `[verified]` as a negative:

- What the corpus holds is the ordinance **as introduced**, published 2026-09-10 — four days before
  the meeting. It prints "Passed: \_\_\_\_, 2026" over Jamie L. Dixon, President and "Approved:
  \_\_\_\_, 2026" over Sharetta T. Smith, Mayor, and its vote grid (columns VOTE / 1ST / 2ND / 3RD,
  each split Y|N, over rows GORDON, WILKERSON, LOWE, JORDAN, JONES, GLENN, NEEPER, DIXON) is
  entirely blank, as are the "Introduced by" and "Seconded by" lines.
- The City publishes **no Minutes document** for this meeting. PrimeGov's
  `ListArchivedMeetings?year=2026` returns meeting 359 with exactly three documents — Agenda, Packet,
  HTML Packet, all published 2026-09-10. The 2026-08-17 special meeting *does* have minutes
  (published 2026-09-15), so the portal does carry minutes; these have simply not been approved and
  posted. An Ohio council approves minutes at a later meeting, so this is an expected lag, not a
  refusal.
- Therefore `[open]`: **the fact of passage, the vote tally, the mover and seconder, the reading at
  which it passed, the effective date, and the end of the eighteen-month clock.**
- Secondary coverage reports that Council approved it. That is `[reference]` and is not promoted
  here. None of the four sources carries a numeric tally either, so there is not even a press figure
  to check against.
- **Emergency status is a trap.** The ordinance *declares itself* "a matter of administrative
  emergency" under City Charter §33 `[verified]` pp. 155-156 — but §33's clause is **cascading**: it
  permits immediate effect on a two-thirds vote *at first reading* and falls through to second and
  third readings if that vote is not there. "Declared an emergency in the text" and "passed as an
  emergency" are different claims and only the first is established. The same clause appears on the
  other ordinances in the same packet (196-26 at p. 149, 197-26 at p. 151), so it is Lima's standard
  form and is not evidence of unusual urgency. Recorded because the opposite reading is available
  and wrong.
- `[verified]` **A documented divergence, recorded without characterizing it.** The Mayor's and
  Utilities Director's own memo asked that the legislation "Proceed through the normal legislative
  process and not as an emergency measure" (p. 44). The drafted ordinance declares itself an
  administrative emergency. Given the pro-forma finding above, whether that was a deliberate
  departure or the Law Department's boilerplate is `[open]`.

### Acquisition route (recorded because it changed)

`[verified]`. The City of Lima's CivicPlus Agenda Center — the route behind all 50 documents in
`data/extracted/lima/meetings/meeting-index.yaml` — **stopped publishing City Council documents on
2024-05-06**. `POST /AgendaCenter/UpdateCategoryList` with `catID=1` offers no year later than 2024,
and the city labels that page "Archived Meeting Agendas & Minutes (Prior to May 2024)". The live
route is a different vendor, **PrimeGov** (`limaoh.primegov.com`), embedded on
`limaohio.gov/887/Agendas-Minutes`. The seven-month gap in the meeting shelf was never a stale
shelf; it was an **unmonitored route change**. Documents and route are recorded at
`data/documents/lima/council/README.md` and `filename-map.yaml`.

## 2 — Bistrozzi LLC data center ("Project BOSC"), American Township

The one confirmed data-center campus in Allen County. Every figure below **belongs to a committed
extraction**, named inline; this section repeats, it does not re-derive.

- **Developer of record:** **Google**. `[verified]` — Select-Committee record (#234). The deed fixes
  the builder, not the occupant.
- **Entity of record:** **Bistrozzi LLC**, 1700 K Street NW, Fifth Floor, Washington, DC 20006-3817;
  contact Michael Montfort. `[verified]` — the issued air PTI's own applicant block,
  `data/extracted/permits/4132514.epa.yaml`.
- **Codename:** "Project BOSC". `[verified]` that the instruments print it — the PTI's project name
  is "Bistrozzi LLC Data Center (Project BOSC) - Initial Installation". See the guardrail above
  before using the string for anything.
- **Site:** N. Cole Rd. and W. Bluelick Rd.; mailing address 4110 N. Cole St., Lima, OH 45801;
  **American Township, Allen County**. `[verified]` — PTI site address; construction plan and RDA
  for the township.
- **Status:** construction. `[verified]` — air-permit-grounded; `SiteProfile.facilities[0].status`.
- **End use:** `[open]` — **deliberately**. Which workload class the campus is, and who may use it,
  is the unresolved question the end-use explorer turns on. It is not an omission and must not be
  filled from a press characterization.

### Load and backup generation

⚠️ **Do not multiply these out.** The profile transcribes the total the record states; deriving it
would restate the headline as 313.5 and contradict the permit extraction, the essay and the docs.

- **Emergency generators: 115** (P001–P115) — **114 data-hall gensets + 1 HUBGEN**. `[verified]`
  final PTI. The two counts you will see in the wild are both real and describe different things;
  the **114** is the hall count and is the basis of the backup total.
- **Per-engine rating: 2.75 MW (~2,750 ekW).** `[verified: draft only]` — the rating is on the draft
  public notice (eDocs 3987141/3987144) and is **CBI-redacted in the issued permit** under an Ohio
  EPA trade-secret grant (OAC 3745-49-03, 2025-10-08;
  `data/extracted/permits/3859883.epa.yaml`). The redaction is what the whole load report rests on.
- **Backup total: ~313 MW.** `[verified]` **as transcribed**, with the `~` carried as data — not as
  a product of 114 × 2.75.
- **IT load: ~275 MW** (range 250–300 MW). ⚠️ `[inference]` — the N+1 midpoint reasoned from the
  disclosed backup total. **It is not a permit disclosure.** Any register, chart or sentence that
  presents 275 MW as a disclosed figure is wrong.
- **Cooling towers: 36** (P120–P155). `[verified]` final PTI.
- **Campus layout:** three generator groups of 38 (GEN 1/2/3) and three cooling-tower groups of 12
  (TWR 1/2/3) — the emission-unit grouping corroborates a **three-data-hall** campus. `[verified]`.

### Air permit

- **OEPA Air PTI P0138965**, Facility 0302022054, **issued 2026-05-28** (Initial Installation).
  `[verified]` — `data/extracted/permits/4132514.epa.yaml`, a manual review of the full 66-page
  final permit. Permit fee $71,755.
- **Synthetic minor** to avoid major New Source Review, on federally enforceable caps: **NOx 235.62
  tpy, CO 96.06 tpy**. `[verified]`. PTE basis is 500 hr/yr per engine.
- **Title V: major source** — an operating-permit application is due within 12 months of commencing
  operation (Response 40). `[verified]`. A synthetic-minor NSR posture and a major Title V source
  are not in tension; they are different programs.
- Cooling-tower limits: 0.11 tpy PM10 and 0.04 tpy PM2.5 per unit (~4.0 and ~1.4 tpy combined),
  drift loss max 0.001%. `[verified]`.
- Fuel: ULSD or renewable diesel (HVO), 15 ppm S max. `[verified]`. 64 responses to comments.

### Financial / tax instruments

- **Allen County CRA No. 1** — boundaries established in **American Township and Sugar Creek
  Township** by Resolution **#304-25** (2025-04-17). `[verified]` — county minutes.
- **CRA Agreement with Bistrozzi LLC** — Resolution **#548-25** (2025-07-10, mover Seibert,
  unanimous). **75% real-property abatement, 15 years per Building.** `[verified]` —
  `data/extracted/legal/prr-mandamus/cra-agreement.cra.yaml`. Real property only; the project total
  may exceed 15 years across phases, but no single Building does. Agreement terminates Dec 31 of the
  later of 2055 or the year after the last Exemption (§21).
- ⚠️ **Elida School District PILOT — $250,000/yr, and this figure is a PROPOSAL, not a term.**
  `[verified]` that the amount was *proposed*: PAAC board minutes record "an additional compensation
  agreement in the amount of $200,000 per year" (2025-02-27 p. 35), restated as a "School District
  PILOT … annual payment in the amount of $250,000/year to the Elida School District" (2025-03-27
  p. 38; 2025-05-01 p. 43) — `data/extracted/aedg/paac-board-minutes.minutes.yaml`. **The EXECUTED
  amount is `[open]`**: the CRA agreement and the school-district notices withhold the school
  compensation as non-public. So $250,000/yr is the best figure the public record contains and it is
  a negotiating figure that moved once already ($200K → $250K). Do not present it as the agreed
  payment.
- **Roadwork Development Agreement — Resolution #588-25**; Company Contribution **$14.5M**,
  cost basis the Tetra Tech OPC. `[verified]` —
  `data/extracted/aedg/roadwork-development-agreement.rda.yaml`. The OPC's own construction total is
  **$14,223,081** (`data/extracted/aedg/roundabouts.summary.opc.yaml`, conceptual basis
  2025-07-11, 25% contingency-and-inflation), so the $14.5M Contribution ≈ that total plus ~$277K of
  admin/legal headroom. ⚠️ Exhibit D prints the estimate as "$14,500.00" — a **source typo** for
  $14,500,000.00, preserved not corrected.
- ⚠️ **§5.5 Overpayment Amount: the private contribution is refundable from public grants.**
  `[verified]` the mechanism; `[inference]` its effect — Roadwork Development (629) and ODOD Jobs &
  Commerce grants awarded for the same work are refunded to the Company, so the headline "$14.5M
  private contribution" may be net-reduced by public money. This is the single most under-reported
  term in the financial record.
- **Investment:** `[reference]` only. ~$500M Phase-1 and a $1.5B three-phase figure both circulate;
  **no instrument in this corpus states a capital figure**, and neither is promoted.
- **Jobs: ~50.** `[verified]` — the CRA agreement's own term is "approximately fifty (50) permanent,
  full-time" by ~2030-12-31, against **0 current employees**
  (`data/extracted/legal/prr-mandamus/cra-agreement.cra.yaml`). The `~` is the instrument's own and
  is carried as data. ⚠️ The agreement lets those jobs be employed by **the Company *or its
  Affiliates*** (the common-control group), so "50 jobs at this campus" is not what the term
  guarantees.

### Water / hydrology hook

- **Cooling-water source: the City of Lima's municipal system** — city-reservoir water. `[reference]`
  (Lima News, 2026-07-30, via `data/extracted/limaohio/lima-news-construction-wave.news.yaml`). A
  City of Lima / Allen County Water District water-service agreement for the campus was recorded as
  "underway" at PAAC 2025-05-01 p. 43 `[verified]` that it was underway. ⚠️ **The executed
  water-service agreement itself is `[open]` — it is not in this corpus.** That is the instrument
  Ordinance 198-26's preexisting-contracts sentence turns on, and it is priority 1 below.
- **Consumptive cooling draw: 3.1–3.84 MGD.** `[inference: derived]` — `docs/COURSE.md` §11 and
  `watermark.hydrology.cooling.derive_cooling_basis`, by two independent cited methods: top-down
  power × WUE (~275 MW IT × ~1.8 L/kWh evaporative → ~3.1 MGD) and bottom-up blowdown × cycles (the
  documented 2.5 MGD FM-2 discharge at ~5 cycles). The bottom-up raw figure implies ~5.7 L/kWh,
  unreachable for cooling, so it is capped at the physical evaporative-WUE ceiling. **Neither input
  is a disclosure**: cooling-system flowrates are CBI-withheld, and the evaporative archetype itself
  is an assumption grounded on the 36 cooling towers.
- **Wastewater — NPDES `2DP00130*AP`**, applicant BISTROZZI LLC, an **indirect discharge to a POTW**,
  not a direct surface-water discharge. Discharge address: American Bath WWTP, 3226 N. Cole Street.
  Outfall 2DP00130001. Public notice 2026-07-01; permit expires 2028-12-31. `[verified]` —
  `data/extracted/oepa/2DP00130.npdes.yaml`. Described as a data center discharging domestic waste
  and non-contact cooling water.
- **Sanitary redesign (2026-07-30):** Resolution **#582-26**, a Second Amendment to the Sanitary
  Sewer Development Agreement, is on the agenda `[verified]`. The news-reported content of that
  amendment — an $8M change order on a ~$31M contract, the pump station relocated to N. Cole &
  Beery, dual 8"/16" force mains, up to 500,000 gpd split between American Bath and American #2 with
  **excess diverted to the City of Lima WWTP**, a 2.5 MGD "worst day" promised capacity, and cooling
  cycled "three to six times" — is `[reference]` and **that Res. #582-26 is that instrument is an
  `[inference]`** (same meeting, subject and official). ⚠️ The 3–6× cycles-of-concentration figure is
  the County Sanitary Engineer's own self-report; do not upgrade it and do not feed it to a cooling
  classifier.

### Hydrology screen

- **Receiving water (indirect):** American Bath WWTP → **Pike Run**; the campus's consumptive loss
  is taken from the Ottawa/Auglaize supply the plants discharge back to.
- **Ottawa River mainstem 7Q10 = 0.2 cfs; 1Q10 = 0 cfs.** `[verified]` — cited from Lima Refining
  fact sheet 2IG00001 / USGS 04187100, in `data/reference/hydrology/low-flow-7q10.yaml` (and its
  `low-flow-7q10.derived.yaml` peer). The river
  nearly dries at design low flow, heavily abstracted upstream for Lima's own supply.
- **Net basin loss at buildout ≈ 4.85 cfs ≈ 24× the Ottawa 7Q10**, upper bound ~30×.
  `[inference: derived]` from the cooling basis above. This is the register's headline number and it
  is an inference resting on an assumption-tagged archetype — it is robust to the *low* end of the
  cooling range, which is why it survives, not because any of its inputs is disclosed.
- **Assimilative screen, county plants:** American Bath → Pike Run **0.01:1** dilution; American II →
  Dug Run **0.42:1**; Shawnee II → Ottawa mainstem **0.04:1**. All three `violation`. `[verified]`
  from the Ohio EPA fact sheets in the corpus.
- **Groundwater:** `[verified]` PAAC 2026-03-30 p. 76 — the campus prompted "area well concerns";
  Google issued its first public update ~3 years into the project and a well-issue contact email was
  set up. Residents on private wells beside a high-consumption cooling load is the live
  assimilative-capacity question, and no drawdown instrument exists. Magnitude `[open]`.

### Corporate structure

- **Bistrozzi LLC** is the permit applicant and CRA counterparty of record. `[verified]`.
- **Bistrozzi Addition** (Ziance / CT Corporation), and **Magenta Capital** and **Tilted Gate** (both
  Montfort / CSC / Delaware) appear in the SOS record. The link from the nominee LLCs to the
  operator rests on the **documented Montfort bridge** and is `[inference]`, not a finding. Do not
  merge these entities in the graph on the codename.
- ⚠️ **Executive-session shield in active use:** PAAC entered executive session citing
  R.C. 4582.58(B), the economic-development trade-secret shield, on 2026-03-30 p. 78. `[verified]`.

## 3 — No other data-center activity found

Each negative is a check that was run, not an absence of curiosity.

- **RSEI county inventory:** `data/reference/rsei/inventory.yaml` holds **49 facilities** for Allen
  County (FIPS 39003) and **none carries NAICS 518210** (data processing, hosting and related
  services). The NAICS actually present are refining, chemicals, fabricated metal and motor-vehicle
  codes — Lima's existing industrial base. `[verified]`, and checkable by re-reading that file.
  ⚠️ Note the limit of this check: RSEI is a *toxic-release* inventory, so it would not list a data
  center that reports no TRI chemical in any case. It is a negative about the toxics record, not
  about the existence of a facility.
- **NPDES record:** the committed Maumee basin inventory
  (`data/reference/echo/maumee-wwtp.all-npdes.yaml`) holds **443 Allen County rows**, and none is
  described as a data center. `2DP00130` is the only data-center-type permit in the Allen County
  record, and it is the campus in §2. `[verified]`.
- **Web sweep:** no council or trustee resolution, and no trade-press coverage, naming a second
  Allen County data-center project. `[verified]` as a dated negative for 2026-09-16. ⚠️ A negative
  web sweep is the weakest check here: an early-stage project under an NDA is exactly what does not
  surface this way, and Lima's own record shows a codename phase running for years before a name
  appeared. Read it as "nothing has surfaced", not as "nothing exists".
- ⚠️ **The guardrail catch — Amazon in Allen County is a WAREHOUSE.** Amazon.com Services LLC is
  building at **Jay Begg Parkway, Shawnee Township** (Gateway Shawnee, tied to VanTrust / VTRE
  Development LLC; PAAC codenames "Project Last Mile" / "Project Sloane" / "Project Amazon").
  `[verified]` — the recorded deed, `data/extracted/recorder/202511180011830-amazon-deed.deed.yaml`.
  It is a **distribution / delivery station**, the general logistics entity **Amazon.com Services
  LLC** and *not* Amazon Data Services. Recorded as an explicit non-entry so the next sweep does not
  re-chase it.

## Instruments to pull (priority order)

1. **The executed City of Lima water-service agreement for the campus** — `[open]`, and the single
   largest hole in the record. Ordinance 198-26's preexisting-contracts sentence turns on it, the
   Mayor's memo characterizes it, and this corpus does not hold it. PAAC recorded it as "underway"
   2025-05-01. Route: R.C. 149.43 to the Lima Clerk of Council / Utilities.
2. **Ordinance 198-26 as passed, certified, with the roll call and the journal entry** — `[open]`.
   The eighteen-month clock cannot be computed without a passage date. Drafted at
   `data/extracted/lima/council/2026-09-16-lima-clerk-of-council.records-request.md`; the cheap
   alternative is to re-pull PrimeGov meeting 359 once minutes post.
3. **Resolution #582-26, the Second Amendment to the Sanitary Sewer Development Agreement** —
   the text, plus the vote. It would convert the whole 2026-07-30 sewer-redesign paragraph from
   `[reference]` to `[verified]` and settle whether excess really routes to the City of Lima WWTP.
4. **The standards ordinance the moratorium was bought to produce** — does not exist yet. Watch for
   it: its effective date is branch (1) of the early exit, and its content is the actual regulatory
   outcome of this whole episode.
5. **The draft air PTI public-notice documents (eDocs 3987141 / 3987144)** as committed artifacts —
   they carry the ~2,750 ekW per-engine rating that the issued permit redacts, and the entire load
   figure depends on them.

## Open questions

- `[open]` End use / workload class of the campus, and who may use it.
- `[open]` Passage, tally, sponsor, reading and effective date of Ordinance 198-26.
- `[open]` Whether "standalone" excludes an ancillary data center, and whether a pending request is
  a "new request".
- `[open]` Actual campus water withdrawal as metered — every draw figure here is derived.
- `[open]` Magnitude of residential well drawdown near the campus.
- `[open]` Capital investment: no instrument states one.

## Sources

Primary instruments are cited inline to their committed extraction. Secondary sources, `[reference]`
only, used as leads and never as findings:

- `https://limaoh.primegov.com/public/portal` — City of Lima PrimeGov agenda portal; meeting 359
  (2026-09-14) agenda and packet. **Primary**, committed at `data/documents/lima/council/`.
- `https://www.limaohio.gov/887/Agendas-Minutes` — the city page that embeds the above and labels
  the CivicPlus Agenda Center as the pre-May-2024 archive.
- limaohio.com, "Lima council passes 18-month data center moratorium", 2026-09-15 — `[reference]`.
- hometownstations.com / 13abc, "Lima puts pause on future data center projects as city evaluates
  standards", 2026-09-15 — `[reference]`.
- toledoblade.com, "Lima, Pioneer latest communities to pass data center moratoriums", 2026-09-15 —
  `[reference]`. Covers Pioneer (Williams County) in the same story; see guardrail 4.
- govtech.com, "Lima, Ohio, Passes 18-Month Data Center Moratorium" — `[reference]`.
