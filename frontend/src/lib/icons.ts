/**
 * The BOSC icon set (design-system extension): one stroke-based family on a 24px
 * grid, 1.7 weight, round cap/join, `currentColor`. Square caps stay reserved for
 * the logo mark (`components/Logo.astro`). Evidence/provenance icons carry the
 * semantic palette wherever they appear — they're used inside semantic-colored
 * contexts (the `currentColor` inherits the right color); never recolor them to ink.
 *
 * Each entry is the inner SVG of a `0 0 24 24` viewBox; `<Icon>` wraps it. `filled`
 * icons paint with `fill="currentColor"` and no stroke (the redaction bar).
 */
export interface IconDef {
  body: string;
  /** Painted with fill, not stroke (e.g. the redaction bar). */
  filled?: boolean;
}

export const ICONS: Record<string, IconDef> = {
  // ---- navigation & chrome ----
  search: { body: '<circle cx="10.5" cy="10.5" r="6.5"/><line x1="15.5" y1="15.5" x2="21" y2="21"/>' },
  menu: {
    body: '<line x1="3.5" y1="7" x2="20.5" y2="7"/><line x1="3.5" y1="12" x2="20.5" y2="12"/><line x1="3.5" y1="17" x2="20.5" y2="17"/>',
  },
  home: { body: '<path d="M4 11 L12 4 L20 11"/><path d="M6 9.7 V20 H18 V9.7"/><path d="M10 20 V14 H14 V20"/>' },
  chevron: { body: '<path d="M9 5 L16 12 L9 19"/>' },
  arrow: { body: '<line x1="3.5" y1="12" x2="20" y2="12"/><path d="M13.5 5.5 L20 12 L13.5 18.5"/>' },
  external: { body: '<path d="M13 4 H20 V11"/><line x1="20" y1="4" x2="11" y2="13"/><path d="M18 13.5 V20 H4 V6 H10.5"/>' },
  close: { body: '<line x1="6" y1="6" x2="18" y2="18"/><line x1="18" y1="6" x2="6" y2="18"/>' },

  // ---- records & sources ----
  document: {
    body: '<path d="M6 3 H14 L19 8 V21 H6 Z"/><path d="M14 3 V8 H19"/><line x1="9" y1="13" x2="16" y2="13"/><line x1="9" y1="16.5" x2="16" y2="16.5"/>',
  },
  scan: {
    body: '<path d="M5 8.5 V5 H8.5"/><path d="M15.5 5 H19 V8.5"/><path d="M19 15.5 V19 H15.5"/><path d="M8.5 19 H5 V15.5"/><line x1="4" y1="12" x2="20" y2="12"/>',
  },
  corpus: { body: '<path d="M12 3 L21 8 L12 13 L3 8 Z"/><path d="M3 12 L12 17 L21 12"/><path d="M3 16 L12 21 L21 16"/>' },
  archive: { body: '<path d="M3.5 4.5 H20.5 V8.5 H3.5 Z"/><path d="M5 8.5 V20 H19 V8.5"/><line x1="10" y1="12" x2="14" y2="12"/>' },
  citation: { body: '<path d="M9 5 H6 V19 H9"/><path d="M15 5 H18 V19 H15"/>' },
  link: { body: '<path d="M9 15 H7 A3 3 0 0 1 7 9 H9"/><path d="M15 9 H17 A3 3 0 0 1 17 15 H15"/><line x1="8" y1="12" x2="16" y2="12"/>' },
  pages: { body: '<path d="M9 6.5 V3.5 H15 L19 7.5 V18"/><path d="M5 8.5 H12 L16 12.5 V21 H5 Z"/><path d="M12 8.5 V12.5 H16"/>' },

  // ---- evidence & provenance (semantic palette — never recolored to ink) ----
  verified: { body: '<circle cx="12" cy="12" r="8.5"/><path d="M8.3 12.4 L11 15 L15.7 9.5"/>' },
  inference: { body: '<circle cx="12" cy="12" r="8.5"/><path d="M7.7 12.8 q2.2 -2.8 4.3 0 t4.3 0"/>' },
  open: { body: '<circle cx="12" cy="12" r="8.5" stroke-dasharray="3 3.4"/>' },
  redaction: {
    body: '<rect x="3.5" y="7" width="17" height="3.4" rx="0.8"/><rect x="3.5" y="13.6" width="11.5" height="3.4" rx="0.8"/>',
    filled: true,
  },
  "scope-gap": { body: '<line x1="6" y1="3" x2="6" y2="21"/><path d="M6 4.5 H18 L15 8.7 L18 13 H6"/>' },
  excerpt: {
    body: '<path d="M6 9 H10 V13 C10 15.2 8.6 16.4 6.8 16.6"/><path d="M14 9 H18 V13 C18 15.2 16.6 16.4 14.8 16.6"/>',
  },

  // ---- entities & places ----
  entity: {
    body: '<path d="M5 20.5 V8 L12.5 4.5 V20.5"/><path d="M12.5 11 L19 13 V20.5"/><line x1="3.5" y1="20.5" x2="20.5" y2="20.5"/><line x1="7.7" y1="10" x2="10" y2="10"/><line x1="7.7" y1="14" x2="10" y2="14"/><line x1="15" y1="16.5" x2="16.7" y2="16.5"/>',
  },
  person: { body: '<circle cx="12" cy="8" r="3.6"/><path d="M5.5 20 a6.5 6.5 0 0 1 13 0"/>' },
  place: { body: '<path d="M12 21 C12 21 18.5 14 18.5 9 A6.5 6.5 0 0 0 5.5 9 C5.5 14 12 21 12 21 Z"/><circle cx="12" cy="9" r="2.4"/>' },
  watershed: { body: '<path d="M3.5 8 q4 -3 8 0 t8 0"/><path d="M3.5 13 q4 -3 8 0 t8 0"/><path d="M3.5 18 q4 -3 8 0 t8 0"/>' },
  timeline: {
    body: '<line x1="7" y1="3.5" x2="7" y2="20.5"/><circle cx="7" cy="8" r="2.3"/><circle cx="7" cy="15.5" r="2.3"/><line x1="11" y1="8" x2="18" y2="8"/><line x1="11" y1="15.5" x2="16" y2="15.5"/>',
  },
  concept: {
    body: '<circle cx="6" cy="8" r="2.2"/><circle cx="17.5" cy="7" r="2.2"/><circle cx="13.5" cy="17.5" r="2.2"/><line x1="7.9" y1="9" x2="12.3" y2="15.9"/><line x1="8.1" y1="7.7" x2="15.3" y2="7.2"/>',
  },

  // ---- actions ----
  download: { body: '<line x1="12" y1="4" x2="12" y2="15.5"/><path d="M7.5 11 L12 15.5 L16.5 11"/><path d="M5 18.5 H19"/>' },
  attach: { body: '<path d="M15.5 7.2 L7.6 15.1 a3.2 3.2 0 0 0 4.5 4.5 L19.7 12 a5.3 5.3 0 0 0 -7.5 -7.5 L4.6 12.1"/>' },
  send: { body: '<path d="M21 3 L3 10.5 L10.5 13.5 L13.5 21 Z"/><line x1="21" y1="3" x2="10.5" y2="13.5"/>' },
  correction: { body: '<path d="M5 19 L5 15.5 L16 4.5 L19.5 8 L8.5 19 Z"/><line x1="14" y1="6.5" x2="17.5" y2="10"/>' },
  filter: { body: '<path d="M4 5.5 H20 L14 12.5 V19 L10 21 V12.5 Z"/>' },
  copy: {
    body: '<rect x="8.5" y="8.5" width="11" height="12" rx="2"/><path d="M15.5 8.5 V6 A1.5 1.5 0 0 0 14 4.5 H6 A1.5 1.5 0 0 0 4.5 6 V16 A1.5 1.5 0 0 0 6 17.5 H8.5"/>',
  },

  // ---- data & figures ----
  chart: {
    body: '<line x1="4" y1="20" x2="20.5" y2="20"/><rect x="6" y="11" width="3" height="9"/><rect x="11" y="6.5" width="3" height="13.5"/><rect x="16" y="14" width="3" height="6"/>',
  },
  trend: { body: '<polyline points="4 16 9 11 13 14 20 6"/><path d="M15.5 6 H20 V10.5"/>' },
  measure: {
    body: '<rect x="3.5" y="8.5" width="17" height="7" rx="1"/><line x1="7" y1="8.5" x2="7" y2="11.5"/><line x1="10.5" y1="8.5" x2="10.5" y2="11.5"/><line x1="14" y1="8.5" x2="14" y2="11.5"/><line x1="17.5" y1="8.5" x2="17.5" y2="11.5"/>',
  },
  "key-figure": {
    body: '<path d="M12 3.5 L14.3 9.2 L20.5 9.6 L15.7 13.6 L17.3 19.6 L12 16.2 L6.7 19.6 L8.3 13.6 L3.5 9.6 L9.7 9.2 Z"/>',
  },
};

export type IconName = keyof typeof ICONS;
