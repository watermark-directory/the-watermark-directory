---
name: watermark-design
description: Use this skill to generate well-branded interfaces and assets for Watermark — the provenance-first public-records platform (internally "The Watershed Project") — either for production or throwaway prototypes/mocks. Contains essential design guidelines, colors, type, fonts, assets, and UI kit components for prototyping.
user-invocable: true
---

Read the `readme.md` file within this skill, and explore the other available files.

If creating visual artifacts (slides, mocks, throwaway prototypes, etc), copy assets out and create static HTML files for the user to view. If working on production code, you can copy assets and read the rules here to become an expert in designing with this brand.

If the user invokes this skill without any other guidance, ask them what they want to build or design, ask some questions, and act as an expert designer who outputs HTML artifacts _or_ production code, depending on the need.

## Fast orientation

- **`readme.md`** — the full design guide: brand story, CONTENT FUNDAMENTALS (voice), VISUAL FOUNDATIONS (color/type/shape/motion), ICONOGRAPHY, and the file index. Read this first.
- **`styles.css`** — the one stylesheet to link. It `@import`s `tokens/*` (colors, typography, spacing, fonts). All design tokens are CSS custom properties under `:root`.
- **`components/`** — React UI primitives, each with a `.d.ts` (props) and `.prompt.md` (usage). Core: `Button`, `EvidenceTag`, `PhaseDot`, `ConnectChip`, `Eyebrow`, `AnnotationPin`. Record: `RecordBlock`, `FigureStat`, `SourceCard`, `LeadCard`, `SectionCard`.
- **`ui_kits/`** — full-screen recreations: `directory/` (network tier) and `site/` (site tier).
- **`guidelines/`** — foundation specimen cards.
- **`assets/brand/`** — favicons + app icons.

## The five things to never get wrong

1. **Square corners, no shadows.** `border-radius: 0` everywhere (except the rounded app-icon mask). Depth is hairline + rule weight, never elevation.
2. **One forest signal.** `#1f6f4a` is the only accent; use it sparingly and meaningfully (live, verified, links, accent rail).
3. **Mono for every number.** IBM Plex Mono carries all figures, IDs, eyebrows, and citations; Archivo carries language.
4. **Every figure wears an evidence tag.** verified / inference / open / scope-gap / key — fixed palette, never recolored.
5. **Voice: documentary, provenance-first.** "A lead, not a verdict." Show your work; never sell.

When in doubt, open the matching `.prompt.md` or the `ui_kits/` screen and copy the pattern.
