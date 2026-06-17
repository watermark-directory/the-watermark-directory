import { mkdtempSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { afterAll, afterEach, describe, expect, it, vi } from "vitest";
import type { TeardownRecord } from "./teardown";

// teardownResolve builds its records/concepts maps at module scope from the
// bundle, so each case points BOSC_BUNDLE_DIR at a fresh fixture and re-imports
// with a clean registry (same harness as bundle.test.ts).
const tmpDirs: string[] = [];

function makeBundle(records: object[], concepts: object[] = []): string {
  const dir = mkdtempSync(join(tmpdir(), "bosc-td-"));
  tmpDirs.push(dir);
  const feeds = [
    {
      name: "records",
      path: "records.json",
      media_type: "application/json",
      schema: "s",
      kind: "collection",
      count: records.length,
    },
    {
      name: "concepts",
      path: "concepts.json",
      media_type: "application/json",
      schema: "s",
      kind: "collection",
      count: concepts.length,
    },
  ];
  writeFileSync(
    join(dir, "manifest.json"),
    JSON.stringify({
      bundle_version: "test",
      contract_version: "1.4",
      generated_at: "2026-01-01T00:00:00Z",
      feed_count: feeds.length,
      row_total: 0,
      feeds,
    }),
  );
  writeFileSync(join(dir, "records.json"), JSON.stringify(records));
  writeFileSync(join(dir, "concepts.json"), JSON.stringify(concepts));
  return dir;
}

async function loadResolver(dir: string): Promise<typeof import("./teardownResolve")> {
  process.env.BOSC_BUNDLE_DIR = dir;
  vi.resetModules();
  return import("./teardownResolve");
}

afterEach(() => {
  delete process.env.BOSC_BUNDLE_DIR;
});
afterAll(() => {
  for (const d of tmpDirs) rmSync(d, { recursive: true, force: true });
});

const OPC_RECORD = {
  rel: "aedg/opc.yaml",
  group: "opc",
  title: "OPC",
  warnings: [],
  fields: {
    meta: { summary_construction_total: 14223081, contingency_and_inflation_pct: 25 },
    nox_tpy: 235.62,
    instrument_type: "Limited Warranty Deed",
    consideration: null,
    empty: null,
  },
  approximate_paths: [],
  citation: { source: "aedg/opc.yaml", source_kind: "document", verified: true },
};

function teardown(overrides: Partial<TeardownRecord>): TeardownRecord {
  return {
    title: "t",
    docName: "d",
    source: { file: "f", pages: "p", collection: "c", kind: "k", note: "n" },
    extraction: [],
    reveal: { lead: "", key: "", tail: "" },
    check: { tag: "verified", sub: "", verify: "v", method: "m" },
    connect: [],
    ...overrides,
  };
}

describe("resolveTeardown — figure binding", () => {
  it("binds load-bearing rows to the feed value, formatted by unit", async () => {
    const { resolveTeardown } = await loadResolver(makeBundle([OPC_RECORD]));
    const { teardown: r } = resolveTeardown(
      teardown({
        recordRel: "aedg/opc.yaml",
        extraction: [
          { label: "Total", value: "$0", path: "meta.summary_construction_total", unit: "usd" },
          { label: "Contingency", value: "0%", path: "meta.contingency_and_inflation_pct", unit: "pct" },
          { label: "NOx", value: "0 tpy", path: "nox_tpy", unit: "tpy" },
          { label: "Instrument", value: "wrong", path: "instrument_type" },
        ],
      }),
    );
    expect(r.extraction[0]).toMatchObject({ value: "$14,223,081", live: true });
    expect(r.extraction[1]).toMatchObject({ value: "25%", live: true });
    expect(r.extraction[2]).toMatchObject({ value: "235.62 tpy", live: true });
    expect(r.extraction[3]).toMatchObject({ value: "Limited Warranty Deed", live: true });
  });

  it("flags a null feed value as a blank and warns", async () => {
    const { resolveTeardown } = await loadResolver(makeBundle([OPC_RECORD]));
    const { teardown: r } = resolveTeardown(
      teardown({
        recordRel: "aedg/opc.yaml",
        extraction: [{ label: "Consideration", value: "~ none", path: "consideration" }],
      }),
    );
    expect(r.extraction[0]).toMatchObject({ value: "—", warn: true, live: true });
  });

  it("keeps the curated value when the path is absent or the record isn't bound", async () => {
    const { resolveTeardown } = await loadResolver(makeBundle([OPC_RECORD]));
    const bound = resolveTeardown(
      teardown({
        recordRel: "aedg/opc.yaml",
        extraction: [
          { label: "Missing", value: "fallback", path: "does.not.exist" },
          { label: "Framing", value: "editorial" },
        ],
      }),
    ).teardown;
    expect(bound.extraction[0]).toMatchObject({ value: "fallback" });
    expect(bound.extraction[0].live).toBeUndefined();
    expect(bound.extraction[1]).toMatchObject({ value: "editorial" });
  });

  it("falls back entirely to curated rows when the record is not in the bundle", async () => {
    const { resolveTeardown } = await loadResolver(makeBundle([]));
    const res = resolveTeardown(
      teardown({
        recordRel: "aedg/opc.yaml",
        extraction: [
          { label: "Total", value: "$14,223,081", path: "meta.summary_construction_total", unit: "usd" },
        ],
      }),
    );
    expect(res.verifyResolved).toBe(false);
    expect(res.sourceFields).toEqual([]);
    expect(res.teardown.extraction[0]).toMatchObject({ value: "$14,223,081" });
    expect(res.teardown.extraction[0].live).toBeUndefined();
  });
});

describe("resolveTeardown — source viewer + links", () => {
  it("surfaces the record's substantive fields (dropping empty scalars) and deep-links verify", async () => {
    const { resolveTeardown } = await loadResolver(makeBundle([OPC_RECORD]));
    const res = resolveTeardown(teardown({ recordRel: "aedg/opc.yaml" }));
    expect(res.verifyResolved).toBe(true);
    expect(res.liveCitation?.verified).toBe(true);
    expect(res.teardown.check.verifyHref).toContain("/site/records/opc/");
    // instrument_type is present; the null `empty`/`consideration` scalars are dropped.
    const labels = res.sourceFields.map((f) => f.label);
    expect(labels).toContain("instrument_type");
    expect(labels).not.toContain("empty");
    expect(res.sourceFields.every((f) => f.value !== "—")).toBe(true);
  });

  it("deep-links concept connect chips present in the bundle", async () => {
    const { resolveTeardown } = await loadResolver(makeBundle([], [{ slug: "7q10" }]));
    const res = resolveTeardown(
      teardown({
        connect: [
          { kind: "concept", label: "[[7q10]]" },
          { kind: "entity", label: "x" },
        ],
      }),
    );
    expect(res.teardown.connect[0].href).toContain("/wiki/concepts/7q10");
    expect(res.teardown.connect[1].href).toBeUndefined();
  });
});
