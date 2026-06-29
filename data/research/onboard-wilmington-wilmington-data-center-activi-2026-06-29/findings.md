---
topic: onboard wilmington (Wilmington): data-center activity + receiving-water screen for a new watershed-point site
model: claude-opus-4-8
generated: 2026-06-29T06:49:06+00:00
turns: 33
turns_cap: 30
cost_usd: 1.1671
proposals: 5
tools:
  - ToolSearch
  - mcp__watermark__list_documents
  - mcp__watermark__list_extractions
  - mcp__watermark__entities
  - TaskCreate
  - mcp__watermark__read_extraction
  - mcp__watermark__hydrology_balance
  - TaskUpdate
  - mcp__watermark__retrieve_corpus
---

# Findings — Onboarding Wilmington (Clinton County, OH): Data-Center Activity + Receiving-Water Screen

## Scope and method

I worked the read-only BOSC tools against the live corpus: `entities`, `list_documents`/`list_extractions`, seven `read_extraction` pulls of the Wilmington-area OEPA permits, `hydrology_balance`, and four `retrieve_corpus` queries. The semantic index is **not built** (`retrieve_corpus` returned nothing even for a known-good Lima query), so corpus-wide *text* search was unavailable; the findings below rest on the **structured entity graph and the extraction set, which are built.** I note where that distinction matters.

**Threshold geography check (per the same-name-county discipline):** the corpus "Wilmington" is unambiguously **Wilmington, Ohio, 45177, Clinton County** — confirmed on every permit cover (`475 South Nelson Avenue`, `1142 Prairie Avenue`, `4425 State Route 730`, all Clinton County) and by receiving waters (Lytle Creek, Todd Fork, Wilson Creek). These are **Little Miami River basin** waters — a basin the network does not yet cover (current branches: Maumee, Great Miami, Scioto). [verified]

---

## 1. Data-center activity near Wilmington — *no documented activity in this corpus*

**There is no data-center, land-assembly, or hyperscale-utility signal tied to Wilmington or Clinton County anywhere in the current corpus.** [verified, as a statement about the corpus]

The entire data-center cluster in the entity graph — Bistrozzi and its shells (Bistrozzi Addition LLC, Tilted Gate LLC, Magenta Capital (Ohio) LLC), Amazon.com Services LLC, Google, Turner Construction, and the EMH&T/Vorys/WSGR professional ring — resolves to **Allen County** parcels and meeting bodies (American Township, Perry Township, LACRPC, the Port Authority). Every recorded deed in `recorder/` conveys Allen County land to Bistrozzi or Amazon. No Wilmington party, parcel, or meeting appears in that web. [verified — `entities` graph]

Two caveats on the strength of that null:

- It is a finding **about the corpus**, which is Allen-County-centric by construction. Absence here is weak evidence about the world.
- The semantic index being down means I could not run a full-text sweep for a stray mention. The structured graph is authoritative for *resolved entities*; it would not catch an un-extracted prose reference.

**The real-world question — is there an actual data-center proposal at/near Wilmington? — is [open] and requires external verification**, not corpus inference. The natural triggers to check: JobsOhio/Clinton County economic-development announcements, the former Wilmington Air Park (the ex-DHL/ABX hub, an obvious large-load redevelopment candidate), OEPA new-source air or NPDES filings, and AEP Ohio/utility interconnection or substation filings. None of that is in the corpus today.

**Why Wilmington permits were already pulled, then, is itself unresolved.** Seven OEPA permits sit under `data/documents/oepa/wilmington/` with clean extractions, but there is no Wilmington `SiteProfile`, no site footprint artifact, and no leads file — i.e. the *receiving-water inventory got scaffolded ahead of any documented load driver.* That ordering should be reconciled before promoting the site (see follow-ups).

---

## 2. Receiving-water inventory — built; the assimilative screen itself — *not runnable yet*

### What is documented (high confidence — permit covers, image-verified, `confidence: high`)

Wilmington-proper dischargers (`source_path …/oepa/wilmington/`):

| Permit | Facility | Receiving water | Action / dates |
|---|---|---|---|
| `1PD00013*QD` | **City of Wilmington WWTP** (the municipal plant) | **Lytle Creek** | modification, eff. 2023-07-01, exp. 2026-09-30 |
| `1II00129*HD` | Wilmington Sanitary Landfill (City-operated) | Lytle Creek **at RM 6.5** | modification, eff. 2025-05-01, exp. 2028-09-30 |
| `1IW00240*ID` | Wilmington Water Plant | Unnamed Tributary of Lytle Creek | renewal, eff. 2023-07-01, exp. 2028-06-30 |
| `1PV00089*DD` | Pine Hills Mobile Home Park (RLR Investments) | unnamed trib of Lytle Creek | renewal, eff. 2026-05-01 |
| `1PX00010*HD` | Wilmington RV Resort (MHC TT, L.P.) | unnamed trib of **Todd Fork** | new, eff. 2026-04-01 |
| `1PT00125*BD` | Clinton County Board of Developmental Disabilities | unnamed trib of **Wilson Creek** | renewal, eff. 2023-01-01 |
| `1MP00060*AM` | Wilmington Nursery (Kyle Isler) | swales → ag pond (**LAMP, non-discharging**) | new, eff. 2025-10-01 |

