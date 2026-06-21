# Research run: onboard springfield (Springfield): data-center activity + receiving-water screen for a new watershed-point site

- model: `claude-opus-4-8`
- generated: 2026-06-21T23:39:44+00:00
- turns: 13 (cap 30); cost: $0.5274
- tools: ToolSearch, mcp__bosc__list_documents, mcp__bosc__list_extractions, mcp__bosc__program_overview, mcp__bosc__entities, mcp__bosc__timeline, Grep, mcp__bosc__hydrology_balance, mcp__bosc__hydrology_scenario, AskUserQuestion
- proposals: 5 (see `manifest.yaml`)

---

I'll proceed with the corpus-only findings report (the faithful scope for read-only BOSC tools), and carry the Springfield disambiguation forward as the lead open question rather than guess at external data.

---

# Findings — Onboarding screen: "Springfield" as a BOSC watershed-point site

**Task:** assess data-center activity + a receiving-water screen for a candidate new site, "Springfield," over the BOSC corpus.
**Tools used (read-only):** `list_documents`, `list_extractions`, `program_overview`, `entities`, `timeline`, `hydrology_balance`, `hydrology_scenario`; plus text search over the saved `list_documents` and `timeline` dumps. **Scope note:** the disambiguation question I raised (which Springfield) was not answered, so this pass is deliberately corpus-only and pulls no external data. That boundary is itself one of the findings.

## 1. The corpus contains zero Springfield records `[verified]`

A string search for `springfield` (case-insensitive) returns **no matches** in either the full `list_documents` inventory (1,485 lines) or the cross-document `timeline` (328 lines). The entity graph likewise contains no Springfield party, facility, government body, or receiving water. Every resolved entity, deed, NPDES permit, OPC estimate, and meeting in the corpus is **Lima / Allen County, Ohio** (the BOSC reference build).

This is a flat negative finding, not a hedge: **there is no Springfield evidence base in BOSC today.** Any "data-center activity" or "receiving-water" claim about Springfield cannot be sourced from this corpus, and I will not manufacture one.

## 2. The bound MCP tools cannot screen Springfield `[verified]`

The hydrology and entity tools take **no site parameter** — they read the active site's committed data, which is Lima:

- `hydrology_balance` returns only the three Lima loop WWTPs — Shawnee II → Ottawa River (4.64 cfs `[doc]`), American Bath → Pike Run (2.32 cfs `[doc]`), American II → Dug Run (1.86 cfs `[doc]`) — each flagged a low-flow assimilative **violation** against its cited 7Q10.
- `hydrology_scenario` returns only the Lima/BOSC campus draw (4.85 cfs net, =24.3× the cited Ottawa River 7Q10) `[doc]` / `[inference]` on the cooling knob.

Per `CLAUDE.md`, per-site values live on a `SiteProfile` in `bosc.sites`, selected by `BOSC_SITE`. The MCP server here is bound to `lima`. So a Springfield receiving-water screen is **not blocked by analysis — it's blocked by the absence of a registered Springfield profile and its committed reference data.** This matches the documented onboarding model (`bosc onboard <slug>` → scaffold per-site dirs, run portable connectors, emit a blocking review checklist).

## 3. Watershed fit is the lead open question `[open]`

"Springfield" is ambiguous and the candidates fall in **different river basins**, which is decisive for a network whose axis is *Maumee watershed points*:

- **Springfield, Clark County OH** (the well-known city) drains to the **Mad River → Great Miami → Ohio River** — **outside the Maumee basin.** If this is the target, the site fails the network's stated watershed-axis premise and that mismatch should be resolved *before* any connector work. `[inference — basin assignment is standard hydrography; confirm against NHD before relying on it]`
- **Springfield Township, Lucas County OH** (NW of Toledo) sits in the **Maumee/Ottawa-Lucas** drainage — a clean watershed fit.
- Other Springfields (Summit County OH; out-of-state) do not fit the Maumee axis.

This is the same class of trap recorded in prior onboarding work — *same-name place, wrong basin/state* (cf. the "Williams County" ArcGIS that was North Dakota; the cross-state connector leaks surfaced only by non-Ohio sites). **Resolve the identity and basin from a live hydrography/parcel sample before wiring anything.**

## 4. What an onboarding pass must produce (Lima as the reference template)

The Lima build shows the two layers this task names, and what "done" looks like for each:

**Receiving-water screen** — needs, per WWTP/outfall: cited permitted design flow, the receiving stream, and the stream's **7Q10** low flow, then the dilution ratio (Lima's are all <1:1 → effluent-dominated). Source path: OEPA NPDES permits/fact sheets (corpus has `oepa/oepa-2P*…npdes.yaml`) + USGS NWIS / Ohio low-flow records. None of this exists for Springfield.

**Data-center activity layer** — Lima's is built from recorder deeds (land assembly to `Bistrozzi`/`Amazon`/`Bistrozzi Addition LLC`), SOS shell filings, EPA stormwater/air permits, township & commissioner minutes, and the air-permit power figure that drives the cooling-draw scenario. Springfield has **none** of these ingested.

## 5. Actionable follow-ups (track as issues)

1. **Disambiguate "Springfield" + confirm basin** before any work. Deliverable: a one-line situs (city/township, county, state) verified against a live NHD/parcel sample, and an explicit Maumee-fit yes/no. *(Blocks everything below.)*
2. **Register a `SiteProfile`** in `bosc.sites.SITES` for the confirmed Springfield (GIS URLs, `nwis_sites`, `rsei_fips`, `eia861_utility_number`) — never reuse Lima/Allen values. Re-scan grid/economics connectors for Ohio-hardcoding if non-OH (cross-state-leak pattern).
3. **EIA-861 lookup:** if Springfield's utility is municipal, expect EIA-861S (Short_Form sheet), not full Sales — record the utility number.
4. **Receiving-water reference dataset:** pull the Springfield WWTP NPDES permit(s) + receiving stream 7Q10 into `data/reference/` so `hydrology_balance` has cited inputs.
5. **Data-center activity scan:** open-records/parcel sweep for any data-center land assembly, rezoning, or utility-tap activity near Springfield; ingest deeds/SOS/permits if found, or record a flat **no-activity** finding if not.
6. **Network-scope decision (if Clark County):** escalate the watershed-axis mismatch to the network design owner (cf. epics #308/#323) — a Great-Miami site may not belong in a Maumee network without a stated scope change.

**Bottom line:** there is nothing in the BOSC corpus on Springfield, and the bound tools are Lima-only by design; this is a clean greenfield onboarding, gated first on confirming *which* Springfield and whether it even sits in the network's watershed. If you want, name the specific Springfield and authorize a live web/connector pass and I'll seed the onboarding file.
