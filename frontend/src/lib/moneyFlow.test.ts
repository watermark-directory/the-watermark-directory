import { mkdtempSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { afterAll, afterEach, describe, expect, it, vi } from "vitest";
import { fmtUsd, fmtUsdFull } from "./money";

const tmpDirs: string[] = [];

function makeBundle(records: object[]): string {
  const dir = mkdtempSync(join(tmpdir(), "bosc-mf-"));
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
  return dir;
}

async function loadMoneyFlow(dir: string): Promise<typeof import("./moneyFlow")> {
  process.env.BOSC_BUNDLE_DIR = dir;
  vi.resetModules();
  return import("./moneyFlow");
}

const OPC_RECORD = {
  rel: "aedg/roundabouts.summary.opc.yaml",
  group: "opc",
  title: "OPC",
  warnings: [],
  fields: {
    meta: { summary_construction_total: 14223081 },
    sub_estimates: [
      { name: "Cole Street Corridor", total: 3899800 },
      { name: "Bluelick Road Corridor", total: 2180907 },
    ],
  },
  approximate_paths: [],
  citation: { source: "x", source_kind: "document", verified: true },
};

afterEach(() => {
  delete process.env.BOSC_BUNDLE_DIR;
});
afterAll(() => {
  for (const d of tmpDirs) rmSync(d, { recursive: true, force: true });
});

describe("USD formatters", () => {
  it("compact form keeps significant decimals and whole-million integers", () => {
    expect(fmtUsd(14_500_000)).toBe("$14.5M");
    expect(fmtUsd(3_520_000)).toBe("$3.52M");
    expect(fmtUsd(14_223_081)).toBe("$14.22M");
    // The trailing-zero strip must NOT eat integer zeros (regression guard).
    expect(fmtUsd(500_000_000)).toBe("$500M");
    expect(fmtUsd(14_000_000)).toBe("$14M");
  });

  it("full form groups thousands", () => {
    expect(fmtUsdFull(14223081)).toBe("$14,223,081");
    expect(fmtUsdFull(1535218)).toBe("$1,535,218");
  });
});

describe("buildMoneyFlow", () => {
  it("reads the OPC line items + total from the records feed (no fork)", async () => {
    const { buildMoneyFlow } = await loadMoneyFlow(makeBundle([OPC_RECORD]));
    const m = buildMoneyFlow();
    expect(m.opcFromFeed).toBe(true);
    expect(m.opcTotalUsd).toBe(14223081);
    expect(m.opcItems).toHaveLength(2);
    expect(m.opcItems[0]).toEqual({ name: "Cole Street Corridor", usd: 3899800 });
    expect(m.collectedUsd).toBe(14_500_000);
    expect(m.firstAward.usd).toBe(3_520_000);
  });

  it("never fabricates the abatement-per-job — the school terms stay withheld", async () => {
    const { buildMoneyFlow } = await loadMoneyFlow(makeBundle([OPC_RECORD]));
    const m = buildMoneyFlow();
    expect(m.abatement.schoolTermsPublic).toBe(false);
    // No per-job dollar is asserted anywhere on the model.
    expect(m.abatement).not.toHaveProperty("perJobUsd");
  });

  it("falls back to the curated OPC items when the feed is absent (CI fixture)", async () => {
    const { buildMoneyFlow } = await loadMoneyFlow(makeBundle([]));
    const m = buildMoneyFlow();
    expect(m.opcFromFeed).toBe(false);
    expect(m.opcItems).toHaveLength(6);
    expect(m.opcTotalUsd).toBeGreaterThan(0);
  });
});
