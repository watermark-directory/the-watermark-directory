import { describe, expect, it } from "vitest";
import {
  bounds,
  central,
  disclose,
  type Model,
  mulberry32,
  outcomeBand,
  type Prior,
  quantile,
  sample,
  summarize,
  tornado,
} from "./uncertainty";

const PRIORS: Prior[] = [
  {
    key: "share",
    label: "Building share",
    register: "assumption",
    dist: { kind: "triangular", low: 0.2, central: 0.3, high: 0.45 },
  },
  { key: "jobs", label: "Jobs", register: "assumption", dist: { kind: "uniform", low: 30, high: 50 } },
  { key: "rate", label: "Rate", register: "verified", dist: { kind: "fixed", value: 0.02 } },
];
// give = share * 1000 / jobs * rate-ish — monotone ↑ in share, ↓ in jobs.
const give: Model = (d) => (d.share * 1000 * d.rate) / d.jobs;

describe("distribution helpers", () => {
  it("central + bounds per kind", () => {
    expect(central({ kind: "fixed", value: 5 })).toBe(5);
    expect(central({ kind: "triangular", low: 0, central: 3, high: 10 })).toBe(3);
    expect(central({ kind: "uniform", low: 10, high: 20 })).toBe(15);
    expect(bounds({ kind: "triangular", low: 0, central: 3, high: 10 })).toEqual([0, 10]);
    expect(bounds({ kind: "fixed", value: 5 })).toEqual([5, 5]);
  });

  it("quantile hits the bounds at u=0 and u→1", () => {
    const tri = { kind: "triangular", low: 0, central: 3, high: 10 } as const;
    expect(quantile(tri, 0)).toBeCloseTo(0);
    expect(quantile(tri, 0.999999)).toBeCloseTo(10, 1);
    expect(quantile({ kind: "uniform", low: 10, high: 20 }, 0.5)).toBeCloseTo(15);
    expect(quantile({ kind: "fixed", value: 7 }, 0.42)).toBe(7);
  });
});

describe("mulberry32", () => {
  it("is deterministic for a seed and varies across seeds", () => {
    const a = mulberry32(123);
    const b = mulberry32(123);
    expect([a(), a(), a()]).toEqual([b(), b(), b()]);
    expect(mulberry32(1)()).not.toBe(mulberry32(2)());
    const v = mulberry32(999)();
    expect(v).toBeGreaterThanOrEqual(0);
    expect(v).toBeLessThan(1);
  });
});

describe("sample + summarize", () => {
  it("same seed ⇒ identical outcomes and identical percentiles", () => {
    const a = sample(PRIORS, give, 2000, 42);
    const b = sample(PRIORS, give, 2000, 42);
    expect(a).toEqual(b);
    expect(summarize(a)).toEqual(summarize(b));
  });

  it("a different seed gives a different run", () => {
    expect(sample(PRIORS, give, 2000, 1)).not.toEqual(sample(PRIORS, give, 2000, 2));
  });

  it("percentiles are ordered and the histogram counts every sample", () => {
    const s = summarize(sample(PRIORS, give, 4000, 7));
    expect(s.min).toBeLessThanOrEqual(s.p10);
    expect(s.p10).toBeLessThanOrEqual(s.p50);
    expect(s.p50).toBeLessThanOrEqual(s.p90);
    expect(s.p90).toBeLessThanOrEqual(s.max);
    expect(s.bins.reduce((a, b) => a + b.n, 0)).toBe(4000);
  });
});

describe("tornado", () => {
  it("ranks movable priors by swing and excludes fixed/[verified]", () => {
    const bars = tornado(PRIORS, give);
    expect(bars.map((b) => b.key)).not.toContain("rate"); // fixed excluded
    expect(bars[0].swing).toBeGreaterThanOrEqual(bars[1].swing); // sorted desc
    for (const b of bars) expect(b.high).toBeGreaterThanOrEqual(b.low);
  });
});

describe("disclose", () => {
  it("collapses a prior to a fixed value and tightens the band", () => {
    const wide = outcomeBand(PRIORS, give);
    const disclosed = disclose(PRIORS, "jobs", 50);
    const j = disclosed.find((p) => p.key === "jobs");
    expect(j?.register).toBe("verified");
    expect(j?.dist).toEqual({ kind: "fixed", value: 50 });
    const tight = outcomeBand(disclosed, give);
    expect(tight.high - tight.low).toBeLessThan(wide.high - wide.low);
  });
});

describe("outcomeBand", () => {
  it("brackets the central value over the prior grid", () => {
    const band = outcomeBand(PRIORS, give);
    expect(band.low).toBeLessThanOrEqual(band.central);
    expect(band.central).toBeLessThanOrEqual(band.high);
    // monotone model: low corner = min share / max jobs; high = max share / min jobs.
    expect(band.low).toBeCloseTo((0.2 * 1000 * 0.02) / 50);
    expect(band.high).toBeCloseTo((0.45 * 1000 * 0.02) / 30);
  });
});
