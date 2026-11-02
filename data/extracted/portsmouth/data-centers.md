# Portsmouth / Scioto Co., OH — Data-Center Activity Register

Discover-and-pin register for the Portsmouth watershed point (Ohio River below the Scioto
confluence). Status **as of 2026-11-02** (#484). Tags are BOSC evidentiary discipline:
`[verified]` = cited primary/government source, `[reference]` = secondary source or a party's own
self-report (leads only, never a finding), `[inference]` = arithmetic or pattern from cited inputs,
`[open]` = not found in any public source yet. Unlike most tracking-site registers, **this one rests
partly on instruments the corpus already holds**: the Project Dazzler permit file under
`data/documents/permits/dazzler-permits/` (extracted to `data/extracted/permits/dazzler-permits/`)
and the Tilted Gate LLC SOS registration. Everything else is cited by URL. Nothing here is
fabricated; every figure is cited or marked `[open]`.

**The finding is a permitted-in-progress campus with a Google contact on the filing, not a Google
instrument.** The applicant on every permit document is Tilted Gate LLC. A Google email address
appears on one of them. No instrument the corpus holds names Google as owner, tenant or party.

## Disambiguation guardrail — run first, always

- **"Portsmouth" in "PORTS" is not this site.** The DOE Portsmouth Gaseous Diffusion Plant
  ("PORTS"), and the SB Energy "PORTS Technology Campus" and its FAST-41 entry (whose dashboard
  slug is `portsmouth-data-center`), are in **Pike County**, at Piketon. They belong in
  `data/extracted/piketon/data-centers.md`, not here. `[verified]` — the Permitting Council release
  places that project in Pike County.
- **Project Dazzler is in Green Township, Scioto County**: "West of U.S. Route 52, east of the Ohio
  River, south of County Road 7 (Jr. Furnace Powellsville Road), Green Township, Scioto County,
  Ohio" (`data/extracted/permits/dazzler-permits/4071697.epa.yaml`), at about 38.6067, −82.8392 in
  the USACE public notice (`4081910.epa.yaml`). Its mailing address is Franklin Furnace (45629),
  not the City of Portsmouth. `[verified]`
- **"Green Township" is ambiguous statewide.** Clark County has one (the Springfield register's
  Peacock Rd rezoning). Scioto's is the only one in this register.
- **Tilted Gate is a sibling shell of the Lima Bistrozzi cluster, not evidence about Lima.** It
  shares the registered agent (CSC), the organizer (Michael Montfort) and the engineer (EMH&T) with
  the Lima-side entities (`docs/DOSSIER.md` §8). A shared fingerprint is an `[inference]` about the
  network; it does not move any Lima claim, and no Lima claim moves it.

## 1 — Tilted Gate LLC / "Project Dazzler" (Green Twp, Scioto Co.)

- **Applicant:** Tilted Gate LLC, a Delaware LLC registered in Ohio as a foreign LLC on 2025-09-29
  (filing 202527204518; agent Corporation Service Company; organizer and manager Michael
  Montfort). `[verified]` — `data/extracted/permits/sos-tilted-gate-llc-2025-09-29.sos.yaml`.
- **Scale (as the applicant describes it):** "~792-acre data center campus (two buildings, ~1.7M
  sq ft)"; construction start 2026-07-01, end 2031-06-30 on the Ohio EPA form. `[verified]` as the
  applicant's own statement in its filings (`4081897.epa.yaml`, `4081890.epa.yaml`); the
  delineation study area is ~914 acres (`4071697.epa.yaml`, `4081903.epa.yaml`).
  - Press reports "about 500k sq ft" and $1B (WSAZ, 2026-01-22) `[reference]`. **The square
    footage conflicts with the application's 1.7M sq ft.** Prefer the filing.
- **Google link:** the Ohio EPA 401 application lists the applicant contact as "Randy Barrera
  (`randybarrera@google.com`), DC Project Lead" `[verified]` (`4081890.epa.yaml`). That Google is
  the end user is an `[inference]` from that address. Press names Google outright `[reference]`.
- **Power / MW:** `[open]`. No filing in the corpus states a load.

### Financial / tax instruments

- **Abatement:** Scioto County commissioners approved a 75% / 15-year abatement with a $500k/yr
  PILOT on 2026-01-22 `[reference]` (WSAZ). The CRA agreement and the commissioners' resolution
  are `[open]`, not yet pulled.
- **Litigation:** a suit alleges the CRA was created in an improper executive session
  `[reference]`. Court, case number and status are `[open]`.

### Water / hydrology hook

- **Max withdrawal / consumption:** `[open]`. No figure is disclosed in the filings held.
- **Water source:** `[open]`.
- **Wastewater:** `[open]`. Whether the campus would discharge to Portsmouth's Lawson Run WWTP
  (NPDES 0PD00013, 6.5 MGD average design flow, Ohio River —
  `data/extracted/oepa/portsmouth/0PD00013.npdes.yaml`) is not stated anywhere; that plant is
  context, not the campus's path.
- **Stormwater:** an NPDES construction general permit was "to be submitted 04/03/2026" per the
  401 form `[verified]` (`4081890.epa.yaml`). Coverage itself is `[open]`.
- **Aquatic resources:** USACE Huntington District's JD letter (2026-02-05, LRH-2025-00939-OHR)
  found 23.18 ac of 6 wetlands, 14,306 lf of 8 streams and a 6.52-ac open-water marina potentially
  jurisdictional `[verified]` (`4081903.epa.yaml`). The individual 404 public notice proposes fill
  of 3.12 ac of Wetland P, comment period to 2026-05-14, mitigated by in-lieu-fee credits (5.2 ac
  forested, 2.2 ac non-forested) `[verified]` (`4081910.epa.yaml`, `4081908.epa.yaml`). HUCs
  050901030106 (Ginat Creek) and 050901030107 (Grays Branch–Ohio River).

### Hydrology screen

`[open]`. With no disclosed draw, no screen against the Ohio River mainstem is run.

### Regulatory record (status as of 2026-11-02)

- USACE §404 individual permit (LRH-2025-00939-OHR): public notice issued; **decision `[open]`**.
- Ohio EPA 401 WQC + Level 3 Isolated Wetland Permit: applications filed (pre-application
  2025-12-05; IWP 2026-02-13; 401 2026-04-14) `[verified]`; **decisions `[open]`**. An Ohio EPA
  public hearing around 2026-05-07 is reported `[reference]`; the hearing notice is `[open]`.
- Air PTI for emergency generators: `[open]` — none found.

## Instruments to pull (priority order)

1. **USACE LRH-2025-00939-OHR decision** and the **Ohio EPA 401 / IWP decisions** — whether the
   fill is authorized.
2. **Scioto County CRA agreement and the 2026-01-22 commissioners' resolution** — the abatement
   terms, and the counterparty's name.
3. **The CRA lawsuit docket** — court, number, status.
4. **Recorder / auditor** — deed(s) into Tilted Gate LLC for the 792-ac assembly.
5. **Ohio EPA air PTI search** for the Franklin Furnace address.

## Sources

- `data/extracted/permits/dazzler-permits/` — ten extractions of the Project Dazzler 404 / 401 /
  JD / mitigation file (sources under `data/documents/permits/dazzler-permits/`).
- `data/extracted/permits/sos-tilted-gate-llc-2025-09-29.sos.yaml` — Ohio SOS foreign-LLC
  registration.
- `docs/DOSSIER.md` §8 — the Tilted Gate thread.
- <https://www.wsaz.com/2026/01/22/googles-request-tax-abatement-proposed-data-center-approved> —
  abatement approval `[reference]`.
