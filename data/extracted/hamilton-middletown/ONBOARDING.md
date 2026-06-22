# Onboarding — Hamilton · Middletown (hamilton-middletown)

Living record for the Hamilton · Middletown watershed point (basin: great-miami), scaffolded by `bosc onboard`. Check items as you complete them; the site is **not** promoted (`frontend/src/lib/sites.ts` `status`/`selectable`) until the gate is clear.

Hamilton · Middletown is the **lower Great Miami heavy-industry node** (Butler County) and the I-75 Cincinnati–Dayton corridor's southern anchor, near the Great Miami's Ohio River confluence — and it is the **established-industry comparator** that inverts every other Miami point: **Cleveland-Cliffs Middletown Works** (the former AK Steel integrated mill) anchors a legacy steel/paper/chemicals corridor of large *existing* water users + NPDES dischargers on the Great Miami **mainstem**, the foil to the speculative-greenfield headwaters. Three things distinguish it: the water posture flips (a large mainstem with real dilution capacity, not a headwater ditch — though over the same buried-valley sole-source aquifer, wider near the confluence); the grid is **split** (the City of Hamilton runs its own **municipal** electric utility — AMP, EIA-861S short-form — while Middletown is Duke Energy Ohio), both in PJM's **DEOK** zone (a *third* PJM zone for the network after AEP and DAY); and the seat is **Butler County (FIPS 39017)**, deliberately guarded as *not* Hamilton County / Cincinnati. (UTM 16N, like WPAFB — west of the 84°W meridian.)

## Dimension coverage

