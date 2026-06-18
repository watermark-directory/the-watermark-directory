import { describe, expect, it } from "vitest";
import {
  buildBullet,
  buildDonut,
  buildHBars,
  buildLine,
  buildSparkline,
  buildStacked,
  buildVBars,
  EVIDENCE_FILL,
  INDIGO,
  niceMax,
  WITHHELD_FILL,
} from "./charts";

describe("charts geometry (#306)", () => {
  it("niceMax returns a nice ceiling at or above the value", () => {
    expect(niceMax(31)).toBeGreaterThanOrEqual(31);
    expect(niceMax(8)).toBeGreaterThanOrEqual(8);
    expect(niceMax(0)).toBe(1);
    expect([10, 20, 25, 50, 100]).toContain(niceMax(31));
  });

  it("vertical bars: one bar per datum, peak highlighted in indigo, within the plot", () => {
    const c = buildVBars([
      { label: "a", value: 6 },
      { label: "b", value: 31 },
      { label: "c", value: 13 },
    ]);
    expect(c.bars).toHaveLength(3);
    const peak = c.bars.filter((b) => b.peak);
    expect(peak).toHaveLength(1);
    expect(peak[0].value).toBe(31);
    expect(peak[0].fill).toBe(INDIGO);
    for (const b of c.bars) expect(b.y + b.h).toBeCloseTo(c.baselineY, 1); // bars sit on the baseline
    expect(c.grid).toHaveLength(5);
  });

  it("horizontal bars: withheld bars get the soft fill + value labels carry the unit", () => {
    const c = buildHBars(
      [
        { label: "P2", value: 92 },
        { label: "P1", value: 5, withheld: true },
      ],
      { unit: "ac" },
    );
    expect(c.bars).toHaveLength(2);
    expect(c.bars[1].fill).toBe(WITHHELD_FILL);
    expect(c.bars[0].fill).toBe(INDIGO);
    expect(c.bars[0].valLabel).toBe("92 ac");
  });

  it("line: a single polyline, a closed area, dots per point, last anchored", () => {
    const c = buildLine([
      { label: "a", value: 5 },
      { label: "b", value: 60 },
      { label: "c", value: 340 },
    ]);
    expect(c.line.startsWith("M")).toBe(true);
    expect(c.area.endsWith("Z")).toBe(true);
    expect(c.dots).toHaveLength(3);
    expect(c.last).toEqual({ x: c.dots[2].x, y: c.dots[2].y });
  });

  it("bullet: ratio is measure÷limit, percentages on the shared scale", () => {
    const c = buildBullet(4.85, 0.2);
    expect(c.ratio).toBe(24.25);
    expect(c.measurePct).toBeGreaterThan(c.limitPct);
    expect(c.measurePct).toBeLessThanOrEqual(100);
  });

  it("stacked: evidence-colored segments whose widths fill the bar and sum to 100%", () => {
    const c = buildStacked([
      { label: "verified", value: 196, kind: "verified" },
      { label: "inference", value: 78, kind: "inference" },
      { label: "open", value: 44, kind: "open" },
    ]);
    expect(c.total).toBe(318);
    expect(c.segments[0].fill).toBe(EVIDENCE_FILL.verified);
    expect(c.segments[2].fill).toBe(EVIDENCE_FILL.open);
    const sumW = c.segments.reduce((s, g) => s + g.w, 0);
    expect(sumW).toBeCloseTo(354, 0); // the bar inner width
    expect(c.segments.reduce((s, g) => s + g.pct, 0)).toBeCloseTo(100, 0);
  });

  it("donut: one arc per slice, indigo tints, total summed", () => {
    const c = buildDonut([
      { label: "a", value: 96 },
      { label: "b", value: 78 },
      { label: "c", value: 34 },
    ]);
    expect(c.segments).toHaveLength(3);
    expect(c.total).toBe(208);
    for (const s of c.segments) expect(s.d.startsWith("M")).toBe(true);
  });

  it("sparkline: a polyline ending at the last point's dot", () => {
    const c = buildSparkline([2, 3, 5, 4, 9, 14]);
    expect(c.path.startsWith("M")).toBe(true);
    expect(c.dot.x).toBeGreaterThan(0);
  });
});
