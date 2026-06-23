/**
 * Chart geometry for the record-grammar chart set (#306). Pure + SSR: the components
 * (`components/charts/*.astro`) are thin SVG templates over these builders, so the
 * geometry is unit-tested and there is **no client JS**. Ported from the Claude Design
 * "Chart Set".
 *
 * Grammar (enforced here):
 *  - **Forest is data** — one hue, four tints (`FOREST_TINTS`) for series/slices.
 *  - The **evidence palette** (`EVIDENCE_FILL`) is spent only on *encoding evidence*
 *    (the stacked status bar), never on decoration.
 *  - Figures are monospace (the components set the mono face); the grid is light
 *    (`GRID`, `BASELINE`) with no chrome.
 */
import type { TagKind } from "./teardown";

const round = (n: number, p = 1): number => {
  const f = 10 ** p;
  return Math.round(n * f) / f;
};

/** Forest is data (Swiss 03 chart set): one hue, four tints for series and slices. */
export const FOREST_TINTS = ["#1f6f4a", "#3f8a63", "#5fa07f", "#8fbca0", "#bcd2c4"] as const;
export const FOREST = "#1f6f4a";
export const INK = "#16201a";
export const GRID = "#ece8dc";
export const BASELINE = "#cdc8b8";
export const LIMIT = "#7a2230";
/** The withheld/soft tint for a ranked bar whose value is present but its price isn't. */
export const WITHHELD_FILL = "rgba(31,111,74,0.22)";
export const WITHHELD_STROKE = "#bcd2c4";

/** Evidence encoding — the ONE place the semantic palette enters a chart. */
export const EVIDENCE_FILL: Record<TagKind, string> = {
  verified: "#1f6f4a",
  inference: "#9a6a14",
  open: "#a8a596",
};

/** A "nice" axis ceiling at or above `v` (1/2/2.5/5 × 10ⁿ). */
export function niceMax(v: number): number {
  if (v <= 0) return 1;
  const mag = 10 ** Math.floor(Math.log10(v));
  const norm = v / mag;
  const step = norm <= 1 ? 1 : norm <= 2 ? 2 : norm <= 2.5 ? 2.5 : norm <= 5 ? 5 : 10;
  return round(step * mag, 4);
}

function ticks(max: number, n = 4): number[] {
  return Array.from({ length: n + 1 }, (_, i) => round((max / n) * i, 4));
}

// ---------------------------------------------------------------- 1 · vertical bars
export interface BarDatum {
  label: string;
  value: number;
}
export interface VBar extends BarDatum {
  x: number;
  y: number;
  w: number;
  h: number;
  cx: number;
  valY: number;
  peak: boolean;
  fill: string;
}
export interface AxisGridLine {
  value: number;
  y: number;
}
export interface VBarChart {
  width: number;
  height: number;
  baselineY: number;
  bars: VBar[];
  grid: AxisGridLine[];
}

export function buildVBars(data: BarDatum[], opts: { max?: number; barW?: number } = {}): VBarChart {
  const W = 360;
  const H = 200;
  const L = 34;
  const R = 12;
  const T = 14;
  const base = 172;
  const barW = opts.barW ?? 22;
  const max = opts.max ?? niceMax(Math.max(1, ...data.map((d) => d.value)));
  const plotH = base - T;
  const plotW = W - L - R;
  const slot = data.length > 0 ? plotW / data.length : plotW;
  const peakVal = Math.max(...data.map((d) => d.value), Number.NEGATIVE_INFINITY);
  const bars: VBar[] = data.map((d, i) => {
    const h = (d.value / max) * plotH;
    const x = L + slot * i + (slot - barW) / 2;
    const peak = d.value === peakVal;
    return {
      ...d,
      x: round(x),
      y: round(base - h),
      w: barW,
      h: round(h),
      cx: round(x + barW / 2),
      valY: round(base - h - 5),
      peak,
      fill: peak ? FOREST : FOREST_TINTS[2],
    };
  });
  const grid = ticks(max).map((value) => ({ value, y: round(base - (value / max) * plotH) }));
  return { width: W, height: H, baselineY: base, bars, grid };
}

