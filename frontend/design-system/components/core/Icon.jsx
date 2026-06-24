import React from "react";

/* ============================================================
   Watermark Icon family — one stroke-based set on a 24px grid,
   1.7 stroke, round cap + join, fill:none, currentColor.
   Semantic (evidence) icons carry the evidence palette by default;
   everything else inherits the ink / forest of its context.
   ============================================================ */

// Stroked glyphs: inner geometry only. The wrapper supplies
// fill="none" stroke="currentColor" stroke-width=1.7 round caps.
const STROKE = {
  // --- navigation & chrome ---
  search: <><circle cx="10.5" cy="10.5" r="6.5" /><line x1="15.5" y1="15.5" x2="21" y2="21" /></>,
  menu: <><line x1="3.5" y1="7" x2="20.5" y2="7" /><line x1="3.5" y1="12" x2="20.5" y2="12" /><line x1="3.5" y1="17" x2="20.5" y2="17" /></>,
  home: <><path d="M4 11 L12 4 L20 11" /><path d="M6 9.7 V20 H18 V9.7" /><path d="M10 20 V14 H14 V20" /></>,
  chevron: <path d="M9 5 L16 12 L9 19" />,
  dropdown: <path d="M7 10 L12 15 L17 10" />,
  arrow: <><line x1="3.5" y1="12" x2="20" y2="12" /><path d="M13.5 5.5 L20 12 L13.5 18.5" /></>,
  "verify-link": <><path d="M13 4 H20 V11" /><line x1="20" y1="4" x2="11" y2="13" /><path d="M18 13.5 V20 H4 V6 H10.5" /></>,
  close: <><line x1="6" y1="6" x2="18" y2="18" /><line x1="18" y1="6" x2="6" y2="18" /></>,
  email: <><rect x="3.5" y="6" width="17" height="12" rx="2" /><path d="M4.2 7.6 L12 12.9 L19.8 7.6" /></>,
  notify: <><path d="M12 4 V5.6" /><path d="M7 16.5 V11 a5 5 0 0 1 10 0 V16.5" /><line x1="5" y1="16.5" x2="19" y2="16.5" /><path d="M9.8 19.4 a2.3 2.3 0 0 0 4.4 0" /></>,
  locked: <><rect x="5" y="10.5" width="14" height="9.5" rx="2" /><path d="M8 10.5 V8 a4 4 0 0 1 8 0 V10.5" /><circle cx="12" cy="14.5" r="1.25" /><line x1="12" y1="15.5" x2="12" y2="17.2" /></>,
  secure: <><path d="M12 3.5 L19 6 V11.4 C19 16 15.8 19.1 12 20.5 C8.2 19.1 5 16 5 11.4 V6 Z" /><path d="M9 12 L11.2 14.2 L15.2 9.9" /></>,
  // --- records & sources ---
  document: <><path d="M6 3 H14 L19 8 V21 H6 Z" /><path d="M14 3 V8 H19" /><line x1="9" y1="13" x2="16" y2="13" /><line x1="9" y1="16.5" x2="16" y2="16.5" /></>,
  scan: <><path d="M5 8.5 V5 H8.5" /><path d="M15.5 5 H19 V8.5" /><path d="M19 15.5 V19 H15.5" /><path d="M8.5 19 H5 V15.5" /><line x1="4" y1="12" x2="20" y2="12" /></>,
  corpus: <><path d="M12 3 L21 8 L12 13 L3 8 Z" /><path d="M3 12 L12 17 L21 12" /><path d="M3 16 L12 21 L21 16" /></>,
  archive: <><path d="M3.5 4.5 H20.5 V8.5 H3.5 Z" /><path d="M5 8.5 V20 H19 V8.5" /><line x1="10" y1="12" x2="14" y2="12" /></>,
  citation: <><path d="M9 5 H6 V19 H9" /><path d="M15 5 H18 V19 H15" /></>,
  link: <><path d="M9 15 H7 A3 3 0 0 1 7 9 H9" /><path d="M15 9 H17 A3 3 0 0 1 17 15 H15" /><line x1="8" y1="12" x2="16" y2="12" /></>,
  pages: <><path d="M9 6.5 V3.5 H15 L19 7.5 V18" /><path d="M5 8.5 H12 L16 12.5 V21 H5 Z" /><path d="M12 8.5 V12.5 H16" /></>,
  // --- entities & places ---
  entity: <><path d="M5 20.5 V8 L12.5 4.5 V20.5" /><path d="M12.5 11 L19 13 V20.5" /><line x1="3.5" y1="20.5" x2="20.5" y2="20.5" /><line x1="7.7" y1="10" x2="10" y2="10" /><line x1="7.7" y1="14" x2="10" y2="14" /><line x1="15" y1="16.5" x2="16.7" y2="16.5" /></>,
  person: <><circle cx="12" cy="8" r="3.6" /><path d="M5.5 20 a6.5 6.5 0 0 1 13 0" /></>,
  place: <><path d="M12 21 C12 21 18.5 14 18.5 9 A6.5 6.5 0 0 0 5.5 9 C5.5 14 12 21 12 21 Z" /><circle cx="12" cy="9" r="2.4" /></>,
  watershed: <><path d="M3.5 8 q4 -3 8 0 t8 0" /><path d="M3.5 13 q4 -3 8 0 t8 0" /><path d="M3.5 18 q4 -3 8 0 t8 0" /></>,
  timeline: <><line x1="7" y1="3.5" x2="7" y2="20.5" /><circle cx="7" cy="8" r="2.3" /><circle cx="7" cy="15.5" r="2.3" /><line x1="11" y1="8" x2="18" y2="8" /><line x1="11" y1="15.5" x2="16" y2="15.5" /></>,
  concept: <><circle cx="6" cy="8" r="2.2" /><circle cx="17.5" cy="7" r="2.2" /><circle cx="13.5" cy="17.5" r="2.2" /><line x1="7.9" y1="9" x2="12.3" y2="15.9" /><line x1="8.1" y1="7.7" x2="15.3" y2="7.2" /></>,
  map: <><path d="M9 4.5 L3.5 6.5 V19.5 L9 17.5 L15 19.5 L20.5 17.5 V4.5 L15 6.5 L9 4.5 Z" /><line x1="9" y1="4.5" x2="9" y2="17.5" /><line x1="15" y1="6.5" x2="15" y2="19.5" /></>,
  // --- actions ---
  download: <><line x1="12" y1="4" x2="12" y2="15.5" /><path d="M7.5 11 L12 15.5 L16.5 11" /><path d="M5 18.5 H19" /></>,
  attach: <path d="M15.5 7.2 L7.6 15.1 a3.2 3.2 0 0 0 4.5 4.5 L19.7 12 a5.3 5.3 0 0 0 -7.5 -7.5 L4.6 12.1" />,
  send: <><path d="M21 3 L3 10.5 L10.5 13.5 L13.5 21 Z" /><line x1="21" y1="3" x2="10.5" y2="13.5" /></>,
  correction: <><path d="M5 19 L5 15.5 L16 4.5 L19.5 8 L8.5 19 Z" /><line x1="14" y1="6.5" x2="17.5" y2="10" /></>,
  filter: <path d="M4 5.5 H20 L14 12.5 V19 L10 21 V12.5 Z" />,
  copy: <><rect x="8.5" y="8.5" width="11" height="12" rx="2" /><path d="M15.5 8.5 V6 A1.5 1.5 0 0 0 14 4.5 H6 A1.5 1.5 0 0 0 4.5 6 V16 A1.5 1.5 0 0 0 6 17.5 H8.5" /></>,
  submit: <><line x1="12" y1="20" x2="12" y2="8.5" /><path d="M7.5 13 L12 8.5 L16.5 13" /><line x1="5" y1="5" x2="19" y2="5" /></>,
  // --- data & figures ---
  chart: <><line x1="4" y1="20" x2="20.5" y2="20" /><rect x="6" y="11" width="3" height="9" /><rect x="11" y="6.5" width="3" height="13.5" /><rect x="16" y="14" width="3" height="6" /></>,
  trend: <><polyline points="4 16 9 11 13 14 20 6" /><path d="M15.5 6 H20 V10.5" /></>,
  measure: <><rect x="3.5" y="8.5" width="17" height="7" rx="1" /><line x1="7" y1="8.5" x2="7" y2="11.5" /><line x1="10.5" y1="8.5" x2="10.5" y2="11.5" /><line x1="14" y1="8.5" x2="14" y2="11.5" /><line x1="17.5" y1="8.5" x2="17.5" y2="11.5" /></>,
  // --- footprint & measures ---
  cost: <><circle cx="12" cy="12" r="8.5" /><path d="M14.6 9.2 C14 8.2 13 7.7 12 7.7 c-1.6 0 -2.7 0.9 -2.7 2.1 0 2.7 5.4 1.4 5.4 4.1 0 1.2 -1.1 2.1 -2.7 2.1 -1.1 0 -2.1 -0.5 -2.7 -1.5" /><line x1="12" y1="5.8" x2="12" y2="7.7" /><line x1="12" y1="16.3" x2="12" y2="18.2" /></>,
  power: <path d="M13 3 L5.5 13.5 H11 L10 21 L18.5 10 H12.5 Z" />,
  discharge: <><path d="M12 3.4 C12 3.4 6 10 6 14.5 a6 6 0 0 0 12 0 C18 10 12 3.4 12 3.4 Z" /><path d="M9.6 14.8 a2.5 2.5 0 0 0 2.3 2.3" /></>,
  // --- evidence & provenance (semantic — see SEMANTIC below) ---
  verified: <><circle cx="12" cy="12" r="8.5" /><path d="M8.3 12.4 L11 15 L15.7 9.5" /></>,
  inference: <><circle cx="12" cy="12" r="8.5" /><path d="M7.7 12.8 q2.2 -2.8 4.3 0 t4.3 0" /></>,
  open: <circle cx="12" cy="12" r="8.5" strokeDasharray="3 3.4" />,
  "scope-gap": <><line x1="6" y1="3" x2="6" y2="21" /><path d="M6 4.5 H18 L15 8.7 L18 13 H6" /></>,
  excerpt: <><path d="M6 9 H10 V13 C10 15.2 8.6 16.4 6.8 16.6" /><path d="M14 9 H18 V13 C18 15.2 16.6 16.4 14.8 16.6" /></>,
  "key-figure": <path d="M12 3.5 L14.3 9.2 L20.5 9.6 L15.7 13.6 L17.3 19.6 L12 16.2 L6.7 19.6 L8.3 13.6 L3.5 9.6 L9.7 9.2 Z" />,
};

