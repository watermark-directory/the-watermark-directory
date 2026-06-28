# Onboarding — Urbana (urbana)

Living record for the Urbana watershed point (basin: great-miami), scaffolded by `bosc onboard`. Check items as you complete them; the site is **not** promoted (`frontend/src/lib/sites.ts` `status`/`selectable`) until the gate is clear.

Urbana is the network's **first Miami-basin site** (epic #440 / onboarding #441): the clean *headwaters* of the **Mad River buried-valley sole-source aquifer**, upstream of the Springfield/Dayton/Wright-Patterson corridor — the deliberate geological **inverse** of the Maumee lake-plain sites (groundwater-dominated HSG B vs. poorly-drained Black Swamp clays HSG D; sink = Ohio River, not Lake Erie; no Maumee-style nutrient TMDL).

## Dimension coverage

- [~] **Hydrology** — corridor-DDF + climatology connectors ran (cited); **Great Miami ECHO inventory committed** (PR #455: `great-miami-wwtp.*`, 81 POTWs across HUC-8 05080001 + 05080002); basin-screen now correct for this site: **14/81 screened, 0 violations, 1 tight** (was Maumee 7/129 — superseded). **Mad River 7Q10 still absent** from both low-flow tables — Urbana's WWTP is the direct receiving-water facility, and its screen still has no denominator (#445). SSURGO skipped (no footprint → HSG B stays `[inference]`).
- [x] **Economics** — county baseline + consumer-energy ran (high-confidence: Champaign Co, manufacturing LQ 4.14, information LQ 0.18 = greenfield signature). RSEI toxics ran (Champaign Co, 12 facilities / 9 scored; top by modeled Score: C V Materials); grid-profile ran on the now-pinned serving utility **Dayton Power & Light** (AES Ohio, EIA-861 #4922; PJM/PUCO; verified from the EIA-861 2024 Service_Territory).
- [~] **Data-center activity** — self-research first pass run (#247); **the weakest leg in the corpus** — only the `[open]` **Highland55** lead (one line in `docs/COURSE.md`, no instrument) + a Honda "Champaign-area" candidate profile (not pinned). **Zero Urbana/Champaign primary documents.** See self-research summary below.
- [ ] **Per-jurisdiction GIS** — Champaign County parcels / City of Urbana zoning connector (the known lift; see docs/onboarding.md). Flood = national NFHL (wired).

## Last onboard run (2026-06-21, `--research`)

| step | status | output |
|---|---|---|
| scaffold | ok | per-site dirs + READMEs |
| derive-low-flows | ok | reference/hydrology/low-flow-7q10.derived.yaml (Maumee mainstems only — no Mad River) |
| corridor-ddf | ok | reference/hydrology/urbana/atlas14-corridor-ddf.yaml (24h-100yr 5.54 in) |
| ssurgo-hsg | skipped | footprint missing: extracted/urbana/bosc-site-footprint.yaml |
| climatology | ok | reference/hydrology/urbana/nasa-power-climatology.yaml |
| basin-screen | ok (Maumee) | 7/129 dischargers — the Maumee inventory; **no Great-Miami coverage** **(superseded — see #446)** |
| basin-screen | ok (Great Miami) | 14/81 screened (0 violations, 1 tight) — `great-miami-wwtp.potw.yaml` (PR #455); 39 no receiving water, 28 no 7Q10; Mad River 7Q10 still absent (#445) |
| econ-baseline | ok | reference/economics/urbana/baseline.yaml |
| rsei | ok | reference/rsei/urbana/inventory.yaml — 12 facilities (9 scored) |
| consumer-energy | ok | reference/eia/urbana/consumer-energy.yaml |
| grid-profile | ok | reference/eia/urbana/grid-profile.yaml — Dayton Power & Light #4922, PJM |
| self-research | ok | research/onboard-urbana-urbana-data-center-activity-recei-2026-06-21/ |

## Self-research (Phase 5; #247) — 2026-06-21

`bosc onboard urbana --research` (claude-opus-4-8, 27 turns, $1.02). Findings + manifest in
`data/research/onboard-urbana-urbana-data-center-activity-recei-2026-06-21/`.

**Bottom line.** Urbana is scaffolded but **not promotable** — its two load-bearing dimensions are
both open: data-center activity is the **weakest in the network** and the receiving-water screen has
**no Mad-River denominator at all**.

- **Data-center activity — `[open]`/`[inference]`, no primary record.** The only Urbana-specific signal is **Highland55** (a one-line `[open]` lead in `docs/COURSE.md`; it appears only in analysis text — no deed/NPDES/LLC/CRA/zoning instrument). A second, adjacent signal — **Honda's announced "own Ohio data center" in the "Marysville / Clark / Champaign area"** (`cloud-consumer-candidates.yaml`) — is a demand-fit *candidate profile*, not pinned to Urbana/Champaign. `[verified]` **zero** Urbana/Champaign/Mad-River primary documents are in the corpus. **Method note:** the Lima/Allen Bistrozzi land-assembly graph is **not** bridged in — there is no evidentiary link; any Urbana land assembly stays a separate register.
- **Receiving-water screen — partially unblocked.** The Great Miami ECHO inventory (`great-miami-wwtp.potw.yaml`, PR #455) is now committed; the basin-screen runs correctly for this site: **14/81 screened, 0 violations, 1 tight** (39 no receiving water, 28 no 7Q10). The prior "7/129 screened" figure was the Maumee inventory — `[superseded]` by the Great Miami run. The residual gap: `receiving_water_name` is the Mad River `[verified]`, but it's in **neither** 7Q10 table (cited = the three Lima streams; derived = the four Maumee mainstems), so the **Urbana WWTP** falls into the `no_7q10` bucket. The Mad River **is gaged at Urbana (03267000)**, so a derived 7Q10 is obtainable — the denominator is still missing, not impossible (#445).
- **The screen should be a *source-water / abstraction* screen, not effluent-dominance.** Lima's thesis is effluent-vs-tiny-tributary-7Q10; Urbana's is **consumptive cooling draw vs. Mad River baseflow + the sole-source buried-valley aquifer** (which is exactly why the profile carries `abstraction_gage`/`supply_gage`/`passby` fields). The methodology must not copy Lima's denominator logic onto it.
- **Grid is a different zone than Lima.** Likely **AES Ohio / DAY PJM zone**, not AEP — pin the EIA-861 utility number + PJM zone before publishing any grid figure (Ohio, so the cross-state connector axis isn't re-triggered).

**Proposals — 5 filed as sub-issues of #441:** Mad-River 7Q10 + Urbana WWTP NPDES (the screen's central hole); a Great-Miami / Ohio-River ECHO discharger inventory; source Highland55 via primary instruments; pin-or-downgrade the Honda Champaign-area data center; ~~resolve the Champaign-County utility + PJM zone~~ **done** (Dayton Power & Light #4922, PJM/PUCO; grid-profile committed).

## Review gate (blocking)

- [ ] Every written reference value is reviewed against a cited source (no fabricated values).
- [ ] SSURGO dominant HSG matches the profile, or the SiteProfile is updated with a citation. (HSG B is `[inference]`; footprint needed.)
- [~] basin-screen coverage is sane for this site's receiving waters. (Great Miami inventory committed PR #455, screen now correct: 14/81, 0 violations, 1 tight. **Remaining: Mad River 7Q10 for the Urbana WWTP denominator — #445.**)
- [ ] A per-jurisdiction County/City GIS connector exists (the known lift — see docs/onboarding.md).
- [x] Self-research first pass reviewed (Phase 5, 2026-06-21; data-center = weakest leg, receiving-water screen empty; 5 proposals filed as sub-issues of #441).
- [ ] PROMOTION IS A SEPARATE MANUAL EDIT: flip status->live + selectable->true for 'urbana' in frontend/src/lib/sites.ts, parity-gated. onboard never auto-promotes; only one live build (/bosc) exists today.
