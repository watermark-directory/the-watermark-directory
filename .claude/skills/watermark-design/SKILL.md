---
name: watermark-design
description: Use when designing, building, or reviewing any Watermark / BOSC user interface, page, component, mock, or visual — to stay on-brand with the Swiss 03 documentary design system (bone paper, one forest signal, square corners, no shadows, Archivo + IBM Plex Mono, the evidence grammar). Trigger on building or restyling frontend pages/components, creating mockups or prototypes, applying design tokens, or any "make this look right" / "is this on-brand" question. The full system + tokens live in frontend/design-system/ (mirrored from the Watermark Design System Claude Design project via DesignSync).
user-invocable: true
---

The **Watermark Design System** lives in-repo at **[`frontend/design-system/`](../../../frontend/design-system/)** —
the mirror of the Claude Design project (`dbe30a08-547c-442e-b4ac-81492fa5570f`), kept in sync
two ways via DesignSync. Start there:

- **[`frontend/design-system/readme.md`](../../../frontend/design-system/readme.md)** — the full
  guide: brand story, voice (CONTENT FUNDAMENTALS), VISUAL FOUNDATIONS (color/type/shape/motion),
  iconography, and the file index. Read this first.
- **[`frontend/design-system/tokens/`](../../../frontend/design-system/tokens/)** +
  `styles.css` — every design token as a CSS custom property (`--forest`, `--ink`, `--bone-*`,
  the `--ev-*` evidence grammar, the type scale, square-corner/flat discipline).
- **`frontend/design-system/components/`**, **`ui_kits/`**, **`guidelines/`** — React `.jsx`
  primitives (with `.d.ts` + `.prompt.md`), full-screen recreations, and specimen cards. These
  are pulled **incrementally** — if a path is empty, see `designsync.json` (`pending`) and pull it
  via the DesignSync tool.

The **live site** is Astro (`frontend/src/`); its `.astro` components in
`frontend/src/components/` are the *implementations* of these specs, and `frontend/src/styles/site.css`
carries the tokens under `--bosc-*` names. When designing for production, match those.

## The five things to never get wrong

1. **Square corners, no shadows.** `border-radius: 0` everywhere (except the rounded app-icon mask). Depth is hairline + rule weight, never elevation.
2. **One forest signal.** `#1f6f4a` (`--forest`) is the only accent — live, verified, links, the accent rail. Use it sparingly and meaningfully.
3. **Mono for every number.** IBM Plex Mono carries all figures, IDs, eyebrows, citations; Archivo carries language.
4. **Every figure wears an evidence tag.** verified / inference / open / scope-gap / key — the fixed `--ev-*` palette, never recolored.
5. **Voice: documentary, provenance-first.** "A lead, not a verdict." Show your work; never sell.

## Syncing the design system

To pull upstream changes into the mirror, or push local design-system edits back to Claude Design,
follow **[`frontend/design-system/DESIGNSYNC.md`](../../../frontend/design-system/DESIGNSYNC.md)**
(uses the `DesignSync` MCP tool; run `/design-login` first if the connector isn't authorized).
