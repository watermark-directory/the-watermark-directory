/**
 * Regenerate the raster brand icons from the committed SVG sources, via `rsvg-convert`
 * (same tool the og-default.svg note uses; install with `brew install librsvg`).
 *
 *   node scripts/gen-icons.mjs        (or: npm run gen:icons)
 *
 * Emits, into public/:
 *   - og-default.png        1200x630, rasterized from public/og-default.svg
 *   - apple-touch-icon.png  180x180, the "w." mark on the ink tile
 *   - favicon-32.png        32x32, the "w." mark
 *   - favicon-16.png        16x16, the "w." mark
 *
 * The brand is the wordmark "Watermark." — there is no glyph (design "Watermark ·
 * Brand Final": *no logo, just the word*). The only load-bearing mark is the favicon:
 * a lowercase "w" with the green period, knocked out of ink — it reads as type, not
 * an icon. favicon.svg is the canonical SVG favicon (matches brand/favicon.svg in the
 * design project); these PNGs are the legacy/iOS fallbacks (Arial when Archivo is
 * absent on the rasterizer, per the SVG's font fallback).
 */
import { execFileSync } from "node:child_process";
import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const publicDir = join(dirname(fileURLToPath(import.meta.url)), "..", "public");

// Watermark — ink tile, bone "w", one green signal period (Brand Final).
const INK = "#16201A";
const BONE = "#F5F2EA";
const SIGNAL = "#3D8F63";

/** The "w." mark, knocked out of an ink tile (iOS masks its own corners). */
const wMark = (extra = "") =>
  `<svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 64 64">
  <rect width="64" height="64" fill="${INK}"${extra}/>
  <text x="32" y="47" text-anchor="middle" font-family="Archivo, Arial, sans-serif" font-weight="800" font-size="44" letter-spacing="-3"><tspan fill="${BONE}">w</tspan><tspan fill="${SIGNAL}">.</tspan></text>
</svg>`;

const appleTouchSvg = wMark();
const favicon32Svg = wMark();
const favicon16Svg = wMark();

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
