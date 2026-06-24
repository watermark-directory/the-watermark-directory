# Component audit — Watermark Design System ↔ the live Astro site

Spec↔implementation audit for the DesignSync component sync (the follow-up to the token
regularization, PRs #549–#554). The **source-of-truth** is the Claude Design *Watermark Design
System* project (`dbe30a08-547c-442e-b4ac-81492fa5570f`); the **mirror** of its specs now lives in
`frontend/design-system/components/**` + `ui_kits/**` (pulled this pass). This document maps every
spec to its live implementation and records the drift, the **direction** each should resolve, and
the effort — so reconciliation (Stage 2) is targeted, not a blind rewrite.

**The framework boundary:** specs are React `.jsx` (+ `.d.ts` prop contract + `.prompt.md` design
intent); impls are Astro `.astro`/`.tsx` consuming one `frontend/src/styles/site.css`. "Sync" is
never a file copy — it's reconciling *values / structure / variants / taxonomy*.

## ⚠️ Reading rule: the global flatten layer (do not chase ghost drift)

`site.css:63` carries a universal, `!important` flatten:

```css
*, *::before, *::after { border-radius: 0 !important; box-shadow: none !important; }
```

It is the **only** `!important` radius/shadow in the sheet, so it overrides **every**
`border-radius`/`box-shadow`/round-dot declaration at runtime. The spec reaches square via
`var(--radius, 0)`; the impl reaches the *same* square via this flatten. **Result: the live site
already conforms to the spec's square-corner / no-shadow / square-dot law.** Therefore every
"rounded corner", "drop shadow", or "round dot" the per-component scan flagged (`.btn` 6px,
`.evidence`/`.evidence-dot` pill+circle, `.td-pin` circle+shadow, `.fs-lg` 14px+shadow, `.fs-dot`,
`.tl-dot`, `.hub-door`, `.td-srccard`, the 2–3px rails, the Hypotheses cards…) is **dead source —
not visible drift.** It is at most optional source hygiene (delete the dead declarations), **low
priority**, and explicitly out of scope for reconciliation. The audit below has been corrected for
this; the directions reflect what is *actually visible*.

## The shape of the drift (roll-up)

27 specs. Once the dead radius/shadow noise is removed, the drift sorts cleanly into two piles:

- **The live site is AHEAD of the spec (→ push impl→spec):** ~14 components. The page
  compositions especially — the live pages carry real-data derivation, richer rails, no-JS
  interactions, live-bundle binding, the two-tier chrome, the grouped Site Selector — that the
  hand-drawn comps never caught up to. Closing these means a **DesignSync push** (updating the
  Claude Design project), which is the *other* deferred option — the audit shows the two are the
  same work.
- **The site should adopt the spec (→ reconcile impl←spec):** a **short, high-value list** —
  EvidenceTag taxonomy/variants, PhaseDot color ramp, TextField focus/label, the RadioCard
  kind-picker, SectionCard's missing **locked** door, the LeadCard confidence taxonomy, and (if
  chosen) extracting the 6 primitives.

| direction | count | components |
|---|---|---|
| **reconcile impl←spec** (actionable) | 6 | EvidenceTag, PhaseDot, TextField, RadioCard, SectionCard, LeadCard |
| **push impl→spec** (spec is stale/simpler) | 14 | ProfileHeader, RecordBlock, SourceCard, Timeline, DirectoryHome, Hypotheses, NetworkChrome, SiteChrome, SiteSelector, SubmitLead, LeadsBoard, SiteHome, Profile, RecordScreen, Watershed |
| **missing primitive** (extract-vs-align, decide per-primitive) | 6 | Button, Eyebrow, PhaseDot*, Checkbox, RadioCard*, TextField* |
| **effectively in sync** (visible parity; flagged drift was dead source) | 3 | FigureStat, AnnotationPin, ConnectChip |

(*PhaseDot/RadioCard/TextField appear twice: they're both a missing-primitive *and* carry real
non-radius drift.)

The single load-bearing reconcile is **EvidenceTag** — it's the evidence grammar every figure
wears, and its taxonomy genuinely diverges (below).

---

## Core primitives (`components/core/`)

