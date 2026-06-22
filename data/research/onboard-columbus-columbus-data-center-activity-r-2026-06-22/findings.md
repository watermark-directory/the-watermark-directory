# Research run: onboard columbus (Columbus): data-center activity + receiving-water screen for a new watershed-point site

- model: `claude-opus-4-8`
- generated: 2026-06-22T17:31:17+00:00
- turns: 18 (cap 30); cost: $0.6977
- tools: ToolSearch, mcp__bosc__list_documents, mcp__bosc__list_extractions, mcp__bosc__program_overview, Grep, mcp__bosc__timeline, mcp__bosc__entities, mcp__bosc__hydrology_balance, mcp__bosc__hydrology_scenario, mcp__bosc__sanitary_basis, Read, mcp__bosc__read_extraction
- proposals: 5 (see `manifest.yaml`)

---

I now have a complete and clear picture. Let me give you the findings report.

---

# Findings — Onboarding Columbus (Scioto River basin) as a watershed-point site

## Bottom line up front

**`[verified]` The BOSC corpus presently holds no Columbus / Scioto-River-basin primary-source material of any kind, and the in-process receiving-water screen tools are hard-bound to the Lima reference build.** Onboarding Columbus is a net-new effort, not an extraction-from-existing-corpus effort. Two items in the corpus *look* like they might be Columbus data; both are something else, and conflating either with the Columbus target would be an error. The genuinely useful signal the corpus does carry for a Columbus onboarding is an **actor bridge**, not a place bridge.

---

## 1. What the evidence shows

### 1.1 No Columbus presence in any cross-document index `[verified]`

- **Entity graph (`entities`)** — every resolved party is Lima/Allen County (Bistrozzi cluster, Brenneman/Neff/Pieper grantors, the AEDG/Port Authority government bodies, the Lima RSEI industrial facilities). The only `water/receiving_water` entities are **Dug Run, Ottawa River, and Pike Run** — all Maumee-basin, Allen County. No Scioto, Olentangy, Big Walnut, Alum Creek, or Darby Creek receiving water exists in the graph.
- **Document list (`list_documents`, 1,485 lines)** and **timeline (`timeline`, 328 lines)** — keyword screen for `columbus | scioto | franklin | new albany | licking | olentangy | big walnut | alum creek | delaware co | hilliard | dublin | groveport` returns **no Columbus-area document**.
- **Extraction list (`list_extractions`)** — all 100+ artifacts live under Lima/Allen County collections (`aedg/`, `commissioners/`, `oepa/`, `recorder/`, `permits/`, `plans/`, `lacrpc/`, the township trees, `legal/`). None is Scioto-basin.

### 1.2 The receiving-water screen tools cannot screen Columbus today `[verified]`

`hydrology_balance`, `hydrology_scenario`, and `sanitary_basis` take **no site parameter** and return only Lima objects:

- `hydrology_balance` routes the three Allen County WWTPs to Ottawa River / Pike Run / Dug Run and screens each against that stream's cited 7Q10.
- `hydrology_scenario` compares the BOSC campus cooling draw to **the Ottawa River 7Q10 (0.2 cfs, document-cited)** — Ottawa is named in the output string.
- `sanitary_basis` returns the American/Shawnee permits (OH0037338, OH0023841, OH0023850).

These are the Lima reference implementation of the screen, not a Columbus capability. A Columbus screen requires its own profile and its own document-cited 7Q10 / WWTP design flows (see §3).

### 1.3 Two near-misses — explicitly *not* Columbus data

**(a) The "New Albany 100% tax abatement" line is a comparator quote, not coverage. `[reference]`**
In the Perry Township (Lima) minutes of 2024-06-18, a resident (Larry Sidener) cited "100% tax abatement … as what New Albany has," and Cindy Leis stated Allen County had agreed to no such thing (`perry-township/meetings/meeting-index.yaml`, via `timeline` line 38). This is a Lima meeting referencing New Albany as a benchmark. It is evidence about the *Lima* incentive debate, not about the Columbus/New Albany market.

**(b) "Project Dazzler" is in Scioto *County* (Ohio River), not the Scioto *River* basin at Columbus. `[verified]` — keep these threads separate.**
Permits `4071697.epa.yaml` and `4081896.epa.yaml` (and the related `4081896` family) document a USACE Section 404 / WOTUS jurisdictional-determination delineation for a ~914-acre data-center site:
- Site: *"West of U.S. Route 52, east of the Ohio River, south of County Road 7 (Jr. Furnace Powellsville Road), **Green Township, Scioto County, Ohio**"*
- Subbasins: **Ginat Creek (HUC 05090103-01-06) and Grays Branch–Ohio River (HUC 05090103-01-07)** — i.e. the **lower Ohio River** drainage near Portsmouth, ~120 miles south of Columbus. HUC 0509 is not the Scioto River (HUC 0506).

Scioto *County* shares only a name with the Scioto *River* basin. Folding Dazzler into a "Columbus" onboarding would cross two unrelated watersheds. **Dazzler is its own candidate watershed-point (Ohio River branch), and worth its own onboarding issue — but it is not Columbus.**

### 1.4 The real Columbus-relevant signal: an actor bridge, not a place bridge `[verified] / [inference]`

The Dazzler permits supply a *documented* connection between the existing corpus and the Columbus market:

