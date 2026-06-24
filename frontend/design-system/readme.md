# Watermark — Design System

> A flat, hard-grid documentary system: bone paper, ink hairlines, square corners,
> no shadows. One forest signal carries status; the **evidence grammar** carries
> meaning. Type is **Archivo** for prose and **IBM Plex Mono** for every load-bearing
> figure.

## What Watermark is

**Watermark** is a browsable, citable, **provenance-first** public-records platform.
It assembles the public record behind a contested hyperscale **data-center build-out** —
**32 sites across 9 basins** in Ohio — each a point where compute meets ground, water,
and power. This effort is internally called **The Watershed Project**. The product is
assembled entirely from documents the developer didn't write (deeds, permits, transfers,
filings), and built in the open with the people who live near each site.

The platform has two tiers:

- **The network (directory)** — `watermark.directory`. The index of all sites, read three
  ways (Water & Power · Defense & Federal · Corporate & Economic). Tabs: Report, Hypotheses,
  Submit, About.
- **A site** — e.g. *Lima (codename BOSC)*. Each site is one investigation that climbs a curve
  from **Under investigation → Corroborating → Nearly complete → Live** as contributions land.
  Inside: The site, The record, The watershed.

The reading model is doctrinal: **source → structured read → meaning → verify.** Nothing is
asserted that can't be traced back a step. A lead becomes a record only when a source
corroborates it; until then it is **labeled as inference.** Redactions are *shown, not hidden.*

### Sources this system was built from

- **Foundation design project** (Watermark prototype, Design Components): project
  `6422c739-9076-4b5a-baf1-0be1b04b3751` — ~40 `.dc.html` screens (Site Home, Directory Home,
  Record Block, Record Screen, Profiles, Timeline, Site Selector, Chrome, Brand lockups, the
  in-product Design System & Icon Set artboards). The brand, colors, type, evidence grammar,
  components, and icon family are all lifted directly from these.
- **Brand assets**: `brand/` favicons + app icons from that project, copied into `assets/brand/`.

No external Figma or codebase was attached — the foundation project's own DCs are the source
of truth, and they are unusually complete.

---

## CONTENT FUNDAMENTALS — how Watermark writes

The voice is a **documentary editor**: plain, exact, quietly serious. It never sells, never
spins, never gets cute. It earns trust by showing its work.