### EvidenceTag · `reconcile impl←spec` + `push impl→spec` · **M** · risk: med
- **Spec:** `components/core/EvidenceTag.jsx` · **Impl:** `src/components/EvidenceTag.astro` (`.evidence`, 11 importers)
- **Real drift (visible):**
  - **taxonomy** — spec has **5** kinds `verified/inference/open/gap/key`; impl has **4**
    `verified/inference/open/filename`. `gap` (oxblood scope-gap) + `key` (highlight) are missing
    from the impl; `filename` is real repo vocabulary the spec lacks. → reconcile impl←spec (add
    `gap`+`key`) **and** push impl→spec (teach the spec `filename`, or map it to `reference`).
  - **variants** — spec adds `size` (sm/md), `dot` toggle, `brackets` toggle (default **off**);
    impl has none and hardcodes `[brackets]` always-on. Flipping brackets-default touches the
    `[verified]` record-screen convention — review carefully.
- **Dead (flatten):** spec square tag + square dot vs impl pill (`999px`) + round dot (`50%`) — both
  already render square. The `open`/`filename` `#ece8dc` literals → tokens is minor hygiene.
- **Class:** `wm-evidence` vs `evidence` — keep the repo name (not drift).

### Button · `missing-impl` (extract vs align) · **L** · risk: med
- **Spec:** `components/core/Button.jsx` (solid/forest/ghost/link × sm/md/lg, icon/iconRight/href/disabled) · **Impl:** a thin forest-only `.btn` + ad-hoc scoped buttons (`.dirh-btn--solid/--ghost`, `.locked-req-btn`, `.pl-cta-btn`, `.gb-btn`, `.leads-cta-btn`, form buttons…).
- **Real drift:** variant matrix (4×3 vs 1×1), border weight (1px vs 1.5px), font-weight (600 vs
  700), no `href`→anchor / icon / disabled in the shared base. (`.btn` `border-radius:6px` is dead.)
- **Extract vs align:** **extract** = a `Button.astro` (4 variants × 3 sizes, icon/href/disabled),
  fold the `*-btn` classes, repoint. **align** = add variant/size modifiers to `.btn` + fix the
  weight/border. **Call sites = 15 files / 11 `<button>` tags.**

### Eyebrow · `missing-impl` (extract vs align) · **L** · risk: low
- **Spec:** `components/core/Eyebrow.jsx` (one component, `tone` muted/faint/forest/ink + `as`) · **Impl:** ~16 hand-rolled `*-eyebrow` classes (`hub-eyebrow`, `submit-eyebrow`, `td-eyebrow`, `dirh-eyebrow`, …) + `.ph-kind`, each re-declaring the mono/uppercase/tracking recipe with small size/tracking drift.
- **Direction:** reconcile impl←spec — normalize onto one register.
- **Extract vs align:** **extract** = `Eyebrow.astro` collapsing the ~16 classes. **align** = a shared
  `.eyebrow` base the variants compose. **Call sites = 35 files** (purely additive label styling).

### PhaseDot · `reconcile impl←spec` (+ missing-impl) · **M** · risk: med
- **Spec:** `components/core/PhaseDot.jsx` (neutral ramp on bare text, **no fill**: live→forest, building→**ink**, queued→**muted**, tracking→**faint**; dot tracks label color) · **Impl:** `.phase-pill` (`site.css:354`) + `.switcher-status` (`SwitcherRow.astro`) + `.status-dot`.
- **Real drift (visible — colors aren't flattened):** impl renders a **filled pill** with a
  divergent ramp — building→**green** (≈live) and queued→**amber** (`.phase-pill`); queued→**amber**,
  tinted backgrounds (`.switcher-status`). Spec is no-fill with building→ink, queued→muted. This is
  genuine visible drift. The data axis already matches (`SiteStatus` in `lib/sites.ts`).
- **Note:** impl's `locked` state is orthogonal to `status` (correct — don't fold into PhaseDot).
- **Extract vs align:** **extract** = `PhaseDot.astro` from `SiteStatus`. **align** = repoint the
  `is-building`/`is-queued` colors + strip the pill fill. **Call sites = 5 files.**