- [~] **Hydrology** — corridor-DDF + climatology connectors ran (Hamilton-centroid, cited; Atlas-14 24h 2-yr 2.82 in → 100-yr 5.58 in). The receiving-water screen is unbuilt: no Great Miami 7Q10 (the derived table is Maumee mainstems only — neither gage 03274000 [Hamilton] nor 03272100 [Middletown] has a low flow) and no WWTP/industrial outfall ingested (`plant_receiving={}`). **Structural contrast (don't pre-judge):** Lima's violations are tiny effluent-dominated headwater tributaries (7Q10 0.03–0.78 cfs); Hamilton/Middletown sit on the **lower Great Miami mainstem**, an order-of-magnitude-larger river — the assimilative question screens against a *real river*, but the actual 7Q10 must be derived and cited before any screen statement. SSURGO skipped → HSG B stays `[inference]`; the sole-source-aquifer claim is `[inference]` pending verification.
- [~] **Economics** — Butler County baseline + consumer-energy ran (high-confidence: pop 389,910, 160,057 jobs). The signature is unmistakably **heavy-industry + logistics**: Manufacturing (NAICS 31-33) LQ **1.83** (the Middletown Works comparator), Wholesale Trade LQ **2.06** + Transportation/Warehousing LQ **1.48** (the I-75 corridor), and Information (51) LQ **0.29** + Prof/Sci/Tech (54) LQ **0.40** — both well below national (no data/IT-hosting concentration, sharp contrast to Greene/WPAFB's NAICS-54 LQ 2.11). **The site's real differentiator is toxics, and it is unmeasured:** RSEI `fips=39017` is set but the inventory was never pulled (v234 cache miss) and `toxic_corridor_bbox=(0,0,0,0)` — of all Miami points this is the one with a large *active* heavy-industrial discharger on the mainstem, so the RSEI inventory is likely material here in a way it is not for the greenfield siblings (the highest-value outstanding connector). Grid-profile errored — the **split utility** (Hamilton muni/AMP EIA-861S vs Middletown/Duke) and the **DEOK** PJM zone are unpinned.
- [~] **Data-center activity** — self-research first pass run (#247). `[verified]` **zero** Hamilton/Middletown/Butler records in the corpus (0 matches across 1,485 document lines; entity graph entirely Lima). `facility=None`; *as of this corpus there is no Hamilton–Middletown data-center land assembly or permit record* — a finding, not a gap, and the economics corroborate it ("heavy-industry node, not data cluster"). The `[open]` sweep target is the **Butler County / West Chester / I-75** boom corridor. **Method note:** the Lima/Allen Bistrozzi land-assembly graph is **not** bridged in.
- [ ] **Per-jurisdiction GIS** — Butler County parcels / City of Hamilton + Middletown zoning connector (the known lift). **The same-name-county trap is acute here** (Hamilton County ≠ City of Hamilton) — verify the situs is **Butler County OH** from a live `?f=json` sample. Flood = national NFHL (wired).

## Last onboard run (2026-06-22, `--research`)

| step | status | output |
|---|---|---|
| scaffold | ok | per-site dirs + READMEs |
| derive-low-flows | ok | reference/hydrology/low-flow-7q10.derived.yaml (Maumee mainstems only — no Great Miami) |
| corridor-ddf | ok | reference/hydrology/hamilton-middletown/atlas14-corridor-ddf.yaml |
| ssurgo-hsg | skipped | footprint missing: extracted/hamilton-middletown/bosc-site-footprint.yaml |
| climatology | ok | reference/hydrology/hamilton-middletown/nasa-power-climatology.yaml |
| basin-screen | ok (Maumee) | 7/129 dischargers — the Maumee inventory; **no Great-Miami coverage** |
| econ-baseline | ok | reference/economics/hamilton-middletown/baseline.yaml (Butler Co 39017) |
| rsei | skipped | cache miss (elements.csv.gz) — **the highest-value gap for this industrial site** |
| consumer-energy | ok | reference/eia/hamilton-middletown/consumer-energy.yaml |
| grid-profile | error | EIA-861 2024: no Short-Form ('861S') row for utility #0 (split utility unpinned) |
| self-research | ok | research/onboard-hamilton-middletown-hamilton-middletown-2026-06-22/ |

## Self-research (Phase 5; #247) — 2026-06-22

`bosc onboard hamilton-middletown --research` (claude-opus-4-8, 26 turns, $1.09). Findings + manifest in
`data/research/onboard-hamilton-middletown-hamilton-middletown-2026-06-22/`.

**Bottom line.** Registered + half-seeded but **not promotable**. Unlike its greenfield siblings, its
defining features are an *established* heavy-industrial discharger on a *large mainstem* over a
*sole-source aquifer* — which makes the **RSEI inventory** and the **Great Miami 7Q10** the two decisive
next steps.

- **Receiving-water screen — inverted posture, still blocked.** No Great Miami 7Q10 (gages 03274000 /
  03272100 not in the derived file; `derive-low-flows` not extended to this basin) and no WWTP/industrial
  NPDES ingested. The mainstem means the assimilative question is qualitatively different from Lima's
  effluent-dominated ditches — but **don't pre-judge the direction**; derive the actual 7Q10 from the two
  cited gages and cite it before publishing any screen.
- **Toxics is the differentiator, and it is unmeasured.** RSEI `fips=39017` set, inventory never pulled,
  `toxic_corridor_bbox` empty. This is the only Miami node with a large active industrial discharger
  (Middletown Works), so the RSEI inventory is likely material — **the highest-value outstanding connector.**
- **Data-center activity — none documented; economics say "heavy-industry node, not data cluster."** Zero
  corpus records; Information LQ 0.29 / Prof-Sci-Tech LQ 0.40 corroborate no IT-hosting concentration. The
  open work is an I-75-corridor sweep that pins activity or records a flat no-activity finding.
- **Split utility + a third PJM zone.** City of Hamilton (municipal/AMP, EIA-861S short-form) vs Middletown
  (Duke Energy Ohio); both in PJM **DEOK** (Duke Energy Ohio/Kentucky) — a third zone for the network. Pin
  the EIA-861 number(s), the DEOK zone, and a cited LMP; re-scan the grid/consumer-energy connectors for the
  muni/short-form path (the one that bit Bryan), even though Butler is in-state OH.
- **Sole-source aquifer overlay.** The Great Miami Buried Valley Aquifer is asserted in `hsg_citation` as a
  US-EPA sole-source aquifer `[inference]`; verify against the EPA designation record and promote to
  `[reference]` — the groundwater analogue of Xenia's Scenic-River constraint.

**Proposals — all 5 manifest drafts + the named DC sweep filed** as sub-issues of #443 (none moot — the run
knew the site was registered; the missing-artifacts work is done by this PR): the Great Miami 7Q10 + WWTP/
Middletown Works NPDES (receiving-water inputs); run the RSEI toxics inventory + corridor bbox (the
differentiator); verify the sole-source-aquifer designation; resolve the split utility + pin the DEOK zone;
and the I-75-corridor data-center activity sweep.

## Review gate (blocking)

- [ ] Every written reference value is reviewed against a cited source (no fabricated values).
- [ ] SSURGO dominant HSG matches the profile, or the SiteProfile is updated with a citation. (HSG B is `[inference]`; footprint needed.)
- [ ] basin-screen coverage is sane for this site's receiving waters. (**Currently the Maumee inventory — a Great Miami 7Q10 + the RSEI/industrial-discharger inventory are required.**)
- [ ] A per-jurisdiction County/City GIS connector exists (the known lift — see docs/onboarding.md; verify Butler County OH, not Hamilton County).
- [x] Self-research first pass reviewed (Phase 5, 2026-06-22; established-industry comparator on a mainstem; RSEI toxics is the unmeasured differentiator; all 5 manifest proposals + the DC sweep filed as sub-issues of #443).
- [ ] PROMOTION IS A SEPARATE MANUAL EDIT: flip status->live + selectable->true for 'hamilton-middletown' in frontend/src/lib/sites.ts, parity-gated. onboard never auto-promotes; only one live build (/bosc) exists today.