// -------------------------------------------------------------- 2 · horizontal bars
export interface RankedBarDatum extends BarDatum {
  /** The value is known but a companion figure (e.g. a price) is withheld → soft fill. */
  withheld?: boolean;
}
export interface HBar extends RankedBarDatum {
  y: number;
  textY: number;
  w: number;
  valX: number;
  valLabel: string;
  fill: string;
  stroke: string;
  strokeW: number;
}
export interface HBarChart {
  width: number;
  height: number;
  x0: number;
  unit: string;
  bars: HBar[];
  ticks: { value: number; x: number }[];
}

export function buildHBars(data: RankedBarDatum[], opts: { max?: number; unit?: string } = {}): HBarChart {
  const W = 360;
  const H = 200;
  const x0 = 70;
  const barAreaW = 278;
  const top = 10;
  const base = 178;
  const max = opts.max ?? niceMax(Math.max(1, ...data.map((d) => d.value)));
  const barH = 14;
  const slot = data.length > 0 ? (base - top) / data.length : base - top;
  const unit = opts.unit ?? "";
  const bars: HBar[] = data.map((d, i) => {
    const w = (d.value / max) * barAreaW;
    const y = top + slot * i + (slot - barH) / 2;
    return {
      ...d,
      y: round(y),
      textY: round(y + barH / 2 + 3.5),
      w: round(w),
      valX: round(x0 + w + 6),
      valLabel: unit ? `${round(d.value)} ${unit}` : `${round(d.value)}`,
      fill: d.withheld ? WITHHELD_FILL : FOREST,
      stroke: d.withheld ? WITHHELD_STROKE : "none",
      strokeW: d.withheld ? 1 : 0,
    };
  });
  const t = [0, max / 2, max].map((value) => ({
    value: round(value, 4),
    x: round(x0 + (value / max) * barAreaW),
  }));
  return { width: W, height: H, x0, unit, bars, ticks: t };
}

// --------------------------------------------------------------------- 3 · line/area
export interface LinePoint {
  label: string;
  value: number;
}
/** A horizontal reference line — the convention the comp's water stories are built on:
 *  a draw/limit/level threshold drawn dashed with a right-aligned colored label
 *  (oxblood `LIMIT` for a cap, amber `#9a6a14` for a modeled draw, `FOREST` for a
 *  static level). The seam is reusable; the hydrology figures that consume it (FDC,
 *  hydrograph, cumulative-vs-cap, drawdown) await time-series data the bundle doesn't
 *  carry yet. */
export interface RefLineInput {
  value: number;
  label: string;
  color: string;
  /** Dash pattern; defaults to "5 3" (the comp's limit/cap dash). */
  dash?: string;
}
export interface RefLine extends RefLineInput {
  dash: string;
  /** Plotted y (clamped to the chart's [0, max] band). */
  y: number;
}
export interface LineChart {
  width: number;
  height: number;
  baselineY: number;
  line: string;
  area: string;
  dots: { x: number; y: number; label: string }[];
  last: { x: number; y: number };
  grid: AxisGridLine[];
  /** Plot x-extent for overlays (reference lines span L → right edge). */
  plot: { left: number; right: number };
  refLines: RefLine[];
}

export function buildLine(
  points: LinePoint[],
  opts: { max?: number; refs?: RefLineInput[] } = {},
): LineChart {
  const W = 360;
  const H = 200;
  const L = 34;
  const R = 14;
  const T = 16;
  const base = 174;
  const max = opts.max ?? niceMax(Math.max(1, ...points.map((p) => p.value)));
  const plotH = base - T;
  const plotW = W - L - R;
  const step = points.length > 1 ? plotW / (points.length - 1) : 0;
  const pts = points.map((p, i) => ({
    label: p.label,
    x: round(L + step * i),
    y: round(base - (p.value / max) * plotH),
  }));
  const line = `M${pts.map((p) => `${p.x} ${p.y}`).join(" L")}`;
  const lastPt = pts[pts.length - 1];
  const last = lastPt ? { x: lastPt.x, y: lastPt.y } : { x: L, y: base };
  const area = `${line} L${last.x} ${base} L${pts[0]?.x ?? L} ${base} Z`;
  const grid = ticks(max).map((value) => ({ value, y: round(base - (value / max) * plotH) }));
  const refLines: RefLine[] = (opts.refs ?? []).map((r) => ({
    ...r,
    dash: r.dash ?? "5 3",
    y: round(base - (Math.max(0, Math.min(r.value, max)) / max) * plotH),
  }));
  return {
    width: W,
    height: H,
    baselineY: base,
    line,
    area,
    dots: pts,
    last,
    grid,
    plot: { left: L, right: W - R },
    refLines,
  };
}