### AnnotationPin · effectively in sync (minor reconcile) · **S** · risk: low
- **Spec:** `components/core/AnnotationPin.jsx` (square pin, `tone` forest/oxblood/muted, `active` ring) · **Impl:** `src/components/TeardownSourceCard.astro` (`.td-pin`, `.td-pin.is-danger`, 1 call site).
- **Real drift:** spec adds an `active` outline ring + a muted tone; impl exposes only
  `is-danger`(≈oxblood) + number. Low-value enhancement. (`.td-pin` circle+shadow → dead; already
  square/flat on screen.)

### ConnectChip · effectively in sync (clean extract opportunity) · **M** · risk: low
- **Spec:** `components/core/ConnectChip.jsx` (one `<a>` chip, `kind` prefix entity/concept/timeline/place/person/**map**, `tone` forest/neutral) · **Impl:** `.td-chip`/`.td-chip-kind` inlined in `RecordBlock.astro` + `Timeline.astro` (2 call sites; shape already matches).
- **Real drift:** no shared primitive (inlined twice); spec adds a `neutral` tone + a `map` kind.
- **Direction:** a clean extract of `.td-chip` → one `ConnectChip.astro` consumed by both; add the
  neutral tone + `map` kind. Low priority.

## Form primitives (`components/forms/`) — all `missing-impl`

### Checkbox · `reconcile impl←spec` (net-new) · **S** · risk: low
- **Spec:** `components/forms/Checkbox.jsx` (18px square box, 2px border, forest fill + bone check) · **Impl:** native UA checkboxes only (island simulators + the `Base.astro` nav toggle); no `.checkbox` rule, and the design's "credit me as a contributor" control has no repo instance yet.
- **Extract vs align:** **extract** = a `.checkbox`/`Checkbox.astro` per spec + repoint the Base
  toggle (and the future Submit "credit me"). **align** = n/a (net-new). **Call sites = 6.**

### RadioCard · `reconcile impl←spec` (+ missing-impl) · **M** · risk: med
- **Spec:** `components/forms/RadioCard.jsx` (selectable **card**: square dot + bold title + one-line desc; forest-tint when selected) · **Impl:** the SubmitForm kind-picker is a **segmented pill bar** (`.seg-row`, sr-only radios); the leads filter is a tab strip — neither is card-shaped.
- **Real drift:** the "what kind of lead?" picker should be RadioCards per `forms.card.html`, not a
  segmented pill (structural + the no-JS `:checked` wiring).
- **Extract vs align:** **extract** = `.radiocard`/`RadioCard.astro` + repoint the SubmitForm
  fieldset to a 2-col grid (keep sr-only radios for no-JS). **align** = nudge the leads-filter
  selected styling toward forest-tint + square dot. **Call sites = 1 card-picker** (5 radio surfaces).

### TextField · `both` (+ missing-impl) · **M** · risk: low
- **Spec:** `components/forms/TextField.jsx` (mono-uppercase micro-label + `optional` qualifier, hairline border, square, **forest focus ring** `--ring-focus`, leading `icon` slot) · **Impl:** `.form input/textarea` (`site.css:1607`) + `.locked-input` (dark variant) + ask/search.
- **Real drift (visible):** focus = `outline:2px solid` not the spec's forest **ring**; label is a
  plain `font-weight:600` block, not the spec's mono uppercase micro-label; no `optional` qualifier;
  no leading `icon` (e.g. on the evidence-URL field). → reconcile impl←spec. (The `.form` `6px`
  radius + `.submit-card` box-shadow are dead.)
- **Extract vs align:** **extract** = `.field`/`TextField.astro` (label+control+hint, `optional`/`icon`
  props) + repoint SubmitForm's 3 fields + ask/search. **align** = retune `.form input/textarea` to
  the forest ring + mono micro-label. **Call sites = 7 inputs** (32 broad incl. islands).

## Record components (`components/record/`)

### FigureStat · effectively in sync · **—** · risk: low
- **Spec:** `components/record/FigureStat.jsx` · **Impl:** `src/components/FigureStat.astro` (`.fs-*`).
- Parity on the `lg`/`sm` split, basis chip, warn→oxblood, mono value, unit/sub/source. All flagged
  drift (`.fs-lg` 14px+shadow, `.fs-dot` round) is **dead** under the flatten. No action.

### ProfileHeader · `push impl→spec` (+ trivial) · **S** · risk: low
- **Spec:** `components/record/ProfileHeader.jsx` · **Impl:** `src/components/ProfileHeader.astro` (`.ph-*`).
- Impl is **ahead**: `.rb-seen` "seen in the walk" backlink + real `graphHref`/`r.href`/`correctHref`
  (spec links are `#`). Delegates the stat strip to `<FigureStat size="sm">` + pill to
  `<EvidenceTag>` (good reuse). → push the walk-backlink + href model to the comp.

### RecordBlock · `push impl→spec` · **M** · risk: low
- **Spec:** `components/record/RecordBlock.jsx` · **Impl:** `src/components/RecordBlock.astro` (`.rb-*`).
- Impl is **ahead**: nested-block section via `<FieldValue>` (with `~` approx handling), `.rb-seen`
  walk backlink, structured `verify {href,label}` + `correctHref` (spec `verify` is a bare string).
  → push to the comp. (Rail radius dead.)

### SectionCard · `reconcile impl←spec` · **M** · risk: med
- **Spec:** `components/record/SectionCard.jsx` (open **and** `locked` variants) · **Impl:** `.hub-door` cards inlined in `…/site/index.astro` (1 call site).
- **Real drift (visible):** the spec's **locked** door (dashed `--line-2` border, 🔒, `lockNote`,
  0.85 opacity, neutral badge) has **no impl** — every `.hub-door` is an open `<a>`. Genuine
  capability gap. Also the badge is bare green text vs the spec's bordered **forest-tint chip**.
  (impl's desc/note/arrow are an enrichment → push; card radius/shadow dead.)
- **Extract vs align:** **extract** = a `SectionCard.astro` carrying both variants (the locked state
  is a real capability, not just CSS). **align** = add a locked branch inline + box the badge.

### SourceCard · `push impl→spec` · **S** (spec-side) · risk: low
- **Spec:** `components/record/SourceCard.jsx` (a single "view source on request" fallback card) · **Impl:** `src/components/TeardownSourceCard.astro`.
- Impl is **far ahead** — the spec is only impl *tier 4*. Impl adds: tier-1 committed scan-crop +
  redaction overlay, tier-2 live `<DocViewer>` embed (gated on `published`, #284), tier-3 extraction
  facsimile, annotation pins. → push: the spec card should be reframed to acknowledge the tiers.

### LeadCard · `reconcile impl←spec` (taxonomy) + `push impl→spec` · **M** · risk: med
- **Spec:** `components/record/LeadCard.jsx` · **Impl:** lead cards inlined in `…/leads.astro` (`.lead*`) + taxonomy in `lib/leads.ts` (1 call site).
- **Real drift:** confidence enum mismatch — spec `low/unanswered/withheld/**rumored**` vs impl
  `low/unanswered/withheld/**review**`. **Decide which.** Also the rail is keyed to **kind** in impl
  vs **confidence** in spec (different axis). Impl is ahead on the evidence `[tag]`, GH-issue link,
  stable id → push.
- **Extract vs align:** **extract** = a `LeadCard.astro` (self-contained, spec defines the props) —
  reconcile the enum first. **align** = align `LeadStatus`↔`confidence` in place. **Call sites = 1.**

### Timeline · `push impl→spec` (+ trivial) · **S** · risk: low
- **Spec:** `components/record/Timeline.jsx` · **Impl:** `src/components/Timeline.astro` (`.tl-*`).
- Impl is **ahead**: `.tl-walk` walk-chapter badge per event; derives `year` from `date`. Minor
  geometry drift (56px rail vs spec 64px) — low priority. (`.tl-dot` round → dead; nodes already
  square. `.tl-diamond` correctly stays a rotated square.) → push the walk badge.

## Page compositions — Directory tier (`ui_kits/directory/`)

All five `mapped`; the live pages are real-data-driven (32-site registry + bundle feeds) while the
comps use sample data — so most drift is **push impl→spec**, with a few genuinely-stale labels.

### DirectoryHome · `both` · **M** · risk: low
- **Impl:** `src/pages/index.astro` (`.dirh-*`).
- **Spec ahead:** two narrative sections — **"How to read the record"** (4-step) + **"The evidence
  grammar"** (5 EvidenceTag rows) — and a composition footer are **absent** from the live home (they
  may live at `/about` by design — confirm). **Impl ahead:** real stat derivation (spec hardcodes
  32/09/01/41; impl's 4th stat is "States" from the registry, not "Contributors"). Hero CTA #1 wording
  differs (spec "Explore the directory" vs impl "Explore the hypotheses →").

### Hypotheses · `push impl→spec` · **L** · risk: med
- **Impl:** `src/pages/research/hypotheses.astro` (`.dir-*`).
- Impl is **substantially ahead**: a per-lens framing panel + a **grouped cross-site scorecard**
  (bundle-driven), vs the spec's single flat 5-col table with ~2–4 hardcoded rows. Lens-switch
  differs (spec inline tab strip + `useState` vs impl no-JS radio cards). H1/H2/H3 taxonomy matches
  `directory.ts`. → push the live scorecard into the comp.

### NetworkChrome · `push impl→spec` (spec labels stale) · **S** · risk: low
- **Impl:** `src/components/Header.astro` (tier=network) + `lib/nav.ts`.
- **Spec is stale:** spec network tabs = **Report · Hypotheses · Submit · About▾**; the live IA
  (`NETWORK_TABS`, documented) = **Directory · Research · About▾** with **Submit moved to a
  right-cluster `+` pill** on both tiers + a mobile burger sheet. The live nav is authoritative →
  push (update the comp's labels + Submit affordance + mobile sheet).

### SiteSelector · `push impl→spec` (+ minor) · **M** · risk: low
- **Impl:** `src/components/Header.astro` (`.site-switcher`) + `src/components/SwitcherRow.astro`.
- Impl is **ahead**: a **State⇄Basin** group-by toggle (spec is basin-only flat) + **region bands** +
  per-row **facility lifecycle clock** + **tracking issue `#NNN`** + a **lock** affordance. Spec is
  ahead only on a live **filter input** (absent in impl — add if wanted). → mostly push.

### SubmitLead · `both` · **L** · risk: med
- **Impl:** `src/components/SubmitForm.astro` (`.submit-*`).
- **Spec ahead:** a two-column layout with a right **rail** (a 4-step "what happens to your lead"
  pipeline + a "this site right now" stat card), **4** lead types (adds "Answer a question" + splits
  "Tip/signal"), an "attach a file" affordance + a "credit me as a contributor" checkbox. **Impl
  ahead:** the real `cf-turnstile` widget (honest disabled/GH-issue fallback) + a ref-context banner.
  → reconcile the rail + lead types in; push the real endpoint/Turnstile up.

## Page compositions — Site tier (`ui_kits/site/`)

### SiteHome · `push impl→spec` · **M** · risk: low
- **Impl:** `…/american-sugar-creek-allen-co/index.astro` (the route-root adaptive home, **not**
  `site/index.astro` which is the corpus hub). Impl renders **Live only** — the spec's
  `investigation` phase is a documented deliberate cut (no per-site leads feed to populate it without
  fabricating). Impl **adds** a "just ask the record" `.home-ask` door + a real facility chip. → push.

### LeadsBoard · `push impl→spec` · **M** · risk: low
- **Impl:** `…/leads.astro` (`.leads-*`). Impl **adds** a whole right rail (CTA card + "how a lead
  closes" lifecycle + "recently closed"), a stats strip, per-lead status chip / evidence tag /
  GH-issue link / id, and the **`claim`** filter kind (spec filters = All/Questions/Redactions/
  Signals; impl adds Claims). → push.

### Profile · `push impl→spec` · **S** · risk: low
- **Impl:** `src/components/ProfileHeader.astro` rendered by `wiki/{entities,concepts,people}` pages.
  Spec is the **whole screen** (header + "records that mention this" compact-`RecordBlock` list); the
  impl component is the **header strip** only (the list is composed by the page). Header is on-parity;
  impl adds seen-in-walk + suggest-correction → push.

### RecordScreen · `push impl→spec` · **L** · risk: med
- **Impl:** `src/components/RecordTeardown.astro` rendered by `…/site/records/[group]/[id].astro`.
  Five-beat spine matches exactly. Impl is **ahead**: live-bundle binding (`verifyResolved`, the
  "● in the published bundle" badge) + **3 layouts** (split/scroll/annotated) + numbered margin pins.
  Spec is ahead only on its **left TOC rail + record-type variant switcher** — a *teaching device*
  (one screen showing the grammar across Cost/Air/NPDES), likely intentionally absent live. → push the
  live model; decide if the teaching rail stays a comp-only artifact.

### SiteChrome · `push impl→spec` (spec tabs stale) · **M** · risk: med
- **Impl:** `src/components/Header.astro` (tier=site) + `lib/nav.ts` (`SITE_TABS`).
- **Spec is stale:** spec site tabs = **The site · The record · The watershed** (flat 3); the live IA
  = **The site▾ (mega-menu) · The story · The record** — "The watershed"/"The economy" fold into the
  mega-menu, and Submit is the right-cluster `+` pill. The live `nav.ts` is authoritative + documented
  → push (update the comp's tabs + mega-menu + Submit).

### Watershed · `both` (+ coverage gap) · **S** · risk: low
- **Impl:** despite the filename, the `Watershed.jsx` comp is a **chronology/Timeline** screen
  (eyebrow "The watershed · chronology", renders `<Timeline>`) → maps to `…/timeline.astro`, **not**
  the interactive watershed hub. Impl reads the live `timeline` feed + adds walk anchors → push. Spec
  has a stronger H1/lead ("How the record was assembled — and withheld") worth reconciling in.
- **⚠ Coverage gap:** the **real** interactive watershed hub (`…/watershed/index.astro` — the
  `.hub-door` grid over hydrology/map/imagery/rsei islands) has **no spec** in the kit. Flag for
  whoever owns the watershed islands.

---

## Proposed Stage 2 ordering (reconciliation — gated on review of this audit)

Primitives underpin everything, so they go first. Each wave is reviewable per-component PRs on the
same chunked + dev-stack-review cadence as the token work; **repo class names are kept** (no
`wm-*` rename churn) — reconciliation targets values/structure/variants/taxonomy.

1. **Wave 1 — primitives (`reconcile impl←spec`; decide extract-vs-align per the table above):**
   EvidenceTag (taxonomy + variants — do first, it's load-bearing) · PhaseDot (color ramp) ·
   TextField (focus ring + mono label) · RadioCard (kind-picker) · Checkbox (net-new) ·
   Button · Eyebrow.
2. **Wave 2 — record-component reconciles:** SectionCard (**locked** door + badge chip) ·
   LeadCard (confidence taxonomy decision) · AnnotationPin (`active` ring) · ConnectChip (extract +
   `map` kind).
3. **Wave 3 — `push impl→spec` = the first DesignSync PUSH:** update the stale comps to the live
   site (chrome labels/IA, the richer scorecard/selector/leads/record-screen/home, the SourceCard
   tiers, the walk backlinks). This *is* the other deferred option — the audit shows ~14 components'
   "drift" is just the design project lagging the shipped site.

## The 6 primitives — extract vs align (decide per-primitive at review)

| primitive | extract (build a reusable primitive) | align (keep inline, fix values) | call sites |
|---|---|---|---|
| **Button** | `Button.astro` 4×3 variants/sizes, icon/href/disabled; fold `*-btn` | add modifiers + fix weight/border on `.btn` | 15 files / 11 `<button>` |
| **Eyebrow** | `Eyebrow.astro` (tone+as); collapse ~16 `*-eyebrow` | shared `.eyebrow` base composed by variants | 35 files |
| **PhaseDot** | `PhaseDot.astro` from `SiteStatus` | repoint ramp + strip pill fill | 5 files |
| **Checkbox** | `.checkbox` + `Checkbox.astro` | n/a (net-new) | 6 |
| **RadioCard** | `.radiocard` + `RadioCard.astro`; repoint SubmitForm | nudge leads-filter styling | 1 picker (5 surfaces) |
| **TextField** | `.field`/`TextField.astro` (optional/icon) | retune `.form input/textarea` tokens | 7 inputs |

## Coverage extension — charts · hydrology · Icon (added upstream 2026-06-23)

After the initial audit, the design project added **three new families** that close the coverage
gaps flagged below — mirrored + audited here. The token layer grew too: `tokens/colors.css` gained
the `--data-1..5` / `--data-withheld` / `--data-grid` / `--data-axis` **chart-series ramp**
("forest is data"); additive-only, so the live site (which `@import`s it) is unaffected.

### Charts (`components/charts/`) — 6/6 mapped to `src/components/charts/*.astro`

Repo charts are hand-rolled SSR Astro SVG (`lib/charts.ts` + `charts/*.astro`); geometry is a
near-literal match to the specs. **One uniform drift: palette tokenization** — the specs use the new
`--data-*` tokens, the repo hardcodes the equivalent hex (`FOREST`/`FOREST_TINTS`/`GRID`/… in
`charts.ts`; `site.css` defines zero `--data-*`). The impl is *ahead* in two places worth pushing up.

| spec | impl | drift | direction | effort |
|---|---|---|---|---|
| BarChart (orientation v/h) | BarChart.astro + RankedBarChart.astro | spec folds both into `orientation`; palette tokens; impl adds card-shell + `niceMax` axis | both | M |
| BulletBar | BulletChart.astro | palette; **impl ahead** — typed `evidence` register vs spec's raw `noteColor`; spec has per-row markers | both | S |
| Donut | DonutChart.astro | palette; spec adds `center`/`size`/per-slice color knobs | both | S |
| LineChart | LineChart.astro | palette; **impl ahead** — `refs` dashed reference/threshold lines (no spec concept) | push impl→spec | M |
| Sparkline | Sparkline.astro | palette; spec exposes `strokeWidth`/`dot`/`height` | reconcile impl←spec | S |
| StackedBar | StackedBar.astro | the one evidence-palette chart; **spec broader** — adds `gap`/`key` kinds + forest-series fallback (impl is 3 kinds) | reconcile impl←spec | M |

Net: `--data-*` palette adoption is the coherent reconcile; LineChart `refs` + BulletChart's
evidence-register are the two impl→spec pushes.

### Hydrology (`components/hydrology/`) — 0/6 have a dedicated impl (all missing-impl)

The watershed-hub gap the audit flagged, now spec'd. The repo renders draw-vs-low-flow as a
`BulletChart` + the `DilutionScreen` island — **none of the six domain charts exist.** `charts.ts:174`
already records that FDC / hydrograph / cumulative-vs-cap / drawdown await time-series the content
bundle doesn't carry. Palette/grammar (forest=data, amber=modeled, oxblood=limit) is consistent.

| spec | dedicated impl | build readiness | effort | risk |
|---|---|---|---|---|
| **Waterfall** (intake−returned=consumed) | none | **buildable now** — data in-bundle (`dilution.ts` cfs), pure SSR | M | low |
| **GaugeBar** (value vs cap + overage) | none | **buildable now** — value+cap in-bundle, plain HTML/CSS | S | low |
| FlowDurationCurve (log exceedance) | none | data-gated — needs an exceedance feed; best as an island | L | med |
| Hydrograph (bars/envelope) | none (`DilutionScreen` adjacent) | data-gated — needs a monthly-flow feed | L | med |
| ThresholdLine (cumulative vs cap) | none (`RefLine` seam partial) | data-gated — needs a cumulative acre-ft feed | M | med |
| AquiferSection (drawdown schematic) | none | **needs a modeled `[inference]` groundwater input the corpus lacks** | M/L | high |

Net: 2 buildable now (Waterfall, GaugeBar), 3 data-gated (need new `data/reference/hydrology` feeds +
bundle), 1 (AquiferSection) blocked on a citable drawdown model — **don't draw it without a cited
basis** (evidentiary discipline).

### Icon (`components/core/Icon`) — mapped to `Icon.astro` (+ `lib/icons.ts`)

~44/47 glyphs are byte-identical geometry. Real deltas: impl-missing **`dropdown`**, spec-missing
**`ask`** (the repo's Ask-affordance glyph), and a `verify-link`(spec) ≡ `external`(repo) **rename**.
Substantive drift: the **spec auto-colors semantic evidence icons** (in-component `SEMANTIC` map →
`--ev-*-fg`); `Icon.astro` is pure `currentColor` and relies on callers to colorize. Spec also exposes
`stroke`/`color`/`inherit`/`ICON_NAMES`; impl has `class`/`label`. → **both** (adopt the auto-coloring
+ add `dropdown`; push the `ask` glyph upstream). Effort S · risk low.

## Coverage notes

- **Unspecified in the design project (no spec to sync):** the **map/graph** islands (deck.gl
  `CorridorMap`/`DefenseNexusMap`/`EntityGraph`) and the economic/grid **simulators** (`EconLedger`,
  `GridLoad`, `MoneyFlow`, `EndUse`). Charts and the watershed hydrology surface are **now spec'd**
  (see the coverage extension above) — the remaining gap is the interactive map/sim islands.
- **Not mirrored (design-canvas artifacts, not components):** `explorations/hydrology/**` (a
  hydrology-viz working exploration) and `templates/social-kit/**`.
- **Not mirrored (by design):** `assets/brand/**` (binaries already in `frontend/public/`),
  `templates/social-kit/**` (a social-card template, not a component), `_ds_*` (generated).
- **Dead-source hygiene (optional, low priority):** the radius/shadow/round-dot declarations the
  flatten layer overrides could be removed so the source matches intent — but it's invisible and
  out of scope for reconciliation.

---

## DesignSync push log (Stage 2, Wave 3 — `impl→spec`)

The `push impl→spec` items round-trip upstream to the Watermark project in reviewable
batches (the DesignSync "incrementally, one component at a time — never a wholesale
replace" discipline). Each batch: edit the mirror spec → `finalize_plan` → `write_files`.

### Batch 1 — the stale chrome (2026-06-24) ✅ pushed
`ui_kits/directory/NetworkChrome.jsx` · `ui_kits/site/SiteChrome.jsx` (+ both kit
`index.html` preview harnesses). The two-tier chrome comps described navigation that no
longer exists; brought to the shipped IA (`src/lib/nav.ts`, authoritative): network tabs
`Report · Hypotheses · Submit · About` → **`Directory · Research · About▾`**; site tabs
`The site · The record · The watershed` → **`The site▾ (mega) · The story · The record`**;
and **Submit moved off the left tabs to a right-cluster `+` pill** on both tiers (watershed +
economy now fold into the "The site" mega rather than standing as tabs).

### Batch 2 — concrete component vocab (2026-06-24) ✅ pushed
The surgical, clearly-correct vocabulary the impls carry that the specs lacked — each a
discrete addition, no structural rewrite:
- **EvidenceTag** — added the **`filename`** kind (a source-file reference; the muted `open`
  palette, name passed via `label`), so the spec covers the repo's full six-kind taxonomy.
- **Icon** — added the **`ask`** glyph (the speech-bubble "conversational front door" / Ask
  topbar affordance) to `STROKE` + `ICON_NAMES` + the icon card's Navigation row.
- **LineChart** — added **`refs`**: dashed horizontal threshold lines (a disclosed cap, a
  design low flow, a target), clamped to the scale with a right-aligned label.
- **BulletBar** — added a typed **`evidence` + `evidenceNote`** register per row (colored from
  the evidence palette), preferred over the raw `note`/`noteColor`.
- **LeadCard** — renamed the 4th confidence **`rumored` → `review`** ("Under review") to match
  `lib/leads.ts` `LeadStatus`; also updated the two consumers that passed it (`SiteHome`,
  `LeadsBoard` sample data) so the enum stays consistent.

### Batch 3 (curated) — SiteSelector (2026-06-24) ✅ pushed
`ui_kits/directory/SiteSelector.jsx`. The one remaining **concretely-stale** comp — the other
`push impl→spec` page comps are "the comp is a simpler reference of a *richer* shipped page" and
were left as references (the user's call: fix what's misleading, preserve the rest). Brought the
selector up to the shipped switcher (`Header.astro` + `SwitcherRow.astro` + `lib/sites.ts`): a
**State⇄Basin group-by toggle** (Basin default), **region bands** in the basin lens (Maumee Basin /
The Two Miamis / Southeastern / Northeast), and a per-row **facility lifecycle clock** (a separate
clock from the build phase) + **tracking issue `#NNN`**, with the **lock** affordance in the foot
legend. **The push stops here** — batches 1–3 closed the concrete + clearly-stale tier; the richer
page-comp pushes are documented above but intentionally not made.
