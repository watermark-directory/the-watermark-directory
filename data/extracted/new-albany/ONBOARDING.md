# Onboarding — New Albany (new-albany)

Living record for the New Albany watershed point (basin: scioto), scaffolded by `bosc onboard`. Check items as you complete them; the site is **not** promoted (`frontend/src/lib/sites.ts` `status`/`selectable`) until the gate is clear.

New Albany / Licking County is the network's **third-basin branch** (Scioto epic #484, onboarding #485) and the **data-center epicenter** of the Ohio boom — Intel "Ohio One" + Google/Meta/AWS/Microsoft/QTS in the New Albany International Business Park, the at-scale, already-built comparator to the speculative Miami greenfields. It **straddles the Scioto↔Muskingum divide**: the New Albany city core (Franklin Co) drains Rocky Fork + Blacklick → **Big Walnut Creek → Scioto** (HUC-8 05060001); the Intel/business-park epicenter (Licking Co, Jersey Twp) drains the **South Fork Licking River → Licking → Muskingum** (HUC-8 05040006). The profile frames the Scioto/Big-Walnut side; the Muskingum-side receiving water is `[open]` and flips if the pinned footprint lands on the Licking side. Grid is back to the **PJM AEP** zone (AEP Ohio / Ohio Power #14006), unlike the Miami branch's DAY/DEOK.

## Dimension coverage

- [x] **Hydrology** — corridor-DDF + climatology ran (cited). The **Scioto-basin 7Q10s are derived** (`low-flow-7q10.derived.yaml`): Big Walnut Creek 35.43 cfs (03229500), Scioto River 515.73 (03234500), Olentangy 13.53, Big Darby 11.24. The site's at-reach supply gage is **Big Walnut at Central College (03228500)**. SSURGO skipped (no footprint → HSG C is `[inference]`). **Basin-screen is 0/0 pending the Scioto ECHO inventory** — the live `bosc npdes --basin scioto` pull was deferred at onboard time (ECHO 300/hr throttle, HTTP 429); rerun it to populate `scioto-wwtp.potw.yaml` and the screen.
- [~] **Economics** — county baseline (Licking 39089) + consumer-energy (OH) + **grid-profile** ran. The grid-profile **succeeded** because the AEP utility is pinned (Ohio Power #14006), unlike the Miami sites' `[open]` utility. RSEI skipped (v234 `elements.csv.gz` cache miss — same deferral as the Miami sites).
- [ ] **Data-center activity** — `[open]`, the research target: Intel "Ohio One" + the hyperscaler cluster. The self-research first pass (`bosc onboard new-albany --research`, #247) has **not** been run; it + a discover-and-pin sweep (the Springfield #454 pattern) is the next step. No Intel/hyperscaler facility is in the corpus or the entity graph yet.
- [~] **Per-jurisdiction GIS** — parcels = the OGRIP Ohio statewide layer scoped to Licking (Licking County's own ArcGIS parcel/zoning REST is currently stopped, HTTP 500; OGRIP `SitusAddressAll` is null for Licking — a thin catalog). Flood = national NFHL (wired). Zoning = `[open]` (no confirmed New Albany / Jersey Twp REST). The Franklin County Auditor hosts a fuller native owner+CAMA parcel layer for the city-core side — a follow-up upgrade.

## Last onboard run (2026-06-22)

| step | status | output |
|---|---|---|
| scaffold | ok | per-site dirs + READMEs |
| derive-low-flows | ok | low-flow-7q10.derived.yaml — Scioto mainstems added (Big Walnut 35.43, Scioto 515.73, Olentangy 13.53, Big Darby 11.24) |
| corridor-ddf | ok | reference/hydrology/new-albany/atlas14-corridor-ddf.yaml |
| ssurgo-hsg | skipped | footprint missing: extracted/new-albany/bosc-site-footprint.yaml |
| climatology | ok | reference/hydrology/new-albany/nasa-power-climatology.yaml |
| basin-screen | skipped | 0/0 — the Scioto ECHO inventory is not yet pulled (ECHO 429 at onboard time) |
| econ-baseline | ok | reference/economics/new-albany/baseline.yaml (Licking 39089) |
| rsei | skipped | cache miss (elements.csv.gz); no Licking-Co toxics inventory |
| consumer-energy | ok | reference/eia/new-albany/consumer-energy.yaml |
| grid-profile | ok | reference/eia/new-albany/grid-profile.yaml (AEP Ohio #14006 — pinned) |

## Open follow-ups

- **Pull the Scioto ECHO inventory** — `bosc npdes --basin scioto` (deferred at onboard time on a 429 throttle) → commit `scioto-wwtp.potw.yaml` and re-run the basin-screen. The New Albany Scioto-side receiving water (Big Walnut Creek) is covered by the Scioto inventory (HUC 05060001); the Licking/Muskingum side is **not** (a future Muskingum-basin inventory).
- **Resolve the divide** — pin the operative footprint (Franklin/Scioto vs Licking/Muskingum) and flip `receiving_water_name` to the South Fork Licking River if the facility lands Licking-side. Note: Intel's *process* wastewater is routed to Columbus' sanitary sewer (→ Scioto), not a surface stream.
- **Data-center first pass** — run `--research` + a discover-and-pin sweep (Intel "Ohio One", the hyperscalers); pin each facility to a primary instrument (no Bistrozzi-graph bridging).

## Review gate (blocking)

- [ ] Every written reference value is reviewed against a cited source (no fabricated values).
- [ ] SSURGO dominant HSG matches the profile, or the SiteProfile is updated with a citation. (HSG C is `[inference]`; footprint needed.)
- [ ] basin-screen coverage is sane for this site's receiving waters. (**Pending the Scioto ECHO inventory pull — `bosc npdes --basin scioto`.**)
- [ ] A per-jurisdiction County/City GIS connector exists. (Parcels = OGRIP-Licking substitute; zoning `[open]`; Licking's own REST is down.)
- [ ] Self-research first pass reviewed (`--research`; triage `data/research/<slug>-<date>/`). **Not yet run.**
- [ ] PROMOTION IS A SEPARATE MANUAL EDIT: flip status->live + selectable->true for 'new-albany' in frontend/src/lib/sites.ts, parity-gated. onboard never auto-promotes; only one live build (/bosc) exists today.