The signal worth keeping: **Lytle Creek is a multi-discharger receiving water** — the municipal WWTP, the landfill, the water plant, and Pine Hills MHP all reach Lytle Creek or its unnamed tributaries. That is exactly the cumulative-load setup the assimilative screen exists to test. [verified]

### What is missing — the screen cannot be computed

The Wilmington extractions are **permit-identity extractions only** (`image_pages_read: [0]` — cover page). They carry facility, permit number, receiving water, and outfalls but **no design average flow and no peak hydraulic capacity**, and the corpus has **no 7Q10 low-flow value for Lytle Creek, Todd Fork, or Wilson Creek.** Both inputs to a Tier-0 assimilative screen are therefore absent. [verified — gap]

Confirming this isn't a tooling oversight on my end: `hydrology_balance` ran clean but returned **Lima only** (Shawnee II → Ottawa River, American Bath → Pike Run, American II → Dug Run, plus the BOSC campus draw). The hydrology toolchain is bound to the **active site profile**, and there is no Wilmington profile, so `hydrology_balance`, `hydrology_scenario`, `sanitary_basis`, `stormwater_runoff`, and the Tier-1 SWMM tools **cannot screen Wilmington at all** until a profile and the design-flow/7Q10 inputs exist. [verified]

The one design-flow figure anywhere in this pull is **0.015 MGD**, and it belongs to **Hidden Valley MHP (`1PV00037`) — which is Sidney/Shelby County (Tawawa Creek, Great Miami basin), not Wilmington.** It is correctly filed under `oepa/sidney/` but surfaces in the Wilmington-area entity rollup; do not count it toward Lytle Creek. [verified]

### Data-quality notes for the entity layer

- **`1PV00037` Hidden Valley MHP** and **`1PD00008` Piqua WWTP (Great Miami)** are non-Wilmington dischargers appearing alongside the Wilmington set; basin attribution should keep them separate. [verified]
- **Wilmington Nursery (`1MP00060`)** is a Land Application Management Plan permit that *explicitly is not* a discharge authorization; exclude from any surface-water screen. Its applicant mailing address is Independence, OH (Cuyahoga Co.); the land-application site is 2065 Rombach Ave, Wilmington. [verified]
- Minor entity-resolution dups: "Van Wert WWTP" appears as multiple nodes; "City of Wilmington" / "City of Wilmington WWTP" split. Cosmetic. [verified]

---

## Bottom line

The receiving-water *inventory* for a Wilmington watershed point is already half-scaffolded (7 permits, Little Miami basin, a genuine multi-discharger reach in Lytle Creek), but the *screen* is not runnable — no design flows, no 7Q10, no site profile. And the premise that drives onboarding in this network — **documented data-center load** — is, on the evidence, **absent from the corpus for Wilmington.** Per the standing lesson that onboarding research-pass premises must be verified empirically before work proceeds, I'd treat the data-center driver as an open external question to confirm *before* investing in a full profile, and let any Wilmington page **lock its hydrology/data-center sections** rather than show fabricated completeness.

---

## Recommended follow-ups (concrete, trackable)

**Premise / scope (do first):**
1. **Verify the data-center driver for Wilmington externally** before profile work — JobsOhio/Clinton County ED announcements, Wilmington Air Park redevelopment, AEP Ohio interconnection filings, OEPA new air/NPDES sources. If none, hold Wilmington as inventory-only. *(open question — resolve before #2–#4.)*
2. **Reconcile why `oepa/wilmington/` was pulled with no load driver and no profile** — document the trigger, or reclassify the pull as a basin-coverage stub.

**Extraction targets (corpus gaps):**
3. **Re-extract `1PD00013` (City of Wilmington WWTP) at detail** to capture permitted **average design flow + peak hydraulic capacity** from the permit body — the load term of the screen.
4. **Capture/derive 7Q10 low flows** for Lytle Creek, Todd Fork, and Wilson Creek (permit fact sheets if present; otherwise USGS connector) — the dilution term.
5. **Pull the missing primary instruments** — these extractions are cover-page only; several note "no fact sheet" captured. Fetch fact sheets / Statements of Basis for `1PD00013`, `1PX00010`, `1PV00089`.

**Data hygiene:**
6. **Fix basin attribution** so `1PV00037` (Tawawa/Great Miami) and `1PD00008` (Piqua/Great Miami) don't read as Wilmington dischargers; exclude the `1MP00060` LAMP from surface-water screens.

**Profile work (gated on #1, #3, #4):**
7. **Register a Wilmington `SiteProfile`** (Little Miami basin — a new branch) only once a driver and the design-flow/7Q10 inputs exist; until then the frontend readiness layer should lock the thin sections.

I can file any of #2–#6 as issues via `report_novel_finding` — say which, since I'd rather not mass-file extraction-gap tickets as "novel findings" without your nod. Want me to proceed, and/or check the external data-center triggers in #1?