// ----------------------------------------------------------------------- 4 · bullet
export interface BulletChart {
  measurePct: number;
  limitPct: number;
  ratio: number;
}

/** A measure against a limit on a shared scale (e.g. cooling draw vs the 7Q10 low flow). */
export function buildBullet(measure: number, limit: number, max?: number): BulletChart {
  const m = max ?? niceMax(Math.max(measure, limit));
  return {
    measurePct: round((measure / m) * 100, 2),
    limitPct: round((limit / m) * 100, 2),
    ratio: limit > 0 ? round(measure / limit, 2) : Number.POSITIVE_INFINITY,
  };
}

// ---------------------------------------------------------------- 5 · stacked status
export interface StackSegment {
  label: string;
  value: number;
  kind: TagKind;
}
export interface StackedBar {
  width: number;
  height: number;
  total: number;
  segments: {
    label: string;
    value: number;
    kind: TagKind;
    x: number;
    w: number;
    fill: string;
    pct: number;
  }[];
}

export function buildStacked(segments: StackSegment[]): StackedBar {
  const W = 360;
  const H = 30;
  const x0 = 3;
  const barW = 354;
  const total = segments.reduce((s, d) => s + d.value, 0) || 1;
  let acc = x0;
  const segs = segments.map((d) => {
    const w = (d.value / total) * barW;
    const seg = {
      label: d.label,
      value: d.value,
      kind: d.kind,
      x: round(acc),
      w: round(w),
      fill: EVIDENCE_FILL[d.kind],
      pct: round((d.value / total) * 100),
    };
    acc += w;
    return seg;
  });
  return { width: W, height: H, total, segments: segs };
}

// ------------------------------------------------------------------- 6 · donut
export interface DonutSlice {
  label: string;
  value: number;
}
export interface DonutChart {
  total: number;
  segments: { label: string; value: number; d: string; fill: string; pct: number }[];
}

export function buildDonut(slices: DonutSlice[], opts: { ro?: number; ri?: number } = {}): DonutChart {
  const cx = 100;
  const cy = 100;
  const ro = opts.ro ?? 80;
  const ri = opts.ri ?? 50;
  const total = slices.reduce((s, d) => s + d.value, 0) || 1;
  const pol = (rad: number, a: number): [number, number] => [
    round(cx + rad * Math.cos(a), 2),
    round(cy + rad * Math.sin(a), 2),
  ];
  let a = -Math.PI / 2;
  const segments = slices.map((d, i) => {
    const a0 = a;
    const a1 = a + (d.value / total) * Math.PI * 2;
    a = a1;
    const large = a1 - a0 > Math.PI ? 1 : 0;
    const [x0, y0] = pol(ro, a0);
    const [x1, y1] = pol(ro, a1);
    const [x2, y2] = pol(ri, a1);
    const [x3, y3] = pol(ri, a0);
    return {
      label: d.label,
      value: d.value,
      d: `M${x0} ${y0} A${ro} ${ro} 0 ${large} 1 ${x1} ${y1} L${x2} ${y2} A${ri} ${ri} 0 ${large} 0 ${x3} ${y3} Z`,
      fill: FOREST_TINTS[i % FOREST_TINTS.length],
      pct: round((d.value / total) * 100),
    };
  });
  return { total, segments };
}

// --------------------------------------------------------------------- 7 · sparkline
export interface Sparkline {
  width: number;
  height: number;
  path: string;
  dot: { x: number; y: number };
}

export function buildSparkline(values: number[]): Sparkline {
  const W = 120;
  const H = 32;
  const x0 = 3;
  const w = 114;
  const y0 = 5;
  const h = 22;
  const max = Math.max(...values);
  const min = Math.min(...values);
  const span = max - min || 1;
  const step = values.length > 1 ? w / (values.length - 1) : 0;
  const pts = values.map((v, i) => ({ x: round(x0 + step * i), y: round(y0 + (1 - (v - min) / span) * h) }));
  return {
    width: W,
    height: H,
    path: `M${pts.map((p) => `${p.x} ${p.y}`).join(" L")}`,
    dot: pts[pts.length - 1] ?? { x: x0, y: y0 },
  };
}