- **Address.** Mostly **you** ("Help prove it", "follow any citation to its source", "Know
  something about this site?"). The maintainers are **we / the record team** — collective and
  modest, never an "I", never a named hero.
- **Verbs over adjectives.** "Land is moving and shells are forming." "The record was made thin
  on purpose." Action and specificity carry the weight; hype words ("revolutionary", "powerful")
  never appear.
- **A lead, not a verdict.** This is the load-bearing phrase. Unconfirmed material is *published*
  but always framed as open: *"We treat every submission as a lead, not a verdict."* "Rumored",
  "Unanswered", "Withheld", "inference" are used as honest status, not hedging.
- **Casing.** Sentence case for all headlines and body. **Mono UPPERCASE** only for eyebrows,
  part-labels, table headers, and status pills (`START HERE`, `ACROSS THE NETWORK`,
  `PROVENANCE-FIRST`). Never title-case headlines.
- **Numbers are sacred and they are mono.** Every figure appears with its source and an evidence
  tag. `$14,223,081`, `24.3×`, `0.2 cfs`, `pp. 317–328`. Precision *is* the message — a number
  that exact is the tell.
- **Documentary register, short sentences.** "A Delaware shell. Withheld land prices. Backup
  generators by the hundred." Fragments are allowed for cadence. Em-dashes and mid-sentence
  asides are common.
- **Tone words it owns:** record, source, lead, corroborate, provenance, the walk, the file,
  open case, draft, gap, the build-out. Words it avoids: dashboard, insights, AI-powered, users,
  seamless, leverage.
- **Emoji:** essentially none. The one exception in the product is a 🔒 on locked sections and a
  ⚠ before a "Gaps in the record" warning — functional glyphs, not decoration. Arrows (→, ›, ↗, ↩)
  and the green period are the punctuation that carries personality.
- **Headline examples (lift the cadence, not the words):**
  - "The build-out, on the public record."
  - "We think a data center is coming here. Help prove it."
  - "A 340-acre data center, built to be invisible."
  - "Found an error, or know something we don't?"

---

## VISUAL FOUNDATIONS

**The whole system in one line:** documentary paper, one ink, one green, square corners, hairlines
instead of shadows, mono for every number.

### Color
- **Bone paper.** The field is warm off-white. The page is `#e9e6dc`; surfaces/cards are `#f5f2ea`;
  sunk wells (footers, provenance strips) `#efece2`; faint zebra bands `#ece8dc`. Bone is *warm* —
  never a cool gray.
- **Ink, not black.** Text and frames are `#16201a` (a near-black green-black), stepping down
  through prose `#3a4036`, muted `#566159`, faint `#8c9389`, ghost `#a8a596`.
- **One signal: forest `#1f6f4a`.** Live, verified, links, the accent rail, the affirmative
  action. Used *sparingly* — when forest appears, it means something. `#3d8f63` is the brighter
  wordmark period; `#7fb89a` is forest legible on the ink bar.
- **The evidence palette is fixed and never recolored:** verified (forest), inference (amber
  `#9a6a14`), open (muted), scope-gap/redaction (oxblood `#7a2230`), key figure (highlight
  `#f3e7c4`). These are *semantics*, not decoration.

### Type
- **Archivo** carries all prose and display — heavy (800) and tightly tracked (−1 to −2px) at large
  sizes; 400 at body with `line-height: 1.55` and `text-wrap: pretty`.
- **IBM Plex Mono** carries **every load-bearing figure, eyebrow, ID, code, and citation.** The split
  is doctrinal: language is Archivo; numbers-that-matter and provenance are mono.
- Eyebrows are mono, uppercase, 11px, 1.6px tracking. On-screen text floors at ~13px; figures go
  large (30–52px) and tuck in with negative tracking.

### Shape, depth & borders
- **Square corners everywhere — `border-radius: 0`.** Pills, chips, badges, buttons, cards, inputs
  are all rectangles. The *sole* exception is the rounded PWA app-icon mask (14px).
- **No shadows. Ever.** The system is flat by doctrine. Depth comes only from **hairline + rule
  weight**: 1px hairline (`#dcd8cc`) divides *within* a panel; a 2px ink rule frames it and marks
  the active edge; a 3–4px **forest rail** on the left edge signals a record or a lead.
- **Cards** = `#f5f2ea` surface + 1px `#dcd8cc` hairline, square, no shadow. A "primary" panel uses
  a full 1px or 2px *ink* border instead of the hairline.

### Backgrounds & imagery
- No gradients, no photography-as-hero, no illustration. The background is paper. The only "texture"
  in the system is the **striped document-scan fill** used in the source-excerpt fallback
  (`repeating-linear-gradient` of two bone tones) — it stands in for a scan that's available on
  request. Redactions are drawn as solid ink bars, shown in place.

### Motion, hover & press
- **Restrained.** Transitions are `0.15s cubic-bezier(0.4,0,0.2,1)`. No bounce, no large movement.
- **Hover:** cards lift `translateY(-2px)` and/or shift their hairline border to `--forest-line`;
  list rows tint to `#e8e4d8`/`#e4ece4`; ghost buttons shift their outline toward forest; links
  underline or brighten. Nav tabs carry an `inset 0 -3px 0` underline when active.
- **Press / focus:** a square forest focus ring `0 0 0 2px rgba(31,111,74,0.3)` — never a glow,
  never rounded.

### The global chrome (the ink bar)
- One bar, ink `#16201a`, 56px, square. **Two tiers:** at the *network* level the left tabs are the
  directory's pages; *inside a site* they become the site's pages and a **site chip** (e.g.
  `Lima · BOSC`) appears as the breadcrumb. The wordmark always returns to the network. Platform
  tools (Docs, Wiki, Ask, Search ⌘K) sit on the right and never change. On the ink bar, forest
  reads as `#7fb89a` and dividers/chips use low-opacity white.

### Layout rules
- Centered column, generous outer margin, `max-width` ~1180px for product views, ~840px for prose.
- Hard grid: tables and door-grids use 1px hairline dividers with negative-margin tricks so the
  outer frame stays a clean rule. Zebra rows alternate `transparent` / `#ece8dc`.

---

## ICONOGRAPHY

Watermark ships its **own** stroke-based icon family — there is no icon-font dependency and no
third-party set. See the in-product **Icon Set** artboard (foundation project) for the full grammar.

- **One family, one weight.** Drawn on a **24px grid**, **1.7 stroke**, **round cap and join**,
  `fill: none`. Optical, not mechanical. The bracket-square caps are reserved for the logo only.
- **`currentColor` always.** No baked-in fills — every icon inherits the ink, forest, or evidence
  color of its row. This is why icons "just work" in any context.
- **Semantic icons are fixed to the evidence palette** and never recolored to ink: verified
  (forest check-in-circle), inference (amber tilde-in-circle), open (dashed circle), scope-gap
  (oxblood flag), redaction (solid ink bars), key figure (highlight star).
- **Coverage** (all in the Icon Set artboard): search, menu, home, chevron, dropdown, arrow,
  verify-link (↗ box), close, email, notify, locked, secure; document, scan, corpus, archive,
  citation, link, pages; entity, person, place, watershed, timeline, concept, map; download,
  attach, send, correction, filter, copy, submit; chart, trend, measure; cost, power, discharge.
- **The one foreign mark:** the **repo** glyph is GitHub's own filled octocat — the lone filled,
  non-stroke mark in the system, used *only* for the source-repo link, never redrawn in our stroke.
- **Unicode as glyph.** A handful of typographic glyphs do icon duty inline: → › ↗ ↩ ⤓ ✕ ✎ ⚠ 🔒 ▾▴.
  Treat them as part of the type, set in the surrounding ink/forest color.

> **How to use icons here:** the foundation Icon Set draws each glyph as inline `<svg>` at 24×24,
> stroke 1.7, `stroke="currentColor"`. When building screens, inline those SVGs (copy from the Icon
> Set artboard) rather than hand-rolling new ones, and let color come from the parent. If you must
> reach for a CDN set, **Lucide** is the closest match (24px, ~1.75 stroke, round join) — flag any
> substitution.

---

## INDEX — what's in this system

### Root
- **`styles.css`** — the entry point consumers link. `@import` lines only.
- **`tokens/`** — `fonts.css` (Archivo + IBM Plex Mono via Google Fonts), `colors.css`,
  `typography.css`, `spacing.css` (radii/borders/motion). All `--*` custom properties.
- **`SKILL.md`** — portable Agent-Skill front-matter + usage.
- **`assets/brand/`** — favicon (SVG + PNG sizes) and app icons.

### Components (`window.WatermarkDesignSystem_dbe30a.*`)
- **`components/core/`** — `Button`, `EvidenceTag`, `PhaseDot`, `ConnectChip`, `Eyebrow`,
  `AnnotationPin`.
- **`components/record/`** — `RecordBlock`, `FigureStat`, `SourceCard`, `LeadCard`, `SectionCard`,
  `Timeline`, `ProfileHeader`.
- **`components/forms/`** — `TextField`, `Checkbox`, `RadioCard`.

Each has a `.d.ts` (props contract), a `.prompt.md` (what/when + example), and the directory's
`*.card.html` thumbnail.

### Foundation cards (`guidelines/`)
Colors (bone, ink, forest, evidence), Type (display, body, mono), Spacing (corners & rules, scale),
Brand (wordmark, the mark). These render in the Design System tab.

### UI kits (`ui_kits/`)
- **`directory/`** — the network tier: the directory home, the grouped site selector, the hypotheses
  index, and the Submit-a-Lead form. Interactive click-through.
- **`site/`** — the site tier: the adaptive site home (four phases), a record screen with three
  record-type variants (cost estimate · CBI-redacted air permit · NPDES water-screen), the leads
  board, a wiki profile, and the watershed chronology (timeline).

---

## Notes & caveats

- **Fonts are pulled from Google Fonts via `@import`** (in `tokens/fonts.css`), not self-hosted, so
  the compiler reports 0 bundled `@font-face`. Both Archivo and IBM Plex Mono are the *real* brand
  faces — this is a CDN delivery choice, not a substitution. If you need fully offline/self-hosted
  binaries, drop the `.woff2` files in `assets/fonts/` and swap the `@import` for `@font-face` rules.
- The icon family is **recreated inline as SVG** from the foundation Icon Set artboard, not shipped as
  a sprite. Copy glyphs from there when building.