- **`[verified]`** The Dazzler applicant is **Tilted Gate LLC** — the same Delaware-registered entity already in the corpus as an `epa_applicant ×10` in the Lima/BOSC corridor (organized by Michael Montfort, agent Corporation Service Company; `sos-tilted-gate-llc-2025-09-29.sos.yaml`, `entities`).
- **`[verified]`** The Dazzler engineer is **EMH&T**, whose letterhead address is **5500 New Albany Rd., Columbus, OH 43054** — the same firm that fronts the Lima/Bistrozzi cluster (`entities`: EMH&T `firm ×16`).
- **`[inference]`** That the same Columbus-based engineering firm (EMH&T) and the same shell applicant (Tilted Gate LLC) are running both the Lima corridor and a southern-Ohio Ohio-River site is a documented pattern of a single development apparatus operating across Ohio watersheds. Whether that apparatus has a *Columbus/Scioto-River* project is **`[open]`** — the corpus does not show one. EMH&T's New Albany address is an address on letterhead, not evidence of a Columbus data-center project in the record.

> No-link finding, stated flatly: **There is no documented data-center project, deed, NPDES permit, or receiving water in the Columbus / Scioto River basin anywhere in the current BOSC corpus.**

---

## 2. The receiving-water screen Columbus *would* run (reference, from Lima)

For methodology grounding — these are **Lima figures**, cited only to show the screen an onboarded Columbus profile would reproduce against Scioto-basin inputs. All are document-cited via `hydrology_balance` / `sanitary_basis` unless marked.

| WWTP (Lima ref.) | Permit | Discharge | Receiving water 7Q10 | Dilution | Result |
|---|---|---|---|---|---|
| Shawnee II | OH0023850 | 4.64 cfs | Ottawa R. 0.20 cfs | 0.04:1 | violation |
| American Bath | OH0023841 | 2.32 cfs | Pike Run 0.03 cfs | 0.01:1 | violation |
| American II | OH0037338 | 1.86 cfs | Dug Run 0.78 cfs | 0.42:1 | violation |

Campus consumptive-cooling stressor: **~4.85 cfs net basin loss = 24.3× the Ottawa 7Q10** (`hydrology_scenario`). Mark this as a **derived estimate `~`**, not a metered or permitted value — it is power-figure × water-use-efficiency, and `hydrology_balance` flags it as such ("~4.9 cfs central; 3.14–10 MGD evaporative … not a metered or permitted value"). Preserve the `~`.

The screen's whole point is the effluent-dominated, low-7Q10 receiving stream. **The onboarding question for Columbus is whether its candidate receiving waters behave the same way** — the Scioto and its tributaries are larger than Ottawa River, so a Columbus screen may *not* trip the same way, and that contrast is itself a finding worth producing.

---

## 3. Recommended follow-up investigations (track as issues)

**Onboarding mechanics**
1. **Register a `columbus` SiteProfile in `bosc.sites.SITES` + `frontend/src/lib/sites.ts`** (per CLAUDE.md: never re-hardcode a Lima value). Required per-site knobs: `nwis_sites` (Scioto-basin USGS gauges), `rsei_fips` (Franklin Co. 39049 + collar counties), `eia861_utility_number` (AEP Ohio / muni), GIS URLs (Franklin Co. auditor parcels; OGRIP). Then run `bosc onboard columbus`. Tracks to epic **#486**.
2. **Make the hydrology screen site-aware.** `hydrology_balance` / `scenario` / `sanitary_basis` are hard-bound to Ottawa/American/Shawnee. They must read `active_profile(settings)` so a Columbus 7Q10 + Columbus WWTP design flows can be screened. *This is a code gap, not a corpus gap, but it blocks the deliverable in the topic title.*

**Corpus gaps (net-new acquisition for Columbus)**
3. **Identify Columbus/Franklin-area data-center sites and pull the primary record** — Franklin/Licking/Delaware deeds, OEPA NPDES + isolated-wetland permits, USACE 404 JDs, and the receiving water for each. Cross-check whether **Tilted Gate LLC / EMH&T / Montfort / Vorys** recur (the §1.4 actor bridge gives a concrete name list to query against Ohio SOS and OEPA eDocs).
4. **Establish the candidate receiving waters and their 7Q10s** (Scioto, Olentangy, Big Walnut, Alum Creek, Darby Creek) from a document-cited source so the screen has Columbus inputs rather than Lima ones.

**Adjacent thread (do not merge into Columbus)**
5. **Open a separate "Project Dazzler / Ohio-River branch" issue.** Scioto County, HUC 05090103. Same Tilted Gate LLC applicant + EMH&T engineer as Lima — a strong candidate watershed-point in its own right, and a test of the cross-watershed actor pattern. Extraction targets already in corpus: `permits/4071697.epa.yaml`, `permits/4081896.epa.yaml` (and the `4081xxx` Dazzler family). Note both are *delineation reports*, not issued permits — `permit_no` is EMH&T internal `20250390`, so a follow-up should pull the actual USACE Huntington District action when issued.

**Unverified / open**
6. **`[open]`** Confirm or refute a Columbus/Scioto-River data-center project tied to the EMH&T–Tilted Gate apparatus. Currently absent from the record; should not be asserted until a primary instrument surfaces.

---

### Caveats on this report
- I read the `entities`, `program_overview`, `hydrology_*`, and `sanitary_basis` outputs in full, and the Dazzler extractions in full. The `list_documents` (1,485 lines) and `timeline` (328 lines) outputs I screened by keyword rather than reading end-to-end; the no-Columbus finding rests on that keyword screen plus the (fully read) entity graph, which is derived from the same extractions and corroborates it.
- Every Lima screen figure in §2 is document-cited per the tool provenance except the campus consumptive draw, which is a flagged **`~` derived estimate** and is labeled as such. No Columbus figures are stated because none exist in the corpus.