// Filled glyphs — the two exceptions to the stroke rule.
const FILLED = {
  // redaction — solid ink bars, shown in place
  redaction: <><rect x="3.5" y="7" width="17" height="3.4" rx="0.8" /><rect x="3.5" y="13.6" width="11.5" height="3.4" rx="0.8" /></>,
  // repo — GitHub's own octocat, the lone foreign mark. Never redrawn.
  repo: <path d="M12 .8C5.6.8.5 6 .5 12.3c0 5.1 3.3 9.4 7.9 10.9.6.1.8-.2.8-.5v-2c-3.2.7-3.9-1.5-3.9-1.5-.5-1.3-1.3-1.7-1.3-1.7-1-.7.1-.7.1-.7 1.2.1 1.8 1.2 1.8 1.2 1 1.8 2.7 1.3 3.4 1 .1-.7.4-1.3.7-1.6-2.6-.3-5.3-1.3-5.3-5.7 0-1.3.5-2.3 1.2-3.1-.1-.3-.5-1.5.1-3 0 0 1-.3 3.2 1.2a11 11 0 0 1 5.8 0c2.2-1.5 3.2-1.2 3.2-1.2.6 1.6.2 2.7.1 3 .8.8 1.2 1.8 1.2 3.1 0 4.4-2.7 5.4-5.3 5.7.4.4.8 1.1.8 2.2v3.2c0 .3.2.7.8.5 4.6-1.5 7.9-5.8 7.9-10.9C23.5 6 18.4.8 12 .8Z" />,
};

