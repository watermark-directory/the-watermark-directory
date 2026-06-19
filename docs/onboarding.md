# Onboarding a watershed-point site

How to bring a new site in the BOSC network (epic [#323](https://github.com/goedelsoup/bosc/issues/323) / [#308](https://github.com/goedelsoup/bosc/issues/308))
from nothing to a "coming soon" page, repeatably. Lima is the live reference build; the
basin sites (Fort Wayne, Defiance, …) come online one at a time. The scaffold is
registry-driven and the data tier is per-site keyed ([#325](https://github.com/goedelsoup/bosc/issues/325)),
so onboarding is a short, ordered chain — `bosc onboard <slug>` runs the middle of it.

> **`onboard` proposes; it never promotes.** Flipping a site to a live, switchable build is
> a separate, human, **parity-gated** edit (step 5). Onboarding seeds reviewable data and a
> blocking checklist — nothing it writes is a finding until a human verifies it against a
> cited source.

## The chain

### 1. Register the `SiteProfile` (code edit)

A site's identity is a `SiteProfile` in [`src/bosc/sites.py`](../src/bosc/sites.py)
`SITES` — the Python peer of the frontend registry. **Don't `model_copy` Lima and tweak a
few fields** — Lima's values are Lima-specific and the ones you forget will silently produce
wrong output. Build the entry deliberately; the field-by-field guide is below. Two hard rules:

- **Slug-scope every per-site output relpath** — `climatology_relpath`, `corridor_ddf_relpath`
  (→ `reference/hydrology/<slug>/…`), `baseline_relpath` (→ `reference/economics/<slug>/…`),
  `rsei_relpath` (→ `reference/rsei/<slug>/…`), `consumer_energy_relpath` + `grid_relpath`
  (→ `reference/eia/<slug>/…`). If you leave Lima's un-slugged paths, onboarding would
  overwrite Lima's committed files — `bosc onboard` now **refuses** when these aren't unique
  to the site (and a CI test enforces it), but scope them correctly from the start.
- The `SITES` key must equal the profile's `slug` (CI enforces this too).

Also register the site in the frontend [`frontend/src/lib/sites.ts`](../frontend/src/lib/sites.ts)
`SITES` with `status: "open"` (or `"onboarding"` once the build is queued) and
`selectable: false` — that alone auto-builds its `/network/<slug>` coming-soon page. (A CI
test asserts every Python-registered site also exists in the frontend registry.)

#### SiteProfile fields, by category

**Must set per-site** (geography/identity — wrong values mislead):

| Field(s) | What |
|---|---|
| `slug`, `place`, `basin` | identity (`basin` is the shared axis, e.g. `maumee`) |
| `nwis_sites`, `abstraction_gage`, `auglaize_gage`, `ottawa_gage` | the site's USGS gages (supply + abstraction reach) |
| `design_lat/lon`, `nasa_power_lat/lon`, `map_view_lat/lon/zoom` | the design point, met point, and map centroid |
| `rsei_fips`, `econ_fips`, `county_name` | the county (**Fort Wayne = Allen County, *Indiana*, FIPS `18003`** — not Ohio's `39003`) |
| `eia_state`, `eia861_utility_number`, `lmp_usd_mwh`, `lmp_citation` | the retail utility + its market zone |
| `hydro_utm_epsg`, `gnis_default_state`, `lsc_default_ga` | projection + state/legislature for lookups |
| `toxic_corridor_bbox`, `receiving_water_name` | the industrial receiving-water corridor |
| `plant_receiving` | per-WWTP receiving-water fallback (Lima's are Lima WWTPs — **replace**) |
| `climatology_relpath`, `corridor_ddf_relpath`, `baseline_relpath`, `rsei_relpath`, `consumer_energy_relpath`, `grid_relpath` | the six per-site **output** relpaths — slug-scope all of them (`reference/<source>/<slug>/…`); `parcels_relpath`/`footprint_relpath` point at the site's own committed geometry |
| `dominant_hsg`, `hsg_citation`, `pre_cover`, `post_cover`, `developed_pervious_cover`, `noaa_fallback_24h_depth_in` | stormwater design assumptions (onboarding's SSURGO step validates `dominant_hsg`) |
| `passby_auglaize_cfs`, `passby_ottawa_cfs` | in-stream passby minimums |

**Reused from the basin** (don't regenerate for a Maumee site): the curated mainstem 7Q10s
(`low-flow-7q10.derived.yaml`) and the ECHO POTW/NPDES inventory — both Maumee-wide.

**Needs research before it's trustworthy:** the GIS URLs (`allen_parcels_url`,
`lima_zoning_url`, `lima_floodzone_url`) are **Allen-County/City-of-Lima ArcGIS endpoints** —
a new jurisdiction has *different* endpoints and needs its own connector (the known lift,
below); the utility number + LMP; and `plant_receiving`, which must come from the site's own
NPDES fact sheets. Until verified, prefer omission/`[open]` over a copied Lima value.

### 2. Run the onboard chain

```sh
bosc onboard <slug>            # live connectors
bosc onboard <slug> --offline  # cached/committed fixtures only (hermetic)
```

`bosc onboard <slug>` ([`src/bosc/onboard.py`](../src/bosc/onboard.py)) builds its own
`Settings(site=<slug>)` (the global `--site` flag is not needed) and, for that site:

- **scaffolds** the per-site dirs (`data/reference/<slug>/`, `data/extracted/<slug>/`,
  and the per-output subdirs `reference/{hydrology,economics,eia,rsei}/<slug>/`) — each with
  a house-style README (source + gaps + regenerate). Idempotent: an existing README is left
  untouched.
- runs the **hydrology reach connectors**: NWIS → basin-derived 7Q10 (basin-level, see
  below), NOAA Atlas-14 → corridor DDF (per-site), SSURGO → dominant HSG over the footprint
  (a validation read against the profile), NASA-POWER → climatology (per-site).
- runs the **economics connectors**: Census+QCEW → county baseline (per-FIPS), EPA RSEI →
  county toxics inventory (per-FIPS), EIA → consumer energy (per-state), EIA-861 + grid →
  grid profile (per-utility — **sparse until the site has a documented facility load**, the
  data-center dimension). All per-site outputs are slug-scoped so they never clobber Lima.
- runs **`basin-screen`** as a coverage validation (read-only).
- prints a step table + the **blocking review checklist** (step 4).

Use `bosc onboard <slug> --dry-run` to preview the plan (every step + its target path)
without writing anything.

A brand-new site has no committed fixtures and no seed data, so offline the connector steps
record as `dry-run` (naming the cache key to record) or `skipped` — the run always completes.

### 3. Populate + review the per-site data

Seed the site's `data/extracted/<slug>/` and `data/reference/<slug>/` from its corpus, and
fill any `dry-run` connector outputs by running the per-connector commands live
(`derive-low-flows`, `nasa-power --write`, etc.) and committing the result. Every value is
an **onboarding seed** until reviewed against a cited source — keep the
`[verified]`/`[inference]`/`[reference]`/`[open]` discipline (see
[`docs/methodology.md`](methodology.md)); "no data-center here yet" is a finding, not a gap.

### 4. The review gate (blocking)

`onboard` prints this checklist; it is the human gate before promotion:

1. Every written reference value reviewed against a cited source (no fabricated values).
2. SSURGO dominant HSG matches the profile, or the profile is updated **with a citation**.
3. `basin-screen` coverage is sane for the site's receiving waters.
4. A per-jurisdiction County/City GIS connector exists (the known lift — below).
5. Self-research first pass run (the seam below; awaits [#247](https://github.com/goedelsoup/bosc/issues/247)).
6. Promotion is a separate manual edit (step 5).

The invariant is also enforced in CI by
[`frontend/src/lib/sites.test.ts`](../frontend/src/lib/sites.test.ts): every `selectable`
site must be `status: "live"`, and no `onboarding`/`open` site may be `selectable` — so a
site cannot slip live without the deliberate two-field change.

### 5. Promote (manual, parity-gated)

Once the site reaches parity, flip `status: "live"` + `selectable: true` for it in
`frontend/src/lib/sites.ts`. **Note the single-live-build constraint:** today only Lima is a
built site (re-rooted under `/bosc`); standing up a *second* live build at its own root is a
deeper, separate cutover, not part of routine onboarding.

## What's shared vs. per-site vs. the known lift

- **Basin / PJM / national (shared — reuse for free):** the curated mainstem 7Q10s
  (`bosc derive-low-flows` → `data/reference/hydrology/low-flow-7q10.derived.yaml`), the ECHO
  NPDES/POTW inventory (`bosc npdes`, Maumee HUC-8-wide), the PJM balancing-authority
  interchange (`ba-interchange.yaml`), and the federal energy backdrop (`federal-energy.yaml`).
  A new site does not regenerate these.
- **Per-site (slug-scoped via the profile `*_relpath` fields — what `onboard` writes):**
  *hydrology* — NASA-POWER climatology, Atlas-14 corridor DDF; *economics* — the Census+QCEW
  county **baseline** (FIPS), the RSEI county **toxics** inventory (FIPS), EIA **consumer
  energy** (state), and the **grid profile** (utility). Writes go to `reference/<source>/<slug>/…`;
  the **read** side stays Lima-keyed until a site reaches parity (the site build still consumes
  Lima's data until then — a deliberate, documented deferral).
- **Two dimensions captured, one not:** onboard captures **hydrology** and **economics**.
  The third dimension — **data-center activity** (extracted permits/records + entity graph) —
  is corpus extraction + the self-research pass (#247 seam), not a connector pull; it's also
  why the **grid profile** is sparse for a coming-soon site (it aggregates the facility's power
  load, which doesn't exist until that dimension is populated).
- **The known lift — per-jurisdiction GIS:** the coordinate/id-based connectors (NWIS /
  Atlas-14 / SSURGO / NASA-POWER) are free for any reach, but **County/City parcel & zoning
  GIS is jurisdiction-specific**. [`allen_gis.py`](../src/bosc/hydrology/connectors/allen_gis.py)
  and [`lima_gis.py`](../src/bosc/hydrology/connectors/lima_gis.py) are Allen-County / City-of-Lima
  ArcGIS endpoints; a new jurisdiction needs its **own** parcel/zoning/floodzone connector
  (the profile already carries its URLs, but the connector code is jurisdiction-shaped). Plan
  for this as the parity bar, not a coming-soon blocker.

## The self-research first pass (a seam — awaits #247)

The flow is meant to chain a **discipline-bound `bosc.agent` first pass** that investigates
the new site over the corpus and emits a *proposal* artifact a human triages — the agent
proposes, never promotes. The run machinery already exists
([`bosc research run`](../src/bosc/cli.py) → `bosc.research.run.run_research` + `write_run`
→ a `ResearchRunManifest` under `data/research/<slug>-<date>/`); what's missing is wiring the
investigative skills + system prompt into the agent ([#247](https://github.com/goedelsoup/bosc/issues/247)).
Until then this step is documented, not invoked:

```sh
# after #247:
bosc research run --topic "onboard <slug>: data-center activity + receiving-water screen"
# -> data/research/<slug>-<date>/{findings.md, manifest.yaml}  (review, then triage proposals)
```

When #247 lands, add this call to the onboard chain (or run it alongside) — the proposal
artifact feeds the step-3 review.
