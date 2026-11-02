# Ashville / Pickaway Co., OH — Data-Center Activity Register

Discover-and-pin register for the Ashville watershed point (Walnut Creek → Scioto). Status **as of
2026-11-02** (#2209). Tags are BOSC evidentiary discipline: `[verified]` = cited primary/government
source, `[reference]` = secondary source or a party's own self-report (leads only, never a
finding), `[inference]` = arithmetic or pattern from cited inputs, `[open]` = not found in any
public source yet. **Nothing here is in the BOSC corpus yet**; this records the public record and
the primary instruments to *pull*. Nothing here is fabricated; every figure is cited or marked
`[open]`.

**The finding is a contested village agreement, not a campus.** The Village approved a preliminary
agreement with EdgeConneX by emergency resolution. The Ohio Supreme Court held the emergency clause
insufficient, so the resolution went to referendum on the 2026-11-03 ballot. Its generation plant
is before the Power Siting Board.

## Disambiguation guardrail — run first, always

- **Village of Ashville, Pickaway County (FIPS 39129).** Not Ashville, Alabama or New York, and not
  Asheville, North Carolina.
- **EdgeConneX and PowerConneX are the developer and its generation affiliate.** The OPSB applicant
  is "PowerConneX Inc." (developer page). The same applicant name is on the New Albany 3 case
  (OPSB 26-361-EL-BGN, Licking Co.), which belongs in the New Albany register, not here.
- **The site map point** in `data/sites.yaml` is the Census 2024 gazetteer centroid, not the
  project parcel.

## 1 — EdgeConneX / PowerConneX "Ashville Energy Center"

- **The village instrument:** Resolution No. 06-2026, adopted 2026-04-06, approving the
  preliminary agreement with EdgeConneX and declaring an emergency `[verified]` (as recited in the
  Supreme Court's opinion, below). The resolution itself is `[open]`, not pulled.
  - Press reports it also suspended a data-center moratorium the Village Council had passed in
    December 2025 `[reference]`
    (`data/extracted/legal/datacenter-legislation/local-ballot-2026-11.yaml`).
- **The project, per the press and the developer:** two data centers and an ~800 MW gas plant on
  ~195 ac of village property `[reference]`.
- **Generation siting: OPSB 26-196-EL-BGN** (written so by OPSB and the applicant; one source
  writes "26-0196"). Applicant "PowerConneX Inc."; "up to ~800 Megawatt"; ~110 ac in Pickaway
  County; filed 2026-05-12 `[reference]` (developer page). Local public hearing 2026-08-19, 5 pm,
  Teays Valley HS, per the OPSB notice as relayed by Farm and Dairy (2026-07-19) `[reference]`.
  An evidentiary hearing ran around 2026-09-09/10; OPSB reportedly denied PowerConneX's motion to
  strike intervenor expert testimony on 2026-09-09 `[reference]` (an intervenor's advisory).
  - **The 110 ac (plant) and 195 ac (whole deal) are not the same footprint**; they do not
    conflict.
  - **Docket status `[open]`.** The PUCO DIS docket was not reached (WAF refusal, 2026-11-02).
    One tracker lists the project "Canceled"; no source corroborates that, and the developer page
    lists no withdrawal. An Aug 10 PowerConneX filing names withdrawal only as a contingency for a
    financial pledge `[reference]`.

### The referendum

- ***State ex rel. McNamara-Smith v. Grube*, 2026-Ohio-3035** (No. 2026-0906, decided
  2026-08-07): 6–1, Brunner concurring in part and dissenting in part. The emergency clause on
  Resolution 06-2026 was insufficient; a peremptory writ was granted ordering the fiscal officer to
  submit the petition to the board of elections `[verified]` (slip opinion).
- The Pickaway County BOE found 669 valid signatures and voted unanimously on 2026-08-24 to place
  the referendum on the 2026-11-03 ballot `[reference]` (Circleville Herald). The BOE
  certification itself is `[open]`. The vote is on the resolution, not on a data center.
- Council was reported on 2026-09-04 to be weighing repeal of the deal `[reference]`; whether it
  did is `[open]`.

### Financial / tax instruments

`[open]` beyond the preliminary agreement. Its terms are not in hand.

### Water / hydrology hook

`[open]` — no water figure disclosed. A gas plant of ~800 MW raises its own cooling question,
separate from the data centers' `[inference]`.

### Hydrology screen

`[open]`.

### Regulatory record (status as of 2026-11-02)

- OPSB 26-196-EL-BGN: filed; hearings held; **decision and current status `[open]`**.
- Ohio EPA air PTI for the plant: `[open]`.
- Referendum: on the 2026-11-03 ballot `[reference]`; **result `[open]`**.

## Instruments to pull (priority order)

1. **OPSB DIS, case 26-196-EL-BGN** — the docket index, any withdrawal, any order.
2. **Resolution 06-2026, the December 2025 moratorium, and the preliminary agreement** — R.C.
   149.43 to the Village.
3. **The Pickaway BOE certification (2026-08-24) and the 2026-11-03 result.**
4. **Ohio EPA air PTI** for the Ashville Energy Center.

## Sources

- <https://www.supremecourt.ohio.gov/rod/docs/pdf/0/2026/2026-Ohio-3035.pdf> — slip opinion
  `[verified]`.
- <https://ohiocapitaljournal.com/2026/08/14/ohio-supreme-court-allows-ashville-referendum-against-data-center-project-to-move-forward/>
  `[reference]`.
- <https://www.circlevilleherald.com/community/pickaway-county-board-of-elections-votes-unanimously-to-put-the-ashville-referendum-on-the-ballot/article_baa1518a-0afa-4aa0-a339-547e0cdd2dde.html>
  `[reference]`.
- <https://www.edgeconnex.com/ashville-oh-energy-center/> — developer page `[reference]`.
- `data/extracted/legal/datacenter-legislation/local-ballot-2026-11.yaml` — the Ashville ballot
  entry (written before this site was registered; its `bosc: site: null` predates #2209).
