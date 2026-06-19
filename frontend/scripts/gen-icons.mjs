/**
 * Regenerate the raster brand icons from the committed SVG sources, via `rsvg-convert`
 * (same tool the og-default.svg note uses; install with `brew install librsvg`).
 *
 *   node scripts/gen-icons.mjs        (or: npm run gen:icons)
 *
 * Emits, into public/:
 *   - og-default.png        1200x630, rasterized from public/og-default.svg
 *   - apple-touch-icon.png  180x180, full-bleed indigo square + the full Watermark mark
 *   - favicon-32.png        32x32, the mark with the record rule dropped (the lockup's shed)
 *   - favicon-16.png        16x16, the mark collapsed to a single bracketed line
 *
 * favicon.svg (the full mark in a rounded square) is the canonical SVG favicon and is
 * served as-is to modern browsers; these PNGs are the legacy/iOS fallbacks. The shed
 * geometry (drop the rule at 32, single line at 16) is from the "Watermark · Brand
 * Lockups" app-icon/favicon panel — the brackets never disappear.
 */
import { execFileSync } from "node:child_process";
import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const publicDir = join(dirname(fileURLToPath(import.meta.url)), "..", "public");

const INDIGO = "#3f51b5";
const WHITE = "#ffffff";

/** Full-bleed square (no rounded corners; iOS applies its own mask) + the full mark. */
const appleTouchSvg = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
  <rect width="64" height="64" fill="${INDIGO}"/>
  <g fill="none" stroke="${WHITE}" stroke-width="3.8">
    <path d="M23 13 H13 V51 H23" stroke-linecap="square"/>
    <path d="M41 13 H51 V51 H41" stroke-linecap="square"/>
    <path d="M21 29 q5.5 -6 11 0 t11 0" stroke-linecap="round"/>
    <line x1="21" y1="42" x2="43" y2="42" stroke-linecap="round"/>
  </g>
</svg>`;

/** 32px shed: the record rule is dropped, leaving the brackets + waterline. */
const favicon32Svg = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
  <rect width="64" height="64" rx="14" fill="${INDIGO}"/>
  <g fill="none" stroke="${WHITE}" stroke-width="4.4">
    <path d="M23 14 H14 V50 H23" stroke-linecap="square"/>
    <path d="M41 14 H50 V50 H41" stroke-linecap="square"/>
    <path d="M22 31 q5 -5.5 10 0 t10 0" stroke-linecap="round"/>
  </g>
</svg>`;

/** 16px shed: collapses to a single bracketed line. */
const favicon16Svg = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
  <rect width="64" height="64" rx="14" fill="${INDIGO}"/>
  <g fill="none" stroke="${WHITE}" stroke-width="6">
    <path d="M22 15 H14 V49 H22" stroke-linecap="square"/>
    <path d="M42 15 H50 V49 H42" stroke-linecap="square"/>
    <line x1="23" y1="32" x2="41" y2="32" stroke-linecap="round"/>
  </g>
</svg>`;

/** Rasterize SVG markup (or a file) to a PNG of the given square/size via rsvg-convert. */
function render(svg, width, height, name) {
  const out = join(publicDir, name);
  execFileSync("rsvg-convert", ["-w", String(width), "-h", String(height), "-o", out], {
    input: svg,
  });
  console.log(`  ${name}  (${width}x${height})`);
}

render(readFileSync(join(publicDir, "og-default.svg")), 1200, 630, "og-default.png");
render(appleTouchSvg, 180, 180, "apple-touch-icon.png");
render(favicon32Svg, 32, 32, "favicon-32.png");
render(favicon16Svg, 16, 16, "favicon-16.png");