// Semantic icons are fixed to the evidence palette — never recolored to ink
// unless the caller explicitly passes `color` or `inherit`.
const SEMANTIC = {
  verified: "var(--ev-verified-fg)",
  inference: "var(--ev-inference-fg)",
  open: "var(--ev-open-fg)",
  "scope-gap": "var(--ev-gap-fg)",
  "key-figure": "var(--ev-key-fg)",
};

export const ICON_NAMES = [...Object.keys(STROKE), ...Object.keys(FILLED)];

/**
 * Icon — any glyph in the Watermark family, drawn on a 24px grid.
 * Inherits `currentColor` by default; semantic icons keep their evidence
 * color unless you pass `color` or `inherit`.
 */
export function Icon({ name = "document", size = 24, stroke = 1.7, color, inherit = false, title, style, ...rest }) {
  const filled = name in FILLED;
  const inner = filled ? FILLED[name] : STROKE[name];
  if (!inner) {
    if (typeof console !== "undefined") console.warn(`Icon: unknown name "${name}"`);
    return null;
  }
  const semanticColor = !inherit && !color ? SEMANTIC[name] : undefined;
  const resolved = color || semanticColor; // undefined → currentColor
  const common = {
    viewBox: "0 0 24 24", width: size, height: size,
    role: title ? "img" : "presentation", "aria-hidden": title ? undefined : true,
    style: { display: "block", flex: "0 0 auto", color: resolved, ...style },
    ...rest,
  };
  if (filled) {
    return <svg {...common} fill={resolved || "currentColor"} stroke="none">{title ? <title>{title}</title> : null}{inner}</svg>;
  }
  return (
    <svg {...common} fill="none" stroke={resolved || "currentColor"} strokeWidth={stroke} strokeLinecap="round" strokeLinejoin="round">
      {title ? <title>{title}</title> : null}{inner}
    </svg>
  );
}
